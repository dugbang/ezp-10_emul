import os
import time
from multiprocessing import Queue, Process
import queue
import requests

import logging
from ezp_logger import EzpLog
from hw_io_control import hw_io_control_process
from usb_capture import usb_capture_process


class Communication:
    """
    메인프로세스로 main 에서 실행된다.
    """

    # log = Ezp10Logging()

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
    CAPTURE_URL = 'http://127.0.0.1:8000/gm_photos/upload/'
    files = {'image': open('d:\Documents\앙키01.png', 'rb')}  # indicate > name
    values = {'content': 'requests.post... 입력'}  # indicate > name

    try:
        r = requests.post(CAPTURE_URL, files=files, data=values)
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)


def test_process():

    com = Communication()
    com.start()


if __name__ == "__main__":
    t = time.time()

    # Now, we can log to the root logger, or any other logger. First the root...
    # logging.info('Jackdaws love my big sphinx of quartz.')

    # logger1 = logging.getLogger('ezp-10.area1')
    # logger2 = logging.getLogger('ezp-10.area2')

    logger0 = EzpLog.log.get_logger()
    logger1 = EzpLog.log.get_logger('area1')
    logger2 = EzpLog.log.get_logger('area2')

    logger1.setLevel(logging.WARNING)
    logger1.debug('Quick zephyrs blow, vexing daft Jim.')
    logger1.info('How quickly daft jumping zebras vex.')
    logger1.critical('logger1 ... message...')
    logger2.warning('Jail zesty vixen who grabbed pay from quack.')
    logger2.error('The five boxing wizards jump quickly.')

    logger0.critical('class... message...')

    # log.debug('debug')
    # log.info('info')
    # log.warning('warning')
    # log.error('error')
    # log.critical('critical')

    # test_process()

    # usb_capture_upload_test()

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
