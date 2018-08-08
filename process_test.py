import os
import time
from multiprocessing import Queue, Process
import queue

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


def test_process():

    com = Communication()
    com.start()

    # q_usb = Queue()
    # q_hwio = Queue()
    # q_main = Queue()
    #
    # print('main process pid; {}'.format(os.getpid()))
    #
    # process_usb = Process(target=usb_capture_process, args=(q_usb, q_main))
    # process_hwio = Process(target=hw_io_control_process, args=(q_hwio, q_main))
    # process_usb.start()
    # process_hwio.start()
    # time.sleep(2)
    # # q_usb.put(('quit', 'test'))
    # #
    # while True:
    #     try:
    #         msg = q_main.get(False)
    #     except queue.Empty:
    #         print('main sleep 1')
    #         time.sleep(1)
    #         q_usb.put(('quit', 'uab test...'))
    #         q_hwio.put(('quit', 'hw io test...'))
    #     else:
    #         print(msg)
    #         if msg[0] == 'quit':
    #             break
    #
    # process_usb.join()
    # process_hwio.join()
    #
    # q_usb.close()
    # q_hwio.close()
    # q_main.close()


if __name__ == "__main__":
    t = time.time()

    test_process()

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
