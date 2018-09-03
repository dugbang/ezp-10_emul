import os
import queue
import time
from datetime import datetime


def hw_io_control_process(q, q_main):
    print('hw_io_control_process pid; {}'.format(os.getpid()))
    time.sleep(1)

    duration = 5 * 60
    st_ = datetime.now()
    while True:
        try:
            msg = q.get(False)
        except queue.Empty:
            time.sleep(1)
            ct_ = datetime.now()
            if (ct_ - st_).total_seconds() > duration:
                st_ = ct_
                # TODO; 센싱 시작하기...
        else:
            # print(msg)
            if msg[0] == 'quit':
                q_main.put(('quit', 'main...'))
                break
            elif msg[0] == 'set_duration':  # 분단위 정보
                duration = msg[1] * 60
