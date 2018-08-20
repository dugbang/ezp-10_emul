import os
import time
from multiprocessing import Queue, Process
import queue
import requests
from bs4 import BeautifulSoup as bs

import logging
from ezp_logger import EzpLog
from hw_io_control import hw_io_control_process
from usb_capture import usb_capture_process


class Communication:
    """
    메인프로세스로 main 에서 실행된다.
    """

    def __init__(self):
        self.__queue = Queue()
        self.__q_usb = Queue()
        self.__q_hwio = Queue()

        self.__process = (
            Process(target=usb_capture_process, args=(self.__q_usb, self.__queue)),
            Process(target=hw_io_control_process, args=(self.__q_hwio, self.__queue)),
        )

    def __run(self):
        while True:
            try:
                msg = self.__queue.get(False)
            except queue.Empty:
                print('main sleep 1')
                time.sleep(1)
                self.__q_usb.put(('quit', 'uab test...'))
                self.__q_hwio.put(('quit', 'hw io test...'))
            else:
                print(msg)
                if msg[0] == 'quit':
                    break

    def start(self):
        print('main process pid; {}'.format(os.getpid()))

        for process in self.__process:
            process.start()

        time.sleep(2)
        self.__run()

        for process in self.__process:
            process.join()

    def __del__(self):
        print('Communication del... ')
        self.__queue.close()
        self.__q_usb.close()
        self.__q_hwio.close()


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


def test_process():

    com = Communication()
    com.start()


if __name__ == "__main__":
    t = time.time()

    # test_process()

    # usb_capture_upload_test()
    # usb_capture_upload_with_login_test()

    log = EzpLog.log.get_logger('test')
    log.setLevel(logging.DEBUG)
    log.debug('한글출력')

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
