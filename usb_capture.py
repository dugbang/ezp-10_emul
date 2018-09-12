import os
import queue
import time
from datetime import datetime


class UsbCapture:
    def __init__(self):
        self.__capture_times = None  # ['0900', '1200', '1800']
        self.__select_time = ''

        self.capture_filename = ''
        self.capture_date = ''

        self.__state = {}
        self.__fields = ('is_active', 'is_usb_camera', 'capture_times', 'stable_time_of_camera')

    def set_state(self, total_state):
        for field in self.__fields:
            self.__state[field] = total_state[field]

        self.__capture_times = self.__state['capture_times'].split(',')

    def is_active(self):
        return self.__state['is_active']

    def is_exist(self):
        return self.__state['is_usb_camera']

    def is_capture_time(self, test_flag=False):
        s_time = datetime.now().strftime('%H%M')
        if test_flag:
            self.__select_time = s_time
            return True

        if self.__select_time == s_time:
            return False
        if s_time in self.__capture_times:
            self.__select_time = s_time
            return True
        return False

    def __capture_on_windows(self):
        import cv2
        cap = cv2.VideoCapture(0)
        st_ = datetime.now()
        ret = False
        while cap.isOpened():
            ret, frame = cap.read()
            ct_ = datetime.now()
            if (ct_ - st_).total_seconds() > self.__state['stable_time_of_camera']:
                self.capture_date = ct_
                self.capture_filename = 'capture/{}_{}.png'.format(ct_.strftime('%Y%m%d'), self.__select_time)
                cv2.imwrite(self.capture_filename, frame)  # capture...
                ret = True
                break

        cap.release()
        cv2.destroyAllWindows()
        return ret

    def __capture_on_linux(self):
        self.capture_date = datetime.now()
        self.capture_filename = 'capture/{}_{}.png'.format(self.capture_date.strftime('%Y%m%d'), self.__select_time)
        os.system('fswebcam -r 1920x1080 --no-banner {}'.format(self.capture_filename))

        return os.path.exists(self.capture_filename)

    def capture(self):
        import platform
        if platform.system() == 'linux':
            return self.__capture_on_linux()
        else:
            return self.__capture_on_windows()

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
            if not u.is_active() or not u.is_exist():
                continue

            if u.is_capture_time():
                print('is_capture_time....')
                if u.capture():
                    q_main.put(('capture', u.capture_date, u.capture_filename))
                    # time.sleep(1)
        else:
            if msg[0] == 'quit':
                print('usb_capture_process... exit')
                break
            elif msg[0] == 'set_state':
                print('usb_capture_process get; set_state')
                u.set_state(msg[1])

