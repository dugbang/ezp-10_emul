import os
import time
from multiprocessing import Queue, Process
import queue


def usb_capture_process(q, q_main):
    i = 0
    while True:
        try:
            msg = q.get(False)
        except queue.Empty:
            time.sleep(1)
            i += 1
            print('usb sleep {}'.format(i))
            if i > 5:
                print('time out...')
                break
        else:
            print(msg)
            if msg[0] == 'quit':
                q_main.put(('quit', 'test'))
                break
            # Handle task here and call q.task_done()


def hw_io_control_process():
    pass


def f(q):
    q.put([42, None, 'hello'])


def test_process():

    # q = Queue()
    # p = Process(target=f, args=(q,))
    # p.start()
    # print(q.get())    # prints "[42, None, 'hello']"
    # p.join()

    q_usb = Queue()
    # q_hwio = Queue()
    q_main = Queue()

    print(os.getpid())

    process_one = Process(target=usb_capture_process, args=(q_usb, q_main))
    process_one.start()
    time.sleep(2)
    # q_usb.put(('quit', 'test'))
    #
    # while True:
    #     try:
    #         msg = q_main.get(False)
    #     except queue.Empty:
    #         print('main sleep 1')
    #         time.sleep(1)
    #     else:
    #         print(msg)
    #         if msg[0] == 'quit':
    #             break

    process_one.join()

    q_usb.close()
    # q_hwio.close()
    q_main.close()


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
