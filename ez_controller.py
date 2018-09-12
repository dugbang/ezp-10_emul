import json
import os
import pickle
import queue
import time
from datetime import datetime, date
from multiprocessing import Queue, Process
from bs4 import BeautifulSoup as bs

import requests

from io_control import io_control_process
from usb_capture import usb_capture_process


class Communication:
    FILE_STATE_PICKLE = 'controller_state.pickle'
    FILE_OUTPUT_TIMES = 'output_times.csv'  # 다른 프로세스에서 클래스의 정보교환이 가능한가?

    def __init__(self):
        self.state = None
        self.duration = 60
        self.is_new_state = False
        # self.is_new_output_times = False

        # self.__fields = ('serial', 'is_active', 'plant',
        #                  'minute_of_action_cycle', 'minute_of_upload_cycle',
        #                  'iis_tank_capacity', 'iis_temperature', 'iis_ph', 'iis_mc',
        #                  'iis_temp_humidity_high', 'iis_temp_humidity_low', 'iis_luminance', 'iis_co2',
        #                  'ois_led', 'ois_pump', 'ois_pan_high', 'ois_pan_low',
        #                  'is_usb_camera', 'modify_date', 'actuator_csv',
        #                  'capture_times', 'stable_time_of_camera')
        self.__capture_records = []
        self.__io_records = []

        # TODO; 실제 url 은 나중에 갱신.
        self.__url_state = 'http://127.0.0.1:8000/ezp10/api/controller/0001234/'
        self.__url_capture = 'http://127.0.0.1:8000/ezp10/capture/upload/'
        self.__url_io_report = 'http://127.0.0.1:8000/ezp10/api/report/'

    def add_io_records(self, records):
        self.__io_records.append(records)

    def add_capture_records(self, records):
        self.__capture_records.append(records)
        self.__delete_uploaded_file()

    def __delete_uploaded_file(self):
        for filename in [r[1] for r in self.__capture_records if r[2]]:
            os.remove(filename)
        self.__capture_records = [r for r in self.__capture_records if not r[2]]

    def upload_data(self):
        # print('upload_data...')
        if self.__access_state is None:
            return
        self.__upload_capture_file()
        self.__upload_io_data()

    def is_active(self):
        return self.state['is_active']

    def set_state(self):
        self.is_new_state = False
        # self.is_new_output_times = False
        self.__read_file_state()
        self.__access_server_state()
        if self.__read_state is None and self.__access_state is None:
            # raise Exception('초기화 에러... 지속적인 대기 또는 종료')
            print('초기화 에러... 지속적인 대기 또는 종료')
            return
        elif self.__read_state is None and self.__access_state is not None:
            # self.__read_state = self.__access_state
            self.state = self.__access_state
            self.__save_state()
        elif self.__read_state is not None and self.__access_state is None:
            self.state = self.__read_state
        elif self.__read_state is not None and self.__access_state is not None:
            self.state = self.__access_state

            if self.__read_state['modify_date'] != self.__access_state['modify_date']:
                self.__save_state()
            if self.__read_state['actuator_csv'] != self.__access_state['actuator_csv']:
                self.__download_output_times()

        self.duration = 60 * self.state['minute_of_upload_cycle']

    def __upload_capture_file(self):
        print('__upload_capture_file..')
        data = {'plant': self.state['plant'], 'controller': self.state['serial']}
        files = {}
        for i, rec in enumerate(self.__capture_records):
            if rec[2] is False:
                data['create_at'] = rec[0]
                files['image'] = open(rec[1], 'rb')
                if self.__requests_post_file_data(self.__url_capture, files, data) is False:
                    break
                self.__capture_records[i][2] = True

    def __upload_io_data(self):
        fields = ('create_at', 'tank_capacity', 'temperature', 'ph', 'mc',
                  'temp_humidity_high', 'temp_humidity_low', 'luminance', 'co2',
                  'on_off_led', 'on_off_pump', 'on_off_pan_high', 'on_off_pan_low',
                  )
        data = {'plant': self.state['plant'], 'controller': self.state['serial']}
        upload_idx = []
        for i, rec in enumerate(self.__io_records):
            for j, field in enumerate(fields):
                data[field] = rec[j]

            if self.__requests_post_json_data(self.__url_io_report, data) is False:
                break
            upload_idx.append(i)

        upload_idx.sort(reverse=True)
        for i in upload_idx:
            del self.__io_records[i]

    @staticmethod
    def __requests_post_json_data(url, data):
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError("Type %s not serializable" % type(obj))

        headers = {'content-type': 'application/json'}
        res = requests.post(url, data=json.dumps(data, default=json_serial), headers=headers)
        if res.status_code == 201:
            return True
        print('post_json_data res.status_code; ', res.status_code)
        return False

    @staticmethod
    def __requests_post_file_data(url, files, data):
        with requests.Session() as s:
            first_page = s.get(url)
            soup = bs(first_page.text, 'html.parser')
            csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            post_data = {**data, **{'csrfmiddlewaretoken': csrf['value']}}

            res = s.post(url, files=files, data=post_data)
            if res.status_code == 200:
                return True
        print('post_file_data res.status_code; ', res.status_code)
        return False

    def __save_state(self):
        self.is_new_state = True
        with open(Communication.FILE_STATE_PICKLE, 'wb') as f:
            pickle.dump(self.state, f, pickle.HIGHEST_PROTOCOL)

    def __download_output_times(self):
        self.is_new_output_times = True
        response = requests.get(self.state['actuator_csv'])
        with open(Communication.FILE_OUTPUT_TIMES, 'wb') as f:
            f.write(response.content)

    def __read_file_state(self):
        self.__read_state = None
        if os.path.exists(Communication.FILE_STATE_PICKLE):
            with open(Communication.FILE_STATE_PICKLE, 'rb') as f:
                self.__read_state = pickle.load(f)

    def __access_server_state(self):
        self.__access_state = None
        response = requests.get(self.__url_state)
        if response.status_code == 200:
            self.__access_state = response.json()


class MainProcess:
    """
    메인프로세스로 main 에서 실행된다.
    """

    def __init__(self):
        self.__queue = Queue()
        self.__q_usb = Queue()
        self.__q_io = Queue()

        self.__process = (
            Process(target=usb_capture_process, args=(self.__q_usb, self.__queue)),
            Process(target=io_control_process, args=(self.__q_io, self.__queue)),
        )
        self.__capture_records = []
        self.__io_records = []

        self.__comm = Communication()

        # self.duration = 5 * 60

    def start(self):
        print('main process pid; {}'.format(os.getpid()))

        # TODO; 서버에서 상태정보를 읽어온다.
        self.__comm.set_state()
        while not self.__comm.is_active():
            print('Not Active > {}'.format(datetime.now().strftime('%H:%M:%S')))
            time.sleep(self.__comm.duration / 10)
            self.__comm.set_state()

        print('Active > {}'.format(datetime.now().strftime('%H:%M:%S')))
        for process in self.__process:
            process.start()

        # time.sleep(0.5)
        self.__q_io.put(('set_state', self.__comm.state))
        self.__q_usb.put(('set_state', self.__comm.state))
        self.__run()

        for process in self.__process:
            process.join()

    @staticmethod
    def __is_break():
        if os.path.exists('ez_break'):
            os.remove('ez_break')
            return True
        return False

    def __run(self):
        st_ = datetime.now()
        while True:
            try:
                msg = self.__queue.get(False)
            except queue.Empty:
                ct_ = datetime.now()
                time.sleep(1)
                self.__valid_break()
                if (ct_ - st_).total_seconds() < self.__comm.duration:
                    continue
                st_ = ct_
                self.__msg_empty_loop()
            else:
                if msg[0] == 'quit':
                    print('MainProcess... exit')
                    break
                elif msg[0] == 'capture':
                    print('MainProcess get; add_capture_records')
                    self.__comm.add_capture_records([msg[1], msg[2], False])
                elif msg[0] == 'io_records':
                    print('MainProcess get; add_io_records')
                    self.__comm.add_io_records(msg[1])

    def __msg_empty_loop(self):
        self.__comm.set_state()
        self.__comm.upload_data()
        if self.__comm.is_new_state:
            self.__q_io.put(('set_state', self.__comm.state))
            self.__q_usb.put(('set_state', self.__comm.state))
        # if self.__comm.is_new_output_times:
        #     self.__q_io.put(('output_times',))

    def __valid_break(self):
        if self.__is_break():
            self.__q_io.put(('quit',))
            self.__q_usb.put(('quit',))
            self.__queue.put(('quit',))

    def __del__(self):
        self.__queue.close()
        self.__q_usb.close()
        self.__q_io.close()


if __name__ == "__main__":
    st = datetime.now()

    controller = MainProcess()
    controller.start()

    et = datetime.now()
    process_time = int((et - st).total_seconds())
    if process_time < 100:
        print(__file__, 'Python Elapsed {:.02f} seconds, '
                        'current time; {}'.format(process_time, et.strftime('%H:%M')))
    elif process_time < 6000:
        print(__file__, 'Python Elapsed {:.02f} minute, '
                        'current time; {}'.format(process_time / 60, et.strftime('%H:%M')))
    else:
        print(__file__, 'Python Elapsed {:.02f} hours, '
                        'current time; {}'.format(process_time / 3600, et.strftime('%H:%M')))

