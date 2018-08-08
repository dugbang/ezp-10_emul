import os
import queue
import time


def usb_capture_process(q, q_main):
    print('usb_capture_process pid; {}'.format(os.getpid()))
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
                q_main.put(('quit', 'main...'))
                break
