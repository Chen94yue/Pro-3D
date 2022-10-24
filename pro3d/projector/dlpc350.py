from __future__ import print_function
from email.mime import image

import usb.core
import usb.util
from usb.core import USBError
import time
from math import floor
from contextlib import contextmanager
import sys
from .builder import PROJECTOR


def conv_len(a, l):
    """
    Function that converts a number into a bit string of given length
    :param a: number to convert
    :param l: length of bit string
    :return: padded bit string
    """
    b = bin(a)[2:]
    padding = l - len(b)
    b = '0' * padding + b
    return b


def bits_to_bytes(a, reverse=True):
    """
    Function that converts bit string into a given number of bytes
    :param a: bites to convert
    :param reverse: whether or not to reverse the byte list
    :return: list of bytes
    """
    bytelist = []

    # check if needs padding
    if len(a) % 8 != 0:
        padding = 8 - len(a) % 8
        a = '0' * padding + a

    # convert to bytes
    for i in range(len(a) // 8):
        bytelist.append(int(a[8 * i:8 * (i + 1)], 2))

    if reverse:
        bytelist.reverse()
    return bytelist


@contextmanager
def connect_usb():
    """
    Context manager for connecting to and releasing usb device
    :yields: usb device
    """
    device = usb.core.find(idVendor=0x0451, idProduct=0x6401)
    for cfg in device:
        for intf in cfg:
            if device.is_kernel_driver_active(intf.bInterfaceNumber):
                try:
                    device.detach_kernel_driver(intf.bInterfaceNumber)
                except usb.core.USBError as e:
                    sys.exit("Could not detatch kernel driver from interface({0}): {1}".format(
                        intf.bInterfaceNumber, str(e)))
    device.set_configuration()
    lcr = dlpc350(device)
    yield lcr
    device.reset()
    del lcr
    del device


class dlpc350(object):
    """
    Class representing dmd controller.
    Can connect to different DLPCs by changing product ID. Check IDs in
    device manager.
    """

    def __init__(self, device):
        """
        connects device
        :param device: lcr4500 usb device
        """
        self.dlpc = device

    def command(self,
                mode,
                sequence_byte,
                com1,
                com2,
                data=None):
        """
        Sends a command to the dlpc
        :param mode: whether reading or writing
        :param sequence_byte:
        :param com1: command 1
        :param com2: command 3
        :param data: data to pass with command
        """
        buffer = []

        if mode == 'r':
            flagstring = 0xc0  # 0b11000000
        else:
            flagstring = 0x40  # 0b01000000

        data_len = conv_len(len(data) + 2, 16)
        data_len = bits_to_bytes(data_len)
        buffer.append(flagstring)
        buffer.append(sequence_byte)
        buffer.extend(data_len)
        buffer.append(com2)
        buffer.append(com1)

        # if data fits into single buffer, write all and fill
        if len(buffer) + len(data) < 65:
            for i in range(len(data)):
                buffer.append(data[i])

            # append empty data to fill buffer
            for i in range(64 - len(buffer)):
                buffer.append(0x00)
            # print_str = ''
            # for i in buffer:
            #     print_str += " %#x"%i
            # print(print_str)
            self.dlpc.write(1, buffer)

        # else, keep filling buffer and pushing until data all sent
        else:
            for i in range(64 - len(buffer)):
                buffer.append(data[i])

            self.dlpc.write(1, buffer)
            buffer = []

            j = 0
            while j < len(data) - 58:
                buffer.append(data[j + 58])
                j += 1

                if j % 64 == 0:
                    self.dlpc.write(1, buffer)
                    buffer = []

            if j % 64 != 0:
                while j % 64 != 0:
                    buffer.append(0x00)
                    j += 1

                self.dlpc.write(1, buffer)

        # done writing, read feedback from dlpc
        try:
            self.ans = self.dlpc.read(0x81, 64)
        except USBError as e:
            print('USB Error:', e)

        time.sleep(0.02)

    def read_reply(self):
        """
        Reads in reply
        """
        for i in self.ans:
            print(hex(i))

    def set_power_mode(self, do_standby=False):
        """
        The Power Control places the DLPC350 in a low-power state and powers down the DMD interface. Standby mode should
        only be enabled after all data for the last frame to be displayed has been transferred to the DLPC350. Standby
        mode must be disabled prior to sending any new data.
        (USB: CMD2: 0x02, CMD3: 0x00)
        :param do_standby: True = Standby mode. Places DLPC350 in low power state and powers down the DMD interface
                           False = Normal operation. The selected external source will be displayed
        """
        do_standby = int(do_standby)
        self.command('w', 0x00, 0x02, 0x00, [do_standby])

    def start_pattern_lut_validate(self):
        """
        This API checks the programmed pattern display modes and indicates any invalid settings. This command needs to
        be executed after all pattern display configurations have been completed.
        (USB: CMD2: 0x1A, CMD3: 0x1A)
        """
        self.command('w', 0x00, 0x1a, 0x1a, bits_to_bytes(conv_len(0x00, 8)))
        print(bin(self.ans[0]))
        print('validation:', bin(self.ans[6]))

    def set_display_mode(self, mode='pattern'):
        """
        Selects the input mode for the projector.
        (USB: CMD2: 0x1A, CMD3: 0x1B)
        :param mode: 0 = video mode
                     1 = pattern mode
        """
        modes = ['video', 'pattern']
        if mode in modes:
            mode = modes.index(mode)

        self.command('w', 0x00, 0x1a, 0x1b, [mode])

    def set_pattern_input_source(self, mode='video'):
        """
        Selects the input type for pattern sequence.
        (USB: CMD2: 0x1A, CMD3: 0x22)
        :param mode: 0 = video
                     3 = flash
        """
        modes = ['video', '', '', 'flash']
        if mode in modes:
            mode = modes.index(mode)
        print("pattern input source select %d." % mode)
        self.command('w', 0x00, 0x1a, 0x22, [mode])

    def set_pattern_trigger_mode(self, mode='vsync'):
        """
        Selects the trigger type for pattern sequence.
        (USB: CMD2: 0x1A, CMD3: 0x23)
        :param mode: 0 = vsync
        """
        modes = ['vsync', 'intext', 'trig', 'virintext', 'virvync']
        if mode in modes:
            mode = modes.index(mode)

        print("Trigger mode %d" % mode)
        self.command('w', 0x00, 0x1a, 0x23, [mode])

    def pattern_display(self, action='start'):
        """
        This API starts or stops the programmed patterns sequence.
        (USB: CMD2: 0x1A, CMD3: 0x24)
        :param action: Pattern Display Start/Stop Pattern Sequence
                       0 = Stop Pattern Display Sequence. The next "Start" command will restart the pattern sequence
                           from the beginning.
                       1 = Pause Pattern Display Sequence. The next "Start" command will start the pattern sequence by
                           re-displaying the current pattern in the sequence.
                       2 = Start Pattern Display Sequence
        """
        actions = ['stop', 'pause', 'start']
        if action in actions:
            action = actions.index(action)

        self.command('w', 0x00, 0x1a, 0x24, [action])

    def set_exposure_frame_period(self,
                                  exposure_period,
                                  frame_period):
        """
        The Pattern Display Exposure and Frame Period dictates the time a pattern is exposed and the frame period.
        Either the exposure time must be equivalent to the frame period, or the exposure time must be less than the
        frame period by 230 microseconds. Before executing this command, stop the current pattern sequence. After
        executing this command, call DLPC350_ValidatePatLutData() API before starting the pattern sequence.
        (USB: CMD2: 0x1A, CMD3: 0x29)
        :param exposure_period: exposure time in microseconds (4 bytes)
        :param frame_period: frame period in microseconds (4 bytes)
        """
        exposure_period = conv_len(exposure_period, 32)
        frame_period = conv_len(frame_period, 32)

        payload = frame_period + exposure_period
        payload = bits_to_bytes(payload)
        print("set exposure %s" % str(payload))
        self.command('w', 0x00, 0x1a, 0x29, payload)

    def set_pattern_config(self,
                           num_lut_entries=3,
                           do_repeat=True,
                           num_pats_for_trig_out2=3,
                           num_images=0):
        """
        This API controls the execution of patterns stored in the lookup table. Before using this API, stop the current
        pattern sequence using DLPC350_PatternDisplay() API. After calling this API, send the Validation command using
        the API DLPC350_ValidatePatLutData() before starting the pattern sequence.
        (USB: CMD2: 0x1A, CMD3: 0x31)
        :param num_lut_entries: number of LUT entries
        :param do_repeat: True = execute the pattern sequence once; False = repeat the pattern sequence
        :param num_pats_for_trig_out2: Number of patterns to display(range 1 through 256). If in repeat mode, then this
            value dictates how often TRIG_OUT_2 is generated
        :param num_images: Number of Image Index LUT Entries(range 1 through 64). This Field is irrelevant for Pattern
            Display Data Input Source set to a value other than internal
        """
        num_lut_entries = '0' + conv_len(num_lut_entries - 1, 7)
        do_repeat = '0000000' + str(int(do_repeat))
        num_pats_for_trig_out2 = conv_len(num_pats_for_trig_out2 - 1, 8)
        num_images = '00' + conv_len(num_images - 1, 6)

        payload = num_images + num_pats_for_trig_out2 + do_repeat + num_lut_entries
        payload = bits_to_bytes(payload)
        print('pattern config %s.' % str(payload))

        self.command('w', 0x00, 0x1a, 0x31, payload)

    def set_variable_pattern_config(self, num_lut_entries, num_pats_for_trig_out2, num_images, do_repeat=True):
        num_lut_entries = '00000' + conv_len(num_lut_entries - 1, 11)
        num_pats_for_trig_out2 = '00000' + \
            conv_len(num_pats_for_trig_out2 - 1, 11)
        num_images = conv_len(num_images - 1, 8)
        do_repeat = '0000000' + str(int(do_repeat))
        payload = do_repeat + num_images + num_pats_for_trig_out2 + num_lut_entries
        payload = bits_to_bytes(payload)
        self.command('w', 0x00, 0x1a, 0x40, payload)

    def mailbox_set_address(self, address=0):
        """
        This API defines the offset location within the DLPC350 mailboxes to write data into or to read data from.
        (USB: CMD2: 0x1A, CMD3: 0x32)
        :param address: Defines the offset within the selected (opened) LUT to write/read data to/from (0-127)
        """
        address = bits_to_bytes(conv_len(address, 8))
        self.command('w', 0x00, 0x1a, 0x32, address)

    def set_mailbox(self, mbox_num):
        """
        This API opens the specified Mailbox within the DLPC350 controller. This API must be called before sending data
        to the mailbox/LUT using DLPC350_SendPatLut() or DLPC350_SendImageLut() APIs.
        (USB: CMD2: 0x1A, CMD3: 0x33)
        :param mbox_num: 0 = Disable (close) the mailboxes
                         1 = Open the mailbox for image index configuration
                         2 = Open the mailbox for pattern definition
                         3 = Open the mailbox for the Variable Exposure
        """
        mbox_num = bits_to_bytes(conv_len(mbox_num, 8))
        self.command('w', 0x00, 0x1a, 0x33, mbox_num)

    def set_image_index(self, num_image):
        payload = ''
        for i in range(num_image):
            payload = conv_len(i, 8) + payload
        payload = bits_to_bytes(payload)
        # print("Set image index %s."%str(payload))
        self.command('w', 0x00, 0x1a, 0x34, payload)

    def set_image_index_variable(self, image_indexs):
        payload = ''
        for i in image_indexs:
            payload = conv_len(i, 8) + payload
        payload = bits_to_bytes(payload)
        # print("Set image variable index %s."%str(payload))
        self.command('w', 0x00, 0x1a, 0x34, payload)

    def set_LED_current(self, current):
        if current < 0:
            current = 0
        if current > 255:
            current = 255
        self.command('w', 0x00, 0x0b, 0x01, [current, current, current])

    def set_one_pattern_offset_index(self, index):
        payload = '00000' + conv_len(index, 11)
        payload = bits_to_bytes(payload)
        self.command('w', 0x00, 0x1a, 0x3f, payload)

    def set_one_pattern(self,
                        trigger_type, pattern_index,
                        bit_depth, led_color,
                        do_invert_pat, do_insert_black, swap, do_trig_out_prev,
                        exposure_period, frame_period
                        ):
        trigger_t = conv_len(trigger_type, 2)
        pattern_i = conv_len(pattern_index, 6)
        byte_0 = pattern_i + trigger_t
        bit_d = conv_len(bit_depth, 4)
        led_c = conv_len(led_color, 4)
        byte_1 = led_c + bit_d
        do_invert_pat = str(int(do_invert_pat))
        do_insert_black = str(int(do_insert_black))
        do_buf_swap = str(int(swap))
        do_trig_out_prev = str(int(do_trig_out_prev))

        byte_2 = '0000' + do_trig_out_prev + do_buf_swap + do_insert_black + do_invert_pat
        byte_3 = '00000000'
        exposure_period = conv_len(exposure_period, 32)
        frame_period = conv_len(frame_period, 32)
        byte_4 = frame_period + exposure_period
        payload = byte_4 + byte_3 + byte_2 + byte_1 + byte_0
        payload = bits_to_bytes(payload)
        self.command('w', 0x00, 0x1a, 0x3e, payload)

    def send_pattern_lut(self,
                         trig_type,
                         pat_num,
                         bit_depth,
                         led_select,
                         do_invert_pat=False,
                         do_insert_black=True,
                         do_buf_swap=True,
                         do_trig_out_prev=False):
        """
        Mailbox content to setup pattern definition. See table 2-65 in programmer's guide for detailed description of
        pattern LUT entries.
        (USB: CMD2: 0x1A, CMD3: 0x34)
        :param trig_type: Select the trigger type for the pattern
                          0 = Internal trigger
                          1 = External positive
                          2 = External negative
                          3 = No Input Trigger (Continue from previous; Pattern still has full exposure time)
                          0x3FF = Full Red Foreground color intensity
        :param pat_num: Pattern number (0 based index). For pattern number 0x3F, there is no pattern display. The
            maximum number supported is 24 for 1 bit-depth patterns. Setting the pattern number to be 25, with a
            bit-depth of 1 will insert a white-fill pattern. Inverting this pattern will insert a black-fill pattern.
            These patterns will have the same exposure time as defined in the Pattern Display Exposure and Frame Period
            command. Table 2-66 in the programmer's guide illustrates which bit planes are illuminated by each pattern
            number.
        :param bit_depth: Select desired bit-depth
                          0 = Reserved
                          1 = 1-bit
                          2 = 2-bit
                          3 = 3-bit
                          4 = 4-bit
                          5 = 5-bit
                          6 = 6-bit
                          7 = 7-bit
                          8 = 8-bit
        :param led_select: Choose the LEDs that are on: b0 = Red, b1 = Green, b2 = Blue
                           0 = No LED (Pass Through)
                           1 = Red
                           2 = Green
                           3 = Yellow (Green + Red)
                           4 = Blue
                           5 = Magenta (Blue + Red)
                           6 = Cyan (Blue + Green)
                           7 = White (Red + Blue + Green)
        :param do_invert_pat: True = Invert pattern
                              False = do not invert pattern
        :param do_insert_black: True = Insert black-fill pattern after current pattern. This setting requires 230 us
                                       of time before the start of the next pattern
                                False = do not insert any post pattern
        :param do_buf_swap: True = perform a buffer swap
                            False = do not perform a buffer swap
        :param do_trig_out_prev: True = Trigger Out 1 will continue to be high. There will be no falling edge
                                        between the end of the previous pattern and the start of the current pattern.
                                        Exposure time is shared between all patterns defined under a common
                                        trigger out). This setting cannot be combined with the black-fill pattern
                                 False = Trigger Out 1 has a rising edge at the start of a pattern, and a falling edge
                                         at the end of the pattern
        """
        single_image_pattern = 24 // bit_depth
        payload = ''
        for i in range(pat_num):
            print(i)
            swap = (i % single_image_pattern == 0)
            pat_index = i % single_image_pattern

            # byte 0
            trig_t = conv_len(trig_type, 2)
            pat_num = conv_len(pat_index, 6)

            byte_0 = pat_num + trig_t

            # byte 1
            bit_d = conv_len(bit_depth, 4)
            led_sel = conv_len(led_select, 4)

            byte_1 = led_sel + bit_d

            # byte 2
            do_invert_pat = str(int(do_invert_pat))
            do_insert_black = str(int(do_insert_black))
            do_buf_swap = str(int(swap))
            do_trig_out_prev = str(int(do_trig_out_prev))

            byte_2 = '0000' + do_trig_out_prev + do_buf_swap + do_insert_black + do_invert_pat

            payload_pattern = byte_2 + byte_1 + byte_0
            payload = payload_pattern + payload
        payload = bits_to_bytes(payload)
        # print("Set pattern %s."%(payload))
        self.command('w', 0x00, 0x1a, 0x34, payload)


@PROJECTOR.register_module()
class Ti4500:

    def __init__(self, bit_length, **kwargs):
        self.bit_length = bit_length

    def pattern_mode(
        self,
        num_pats=50,
        num_image=6,
        # trigger_type='intext',
        trigger_source=0,
        period=10000,
        bit_depth=1,
        led_color=4,
    ):
        # 设置投影序列
        # 默认从第一张图的第一个bit开始计算，若采用复杂设置方式，请使用variable_pattern_mode
        # 参数说明：
        # num_pats: 投影的pattern数量，不能大于128
        # num_image：固件中包含的24bit图像数量
        # tirgger_type：投影类型：'intext'内部或外部触发模式，‘vsync’同步模式。
        # trigger_source: 触发源，0内部触发，1外部高电平，2外部低电平，3无
        # period：曝光和pattern持续时间，会设定为一样的，如果需要单独特定设置，使用set_exposure_time。
        # bit_depth：每一个pattern的图像深度，目前只支持1bit和8bit，其余深度未测试，不确定有没有bug。
        # led_color：
        #   0 = No LED (Pass Through)
        #   1 = Red
        #   2 = Green
        #   3 = Yellow (Green + Red)
        #   4 = Blue
        #   5 = Magenta (Blue + Red)
        #   6 = Cyan (Blue + Green)
        #   7 = White (Red + Blue + Green)
        assert num_image * self.bit_length / bit_depth >= num_pats
        with connect_usb() as lcr:
            lcr.pattern_display('stop')
            lcr.set_display_mode('pattern')
            lcr.set_pattern_input_source('flash')
            lcr.set_pattern_config(num_lut_entries=num_pats,
                                   do_repeat=True,
                                   num_pats_for_trig_out2=1,
                                   num_images=num_image)
            lcr.set_exposure_frame_period(period, period)
            lcr.set_pattern_trigger_mode('intext')
            lcr.set_mailbox(2)
            lcr.mailbox_set_address(0)
            lcr.send_pattern_lut(trig_type=trigger_source,
                                 pat_num=num_pats,
                                 bit_depth=bit_depth,
                                 led_select=led_color,
                                 )
            lcr.set_mailbox(0)
            lcr.set_mailbox(1)
            lcr.mailbox_set_address(0)
            lcr.set_image_index(num_image)
            lcr.set_mailbox(0)
            lcr.start_pattern_lut_validate()

    def variable_pattern_mode(self, sequence):
        """
        设置投影序列,每一个pattern单独设置
        参数说明：
            sequence: 投影的pattern序列
            每一个元素为一个dict，包含如下信息：
            {
                'trigger_type': 0:内部，1：外部高电平，2：外部低电平 3：无触发信号，
                'pattern_index': 1~24 for bit depth 1,该参数和bit depth绑定，为当前bit depth下的pattern坐标
                'bit_depth'： 1~8，
                'led_color': 0~7,同pattern_mode，
                'do_invert_pat': 0
                'do_insert_black': 1
                'image_id': 投影的pattern在固件中的id
                'do_trig_out_prevc':0
                'exposure_period': 投影图案曝光时间
                'frame_period': 一个pattern的总时间
            }

        """
        image_indexs = []
        for index, pattern_info in enumerate(sequence):
            if index > 0:
                swap = (sequence[index]['image_id'] !=
                        sequence[index-1]['image_id'])
            else:
                swap = True
            if swap:
                image_indexs.append(sequence[index]['image_id'])

        with connect_usb() as lcr:
            lcr.pattern_display('stop')
            lcr.set_display_mode('pattern')
            lcr.set_pattern_input_source('flash')
            lcr.set_variable_pattern_config(
                num_lut_entries=len(sequence),
                num_pats_for_trig_out2=1,
                num_images=len(image_indexs),
                do_repeat=True
            )
            lcr.set_pattern_trigger_mode('virintext')

            lcr.set_mailbox(3)
            for index, pattern_info in enumerate(sequence):
                lcr.set_one_pattern_offset_index(index)
                if index > 0:
                    swap = (sequence[index]['image_id'] !=
                            sequence[index-1]['image_id'])
                else:
                    swap = True
                assert 24 / \
                    pattern_info['bit_depth'] > pattern_info['pattern_index']
                lcr.set_one_pattern(
                    pattern_info['trigger_type'],
                    pattern_info['pattern_index'],
                    pattern_info['bit_depth'],
                    pattern_info['led_color'],
                    pattern_info['do_invert_pat'],
                    pattern_info['do_insert_black'],
                    swap,
                    pattern_info['do_trig_out_prevc'],
                    pattern_info['exposure_period'],
                    pattern_info['frame_period']
                )
            lcr.set_mailbox(0)
            lcr.set_mailbox(1)
            lcr.set_one_pattern_offset_index(0)
            lcr.set_image_index_variable(image_indexs)
            lcr.set_mailbox(0)
            lcr.pattern_display('stop')
            lcr.pattern_display('stop')
            lcr.start_pattern_lut_validate()

    def video_mode(self):
        """
        Puts LCR4500 into video mode.
        """
        with connect_usb() as lcr:
            lcr.pattern_display('stop')
            lcr.set_display_mode('video')

    def power_down(self):
        """
        Puts LCR4500 into standby mode.
        """
        with connect_usb() as lcr:
            lcr.pattern_display('stop')
            lcr.set_power_mode(do_standby=True)

    def power_up(self):
        """
        Wakes LCR4500 up from standby mode.
        """
        with connect_usb() as lcr:
            lcr.set_power_mode(do_standby=False)

    def set_LED_current(self, val):
        """
        Set LED current 0-255.
        """
        with connect_usb() as lcr:
            val = 255 - val
            lcr.set_LED_current(val)

    def dlp_pause(self):
        with connect_usb() as lcr:
            lcr.pattern_display('pause')

    def dlp_start(self):
        with connect_usb() as lcr:
            lcr.pattern_display('start')

    def dlp_stop(self):
        with connect_usb() as lcr:
            lcr.pattern_display('stop')

    def set_exposure_time(self, exposure_time, period_time):
        with connect_usb() as lcr:
            lcr.pattern_display('stop')
            lcr.set_exposure_frame_period(exposure_time, period_time)
            lcr.start_pattern_lut_validate()
