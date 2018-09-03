import os
import queue
import time
from multiprocessing import Queue, Process

from hw_io_control import hw_io_control_process
from usb_capture import usb_capture_process


class MainProcess:
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
        self.__capture_info = []

    def __run(self):
        while True:
            try:
                msg = self.__queue.get(False)
            except queue.Empty:
                print('main sleep 1')
                time.sleep(1)
                # self.__q_usb.put(('quit', 'uab test...'))
                # self.__q_hwio.put(('quit', 'hw io test...'))
            else:
                print(msg)
                if msg[0] == 'quit':
                    break
                elif msg[0] == 'capture':
                    self.__capture_info.append((msg[1], msg[2]))

    def start(self):
        print('main process pid; {}'.format(os.getpid()))

        # TODO; 서버에서 상태정보를 읽어온다.

        for process in self.__process:
            process.start()

        # TODO; 최초의 메시지 전송은 여기서 이루어진다.
        time.sleep(0.5)
        self.__run()

        for process in self.__process:
            process.join()

    def __del__(self):
        print('MainProcess del... ')
        self.__queue.close()
        self.__q_usb.close()
        self.__q_hwio.close()


if __name__ == "__main__":
    t = time.time()

    task_main = MainProcess()
    task_main.start()

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
