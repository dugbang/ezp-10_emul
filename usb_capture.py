import os
import queue
import time
from datetime import datetime
import cv2


class UsbCapture:
    def __init__(self):
        self.__stable_time = 10
        self.__capture_times = None  # ['0900', '1200', '1800']
        self.__select_time = ''
        self.__exist = False

        self.capture_filename = ''
        self.capture_date = ''

    def set_exist(self, flag=False):
        self.__exist = flag

    def is_exist(self):
        return self.__exist

    def set_stable_time(self, stable=10):
        self.__stable_time = stable

    def set_capture_times(self, str_times='0900,1200,1800'):
        self.__capture_times = str_times.split(',')
        # print(self.__capture_times)

    def is_capture_time(self):
        tm_ = time.localtime()
        s_time = '{:02d}{:02d}'.format(tm_.tm_hour, tm_.tm_min)
        # self.__capture_times.append(s_time)
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
            if (ct_ - st_).total_seconds() > self.__stable_time:
                break

        self.capture_date = '{}'.format(ct_)[:19]  # '{}'.format(datetime.now())[:19]
        self.capture_filename = 'capture/{}_{}.png'.format(st_.strftime('%Y%m%d'), self.__select_time)
        cv2.imwrite(self.capture_filename, frame)

        cap.release()
        cv2.destroyAllWindows()

    def test_capture(self):
        self.set_capture_times()
        if self.is_capture_time():
            self.capture()


def usb_capture_process(q, q_main):
    print('usb_capture_process pid; {}'.format(os.getpid()))
    # i = 0
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
            elif msg[0] == 'set_stable_time':  # int
                u.set_stable_time(msg[1])
            elif msg[0] == 'set_capture_times':  # string '0900,1200,1800'
                u.set_capture_times(msg[1])
            elif msg[0] == 'set_exist':  # bool True / False
                u.set_exist(msg[1])

