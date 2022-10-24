import sys
from ctypes import *
from third.hikrobot.MvCameraControl_class import *
import numpy as np
import cv2
from pro3d.utils.logging import get_logger
from .builder import CAMERA
from .base_camera import BaseCamera


@CAMERA.register_module()
class HikrobotCamera(BaseCamera):

    def __init__(self,
                 dill_path,
                 camera_serial,
                 exposure_time,
                 gain,
                 gamma,
                 rgb,
                 log_file,
                 log_level,
                 **kwargs):
        super(HikrobotCamera, self).__init__()
        self.logger = get_logger(
            name='hikrobot_camera', log_file=log_file, log_level=log_level)
        self.cam_serial_dict = {}
        for camera_serial in camera_serial:
            self.cam_serial_dict[camera_serial] = []
        deviceList = MV_CC_DEVICE_INFO_LIST()
        tlayerType = MV_USB_DEVICE
        MvCamera.set_dill_path(dill_path)
        ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
        if ret != 0:
            self.logger.info("Enum devices fail! ret[0x%x]" % ret)
            sys.exit()
        if deviceList.nDeviceNum == 0:
            self.logger.info("Find no device!")
            sys.exit()
        # camera_index = -1
        for i in range(0, deviceList.nDeviceNum):
            mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(
                MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                self.logger.info("U3V device: [%d]" % i)
                strModeName = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                    if per == 0:
                        break
                    strModeName = strModeName + chr(per)
                self.logger.info("Device model name: %s" % strModeName)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                self.logger.info("User serial number: %s" % strSerialNumber)
                if strSerialNumber in camera_serial:
                    self.cam_serial_dict[strSerialNumber] = i
        self.cam = {}
        for key, value in self.cam_serial_dict:
            self.cam[key] = (MvCamera(), cast(
                deviceList.pDeviceInfo[value], POINTER(MV_CC_DEVICE_INFO)).contents)
            # self.cam[key][0].set_dill_path(dill_path)

        # self.cam = MvCamera()
        # self.stDeviceList = cast(deviceList.pDeviceInfo[camera_index], POINTER(MV_CC_DEVICE_INFO)).contents
        self.exposureTime = exposure_time
        self.gain = gain
        self.gamma = gamma
        self.rgb = rgb
        self.set_camera()

    def set_camera(self):
        for i in self.cam.keys():
            ret = self.cam[i][0].MV_CC_CreateHandle(self.cam[i][1])
            if ret != 0:
                self.logger.info("Create handle failed.")
                sys.exit()
            self.cam[i] = self.cam[i][0]

        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
            if ret != 0:
                self.logger.info("Open device failed.")
                sys.exit()

        stBool = c_bool(False)
        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_GetBoolValue(
                "AcquisitionFrameRateEnable", stBool)
            if ret != 0:
                self.logger.info("Get AcquisitionFrameRateEnable failed.")
                sys.exit()

        # ch:设置触发模式为off | en:Set trigger mode as off
        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_SetEnumValue(
                "TriggerMode", MV_TRIGGER_MODE_OFF)
            if ret != 0:
                self.logger.info("Set trigger mode failed.")
                sys.exit()

        stParam = MVCC_INTVALUE()
        memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))
        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_GetIntValue("PayloadSize", stParam)
            if ret != 0:
                self.logger.info("Set PayloadSize failed.")
                sys.exit()

        self.payload_size = stParam.nCurValue
        self.data_buf_dict = {}
        self.stFrameInfo_dict = {}
        for i in self.cam.keys():
            self.data_buf_dict[i] = byref((c_ubyte * self.payload_size)())
            self.stFrameInfo_dict[i] = MV_FRAME_OUT_INFO_EX()
            memset(byref(self.stFrameInfo_dict[i]), 0, sizeof(
                self.stFrameInfo_dict[i]))

        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_SetEnumValue(
                "ExposureMode", MV_EXPOSURE_MODE_TIMED)
            if ret != 0:
                self.logger.info("Set exposure mode failed.")
                sys.exit()
        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_SetEnumValue(
                "ExposureAuto", MV_EXPOSURE_AUTO_MODE_OFF)
            if ret != 0:
                self.logger.info("Set exposure auto failed.")
                sys.exit()
        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_SetFloatValue(
                "ExposureTime", float(self.exposureTime))  # us
            if ret != 0:
                self.logger.info("Set exposure time failed.")
                sys.exit()
        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_SetFloatValue("Gain", float(self.gain))
            if ret != 0:
                self.logger.info("Set gain value failed.")
                sys.exit()
        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_SetBoolValue("GammaEnable", True)
            if ret != 0:
                self.logger.info("Set GammaEnable fail!")
                sys.exit()
        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_SetEnumValue("GammaSelector", 1)
            if ret != 0:
                self.logger.info("Set GammaSelector fail!")
                sys.exit()
        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_SetFloatValue("Gamma", self.gamma)
            if ret != 0:
                self.logger.info("Set Gamma failed!")
                sys.exit()
    # ch:开始取流 | en:Start grab image

    def start(self):
        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_StartGrabbing()
            if ret != 0:
                self.logger.info("Start Camera failed!")
                sys.exit()

    def get_image(self):
        self.images = {}
        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_GetOneFrameTimeout(
                self.data_buf_dict[i], self.payload_size, self.stFrameInfo_dict[i], 1000)
            if ret == 0:
                frame_data = np.ctypeslib.as_array(self.data_buf_dict[i])
                if self.rgb:
                    self.images[i] = frame_data.reshape(
                        (self.stFrameInfo_dict[i].nHeight, self.stFrameInfo_dict[i].nWidth, 3))
                    self.images[i] = cv2.cvtColor(
                        self.images[i], cv2.COLOR_RGB2BGR)
                else:
                    self.images[i] = frame_data.reshape(
                        (self.stFrameInfo_dict[i].nHeight, self.stFrameInfo_dict[i].nWidth))
            else:
                self.logger.info("Get image failed.")
                sys.exit()

    def stop(self):
        for i in self.cam.keys():
            ret = self.cam[i].MV_CC_StopGrabbing()
            if ret != 0:
                self.logger.info("Stop Camera failed!")
                sys.exit()
