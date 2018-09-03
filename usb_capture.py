import os
import queue
import time
from datetime import datetime
import cv2


class UsbCapture:
    def __init__(self):
        self.__capture_times = None  # ['0900', '1200', '1800']
        self.__select_time = ''

        self.capture_filename = ''
        self.capture_date = ''

        self.__state = {'is_usb_camera': False,
                        'capture_times': '0900,1200,1800',
                        'stable_time_of_camera': 5}
        self.__fields = ('is_usb_camera', 'capture_times', 'stable_time_of_camera')

        # self.__fields = ('serial', 'is_action', 'plant',
        #                  'minute_of_action_cycle', 'minute_of_upload_cycle',
        #                  'iis_tank_capacity', 'iis_temperature', 'iis_ph', 'iis_mc',
        #                  'iis_temp_humidity_high', 'iis_temp_humidity_low', 'iis_luminance', 'iis_co2',
        #                  'ois_led', 'ois_pump', 'ois_pan_high', 'ois_pan_low',
        #                  'is_usb_camera', 'modify_date', 'actuator_csv',
        #                  'capture_times', 'stable_time_of_camera')

    def set_state(self, total_state):
        for field in self.__fields:
            self.__state[field] = total_state[field]

        self.__capture_times = self.__state['capture_times'].split(',')

    def is_exist(self):
        return self.__state['is_usb_camera']

    def is_capture_time(self, test_flag=False):
        tm_ = time.localtime()
        s_time = '{:02d}{:02d}'.format(tm_.tm_hour, tm_.tm_min)
        if test_flag:
            self.__capture_times.append(s_time)
        if s_time in self.__capture_times:
            self.__select_time = s_time
            return True
        return False

    def capture(self):
        cap = cv2.VideoCapture(0)
        st_ = datetime.now()
        while True:
            ret, frame = cap.read()
            ct_ = datetime.now()
            if (ct_ - st_).total_seconds() > self.__state['stable_time_of_camera']:
                break

        # self.capture_date = '{}'.format(ct_)[:19]  # '{}'.format(datetime.now())[:19]
        self.capture_date = ct_
        self.capture_filename = 'capture/{}_{}.png'.format(ct_.strftime('%Y%m%d'), self.__select_time)
        cv2.imwrite(self.capture_filename, frame)

        cap.release()
        cv2.destroyAllWindows()

    def test_capture(self):
        if self.is_capture_time(test_flag=True):
            self.capture()


def usb_capture_process(q, q_main):
    print('usb_capture_process pid; {}'.format(os.getpid()))
    time.sleep(1)

    u = UsbCapture()
    while True:
        try:
            msg = q.get(False)
        except queue.Empty:
            time.sleep(1)

            if u.is_exist() and u.is_capture_time():
                u.capture()
                q_main.put(('capture', u.capture_date, u.capture_filename))
        else:
            if msg[0] == 'quit':
                q_main.put(('quit', 'usb_capture_process... exit'))
                break
            elif msg[0] == 'set_state':
                u.set_state(msg[1])

