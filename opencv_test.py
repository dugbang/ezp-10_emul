import time
from datetime import datetime

import cv2

from usb_capture import UsbCapture


def test01():
    # cap 이 정상적으로 open이 되었는지 확인하기 위해서 cap.isOpen() 으로 확인가능
    cap = cv2.VideoCapture(0)

    st_ = datetime.now()
    while True:
        ret, frame = cap.read()

        if ret:
            # cv2.imshow('frame', frame)  # 화면에 출력할 필요는 없다.
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            ct_ = datetime.now()
            if (ct_ - st_).total_seconds() > 10.:
                break

    # 저장하기.. 추가한것
    cv2.imwrite('capture/{}_{}.png'.format(st_.strftime('%Y%m%d'), '1301'), frame)

    cap.release()
    cv2.destroyAllWindows()


def test02():
    st_ = datetime.now()
    print(datetime.now().strftime('%Y%m%d'))
    for i in range(5):
        time.sleep(1)
        tm_ = time.localtime()
        print('current time; {:02d}:{:02d}:{:02d}'.format(tm_.tm_hour, tm_.tm_min, tm_.tm_sec))

    et_ = datetime.now()
    print((et_ - st_).total_seconds())


if __name__ == "__main__":
    t = time.time()

    # test01()
    u = UsbCapture()
    u.test_capture()

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
