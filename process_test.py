import json
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup as bs

import logging
from ezp_logger import EzpLog
from main_process import MainProcess
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


def process_test():

    com = MainProcess()
    com.start()


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


def download_test():
    url = 'http://127.0.0.1:8000/media/actuator/000123/2018-09-02/%EC%83%81%EC%B6%94_20180831.csv'
    response = requests.get(url)
    with open('output_state.csv', 'wb') as f:
        f.write(response.content)


def get_state_test():
    url = 'http://127.0.0.1:8000/ezp10/api/controller/0001234/'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        u = UsbCapture()
        u.set_state(data)
        u.test_capture()


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


if __name__ == "__main__":
    t = time.time()

    # print(len('2018-08-27 20:32:48'))
    # print('{}'.format(datetime.now())[:19])

    get_state_test()

    # process_test()

    # bbs_upload_test()
    # json_upload_test()

    # usb_capture_upload_test()
    # usb_capture_upload_with_login_test()

    # log = EzpLog.log.get_logger(__name__)
    # log.setLevel(logging.DEBUG)
    # log.debug('한글출력')

    tm = time.localtime()
    process_time = (time.time() - t)
    if process_time < 100:
        print(__file__, 'Python Elapsed {:.02f} seconds, '
                        'current time; {:02d}:{:02d}'.format(process_time, tm.tm_hour, tm.tm_min))
    elif process_time < 6000:
        print(__file__, 'Python Elapsed {:.02f} minute, '
                        'current time; {:02d}:{:02d}'.format(process_time / 60, tm.tm_hour, tm.tm_min))
    else:
        print(__file__, 'Python Elapsed {:.02f} hours, '
                        'current time; {:02d}:{:02d}'.format(process_time / 3600, tm.tm_hour, tm.tm_min))
