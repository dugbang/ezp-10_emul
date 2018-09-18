import csv
import pickle
import time
from datetime import datetime

import cv2

from io_control import IoControl


def test01():
    # cap 이 정상적으로 open이 되었는지 확인하기 위해서 cap.isOpen() 으로 확인가능
    cap = cv2.VideoCapture(0)

    st_ = datetime.now()
    while cap.isOpened():
        ret, frame = cap.read()

        if ret:
            cv2.imshow('frame', frame)  # 화면에 출력할 필요는 없다.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            ct_ = datetime.now()
            if (ct_ - st_).total_seconds() > 10.:
                print('...ok...')
                break

    # 저장하기.. 추가한것
    # cv2.imwrite('capture/{}_{}.png'.format(st_.strftime('%Y%m%d'), '1301'), frame)

    cap.release()
    cv2.destroyAllWindows()


def test02():
    # st_ = datetime.now()
    print(datetime.now().strftime('%Y%m%d'))

    output = {}
    # TODO; linux 에서 문제없이 동작하는지 확인하기(윈도에서 확인됨)
    with open('output_times.csv', 'r', encoding='utf-8') as f:
        for line in csv.reader(f, delimiter='\t'):
            output[line[0]] = line[1:]

    # for key in output.keys():
    #     print(key, output[key])
    for i, key in enumerate(output):
        if i > 9:
            break
        print(key, output[key])

    key = datetime.now().strftime('%H%M')
    print(key, output[key])

    # for i in range(1):
    #     time.sleep(1)
    #     print(datetime.now().strftime('%H%M'))
    #     # tm_ = time.localtime()
    #     # print('current time; {:02d}:{:02d}:{:02d}'.format(tm_.tm_hour, tm_.tm_min, tm_.tm_sec))
    #
    # et_ = datetime.now()
    # print((et_ - st_).total_seconds())


def test_io_ctrl():
    with open('controller_state.pickle', 'rb') as f:
        data = pickle.load(f)

    # print(datetime.now().strftime('%H%M'))
    # print(time.localtime())
    ctrl = IoControl()
    ctrl.set_state(data)
    ctrl.test_01()


def test03():
    pass


if __name__ == "__main__":
    st = datetime.now()

    # test02()
    # u = UsbCapture()
    # u.test_capture()

    # test_io_ctrl()

    test02()

    et = datetime.now()
    process_time = int((et - st).total_seconds())
    if process_time < 100:
        print(__file__, 'Python Elapsed {:.02f} seconds, '
                        'current time; {}'.format(process_time, et.strftime('%H:%M')))
    elif process_time < 6000:
        print(__file__, 'Python Elapsed {:.02f} minute, '
                        'current time; {}'.format(process_time / 60, et.strftime('%H:%M')))
    else:
        print(__file__, 'Python Elapsed {:.02f} hours, '
                        'current time; {}'.format(process_time / 3600, et.strftime('%H:%M')))
