import json
import pickle
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup as bs

import logging
from ezp_logger import EzpLog
from ez_controller import MainProcess, Communication
from io_control import IoControl
from usb_capture import UsbCapture


def usb_capture_upload_test():
    url_upload = 'http://127.0.0.1:8000/gm_photos/upload/'
    values = {'content': 'requests.post... '}
    files = {'image': open('d:\Documents\삼성카드해지01.png', 'rb')}

    log = EzpLog.log.get_logger('upload')
    log.setLevel(logging.DEBUG)

    with requests.Session() as s:

        try:
            first_page = s.get(url_upload)
            soup = bs(first_page.text, 'html.parser')
            csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            values = {**values, **{'csrfmiddlewaretoken': csrf['value']}}
            log.debug(values)

            r = s.post(url_upload, files=files, data=values)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            log.error("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            log.error("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            log.error("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            log.error("OOps: Something Else", err)


def usb_capture_upload_with_login_test():
    # url = 'http://127.0.0.1:8000/gm_photos/upload/'
    # values = {'content': 'requests.post... 입력'}  # indicate > name

    url_upload = 'http://127.0.0.1:8000/photo/photo/add/'
    UPLOAD_INFO = {'album': '3',  # select index 정보를 입력하여야 함...
                   'title': 'test...01',
                   'description': 'description requests.post',
                   }  # indicate > name
    files = {'image': open('d:\Documents\Screenshot_2015-10-28-15-14-46.png', 'rb')}

    log = EzpLog.log.get_logger('upload login')
    log.setLevel(logging.DEBUG)

    url_login = 'http://127.0.0.1:8000/accounts/login/'
    LOGIN_INFO = {
        'username': 'raspi',
        'password': 'passwd123'
    }

    # Session 생성, with 구문 안에서 유지
    with requests.Session() as s:

        try:
            first_page = s.get(url_login)
            csrf = bs(first_page.text, 'html.parser').find('input', {'name': 'csrfmiddlewaretoken'})
            post_data = {**LOGIN_INFO, **{'csrfmiddlewaretoken': csrf['value']}}

            r = s.post(url_login, data=post_data)
            r.raise_for_status()
            log.debug(r.status_code)

            first_page = s.get(url_upload)
            soup = bs(first_page.text, 'html.parser')
            csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            post_data = {**UPLOAD_INFO, **{'csrfmiddlewaretoken': csrf['value']}}

            r = s.post(url_upload, files=files, data=post_data)
            r.raise_for_status()
            # log.debug(r.status_code)

        except requests.exceptions.HTTPError as errh:
            log.error("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            log.error("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            log.error("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            log.error("OOps: Something Else", err)


def json_upload_test():
    url_upload_json = 'http://127.0.0.1:8000/ezp10/api/plant/'

    data = {'name': '무우'}
    req_post(data, url_upload_json)


def bbs_upload_test():
    url_upload_json = 'http://127.0.0.1:8000/bbs/'

    # TODO; 복수개의 데이터 전송방법은?
    data = {
                "title": "title test json...3",
                "author": "michael",
                "pw": "qwer1234",
                "content": "i am here.. json"
            }
    req_post(data, url_upload_json)


def req_post(data, url_upload_json):
    log = EzpLog.log.get_logger('rest framework')
    headers = {'content-type': 'application/json'}
    log.setLevel(logging.DEBUG)
    with requests.Session() as s:
        try:
            r = s.post(url_upload_json, data=json.dumps(data), headers=headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            log.error('Http Error:{}, status_code; {}'.format(errh, r.status_code))
        except requests.exceptions.ConnectionError as errc:
            log.error("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            log.error("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            log.error("OOps: Something Else", err)


def get_state_test():
    url = 'http://127.0.0.1:8000/ezp10/api/controller/0001234/'
    response = requests.get(url)
    if response.status_code == 200:
        state_ = response.json()
        print(state_)
        u = UsbCapture()
        u.set_state(state_)
        u.test_capture()

        response = requests.get(state_['actuator_csv'])
        with open('output_state.csv', 'wb') as f:
            f.write(response.content)

        with open('controller_state.pickle', 'wb') as f:
            pickle.dump(state_, f, pickle.HIGHEST_PROTOCOL)


def loop_step_test():
    print('loop_step_test')
    duration = 5
    st_ = datetime.now()
    for i in range(5):
        while True:
            ct_ = datetime.now()
            time.sleep(1)
            if (ct_ - st_).total_seconds() > duration:
                st_ = ct_
                break
        print('step; {}'.format(i))


def upload_capture():
    # http://127.0.0.1:8000/ezp10/capture/upload/
    url = 'http://127.0.0.1:8000/ezp10/capture/upload/'
    files = {'image': open('capture/20180911_1511.png', 'rb')}
    # data = {'plant': 1, 'controller': '0001234', 'create_at': '2018-08-27 20:32:48'}
    st_ = datetime.now()
    data = {'plant': 1, 'controller': '0001234', 'create_at': st_}

    with requests.Session() as s:

        first_page = s.get(url)
        soup = bs(first_page.text, 'html.parser')
        csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        post_data = {**data, **{'csrfmiddlewaretoken': csrf['value']}}

        res = s.post(url, files=files, data=post_data)
        if res.status_code == 200:
            print('ok')

        print('post_file_data res.status_code; ', res.status_code)


if __name__ == "__main__":
    st = datetime.now()

    upload_capture()

    # print(len('2018-08-27 20:32:48'))
    # print('{}'.format(datetime.now())[:19])

    # comm = Communication()
    # comm.set_state()
    # # print(comm.state)
    # while not comm.is_active():
    #     print('{} >> sleep; {}'.format(datetime.now().strftime('%H:%M:%S'), comm.duration/10))
    #     time.sleep(comm.duration/10)
    #     comm.set_state()
    #     # break
    #
    # str_now = '{}'.format(datetime.now())
    # print(str_now)
    # comm.add_capture_records((datetime.now(), 'capture/20180911_1511.png'))
    # comm.upload_data()

# =======================================================

    # print(comm.state)
    # print('{}'.format(datetime.now().strftime('%H:%M:%S')))
    #
    # u = UsbCapture()
    # u.set_state(comm.state)
    # if u.is_exist():
    #     u.test_capture()
    #     print(u.capture_date, u.capture_filename)
    #
    # ctrl = IoControl()
    # ctrl.set_state(comm.state)
    # ctrl.hw_output()
    # ctrl.hw_input()
    # print(ctrl.records)
    #
    # comm.add_capture_records((datetime.now(), 'capture/20180911_1511.png'))
    # comm.upload_data()

    # log = EzpLog.log.get_logger(__name__)
    # log.setLevel(logging.DEBUG)
    # log.debug('한글출력')

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
