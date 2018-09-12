import csv
import os
import queue
import time
from datetime import datetime
from random import uniform


def tank_capacity():
    return '{:.2f}'.format(uniform(0., 1.))


def temperature():
    return '{:.1f}'.format(uniform(0., 30.))


def ph():
    return '{:.2f}'.format(uniform(0., 1.))


def mc():
    return '{:.2f}'.format(uniform(0., 1.))


def temp_humidity_high():
    return '{:.2f}'.format(uniform(0., 1.))


def temp_humidity_low():
    return '{:.2f}'.format(uniform(0., 1.))


def luminance():
    return '{:.2f}'.format(uniform(0., 1.))


def co2():
    return '{:.2f}'.format(uniform(0., 1.))


def led(value):
    print('led ctrl; {}'.format(value))


def pump(value):
    print('pump ctrl; {}'.format(value))


def pan_high(value):
    print('pan_high ctrl; {}'.format(value))


def pan_low(value):
    print('pan_low ctrl; {}'.format(value))


class IoControl:
    FILE_OUTPUT_TIMES = 'output_times.csv'

    def __init__(self):
        self.duration = 60
        self.records = []

        self.__output = {}
        self.__o_key = ''

        self.__state = {}
        self.__fields = ('minute_of_action_cycle', 'actuator_csv', 'is_active',
                         'iis_tank_capacity', 'iis_temperature', 'iis_ph', 'iis_mc',
                         'iis_temp_humidity_high', 'iis_temp_humidity_low', 'iis_luminance', 'iis_co2',
                         'ois_led', 'ois_pump', 'ois_pan_high', 'ois_pan_low',)

        self.__o_fields = ('ois_led', 'ois_pump', 'ois_pan_high', 'ois_pan_low',)
        self.__o_functions = (led, pump, pan_high, pan_low,)

        self.__i_fields = ('iis_tank_capacity', 'iis_temperature', 'iis_ph', 'iis_mc',
                           'iis_temp_humidity_high', 'iis_temp_humidity_low',
                           'iis_luminance', 'iis_co2',)
        self.__i_functions = (tank_capacity, temperature,
                              ph, mc, temp_humidity_high,
                              temp_humidity_low, luminance, co2,)

        self.__prev_actuator_csv = ''

    def is_active(self):
        return self.__state['is_active']

    def set_state(self, total_state):
        for field in self.__fields:
            self.__state[field] = total_state[field]

        self.duration = 60 * self.__state['minute_of_action_cycle']
        if self.__prev_actuator_csv != self.__state['actuator_csv']:
            self.__prev_actuator_csv = self.__state['actuator_csv']
            self.read_file_output_times()

    def read_file_output_times(self):
        # TODO; linux 에서 문제없이 동작하는지 확인하기(윈도에서 확인됨)
        with open(IoControl.FILE_OUTPUT_TIMES, 'r', encoding='utf-8') as f:
            print('read file; {}'.format(IoControl.FILE_OUTPUT_TIMES))
            for line in csv.reader(f, delimiter='\t'):
                # self.__output[line[0]] = line[1:]
                self.__output[line[0]] = [True if r == '1' else False for r in line[1:]]

    def hw_output(self):
        # rec = [0] * len(self.__o_fields)
        self.records = [datetime.now(), ]

        self.__o_key = datetime.now().strftime('%H%M')
        for i, field in enumerate(self.__o_fields):
            if self.__state[field]:
                self.__o_functions[i](self.__output[self.__o_key][i])
                # print('output >> index; {} / value; {}'.format(i, self.__output[self.__o_key][i]))

    def hw_input(self):
        rec = ['0'] * len(self.__i_fields)
        for i, field in enumerate(self.__i_fields):
            if self.__state[field]:
                rec[i] = self.__i_functions[i]()

        self.records.extend(rec)
        self.records.extend(self.__output[self.__o_key])

    def test_01(self):
        self.read_file_output_times()
        key = datetime.now().strftime('%H%M')
        print(key, self.__output[key])
        print('__i_function', self.__i_functions[0]())
        self.hw_output()
        self.hw_input()
        print(self.records)


def io_control_process(q, q_main):
    print('hw_io_control_process pid; {}'.format(os.getpid()))
    time.sleep(1)

    ctrl = IoControl()
    st_ = datetime.now()
    while True:
        try:
            msg = q.get(False)
        except queue.Empty:
            time.sleep(1)
            if not ctrl.is_active():
                continue

            ct_ = datetime.now()
            if (ct_ - st_).total_seconds() < ctrl.duration:
                continue
            st_ = ct_

            print('io_control hw....')
            ctrl.hw_output()
            ctrl.hw_input()
            q_main.put(('io_records', ctrl.records))
        else:
            # print(msg)
            if msg[0] == 'quit':
                print('io_control_process... exit')
                break
            elif msg[0] == 'set_state':
                print('io_control_process get; set_state')
                ctrl.set_state(msg[1])
            elif msg[0] == 'output_times':
                print('io_control_process get; output_times')
                ctrl.read_file_output_times()

