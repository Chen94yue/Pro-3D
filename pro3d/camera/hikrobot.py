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
        self.cam_serial = camera_serial

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
        camera_index = -1
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
                if strSerialNumber == camera_serial:
                    camera_index = i
        
        self.cam = MvCamera()
        self.stDeviceList = cast(deviceList.pDeviceInfo[camera_index], POINTER(MV_CC_DEVICE_INFO)).contents
            # self.cam[key][0].set_dill_path(dill_path)

        # self.cam = MvCamera()
        # self.stDeviceList = cast(deviceList.pDeviceInfo[camera_index], POINTER(MV_CC_DEVICE_INFO)).contents
        self.exposureTime = exposure_time
        self.gain = gain
        self.gamma = gamma
        self.rgb = rgb
        self.set_camera()

    def set_camera(self):

        ret = self.cam.MV_CC_CreateHandle(self.stDeviceList)
        if ret != 0:
            self.logger.info("Create handle failed.")
            sys.exit()
        
        ret = self.cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if ret != 0:
            self.logger.info("Open device failed.")
            sys.exit()
        
        if self.stDeviceList.nTLayerType == MV_GIGE_DEVICE:
            nPacketSize = self.cam.MV_CC_GetOptimalPacketSize()
            if int(nPacketSize) > 0:
                ret = self.cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
                if ret != 0:
                    self.logger.info("Set GevSCPSPacketSize failed.")
                    sys.exit()
            else:
                self.logger.info("Warning: Get Packet Size fail! ret[0x%x]" % nPacketSize)

        stBool = c_bool(False)
        ret = self.cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", stBool)
        if ret != 0:
            self.logger.info("Get AcquisitionFrameRateEnable failed.")
            sys.exit()

        # ch:设置触发模式为off | en:Set trigger mode as off
        ret = self.cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
        if ret != 0:
            self.logger.info("Set trigger mode failed.")
            sys.exit()

        stParam = MVCC_INTVALUE()
        memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))
        ret = self.cam.MV_CC_GetIntValue("PayloadSize", stParam)
        if ret != 0:
            self.logger.info("Set PayloadSize failed.")
            sys.exit()
        self.payload_size = stParam.nCurValue
        self.data_buf = (c_ubyte * self.payload_size)()

        self.data_buf_ref = byref(self.data_buf)
        self.stFrameInfo = MV_FRAME_OUT_INFO_EX()
        memset(byref(self.stFrameInfo), 0, sizeof(self.stFrameInfo))

        ret = self.cam.MV_CC_SetEnumValue("ExposureMode", MV_EXPOSURE_MODE_TIMED)
        if ret != 0:
            self.logger.info("Set exposure mode failed.")
            sys.exit()

        ret = self.cam.MV_CC_SetEnumValue("ExposureAuto", MV_EXPOSURE_AUTO_MODE_OFF)
        if ret != 0:
            self.logger.info("Set exposure auto failed.")
            sys.exit()

        ret = self.cam.MV_CC_SetFloatValue("ExposureTime",float(self.exposureTime)) # us
        if ret != 0:
            self.logger.info("Set exposure time failed.")
            sys.exit()

        ret = self.cam.MV_CC_SetFloatValue("Gain", float(self.gain))
        if ret != 0:
            self.logger.info("Set gain value failed.")
            sys.exit()

        ret = self.cam.MV_CC_SetBoolValue("GammaEnable", True)
        if ret != 0:
            self.logger.info("Set GammaEnable fail!")
	    
        ret = self.cam.MV_CC_SetEnumValue("GammaSelector", 1)
        if ret != 0:
            self.logger.info("Set GammaSelector fail!")

        ret = self.cam.MV_CC_SetFloatValue("Gamma", self.gamma)
        if ret != 0:
            self.logger.info("Set Gamma failed!")

    def start(self):
        ret = self.cam.MV_CC_StartGrabbing()
        if ret != 0:
            self.logger.info("Start Camera failed!")
            sys.exit()

    def get_image(self):
        ret = self.cam.MV_CC_GetOneFrameTimeout(self.data_buf_ref, self.payload_size, self.stFrameInfo, 1000)
        if ret == 0:
            frame_data = np.ctypeslib.as_array(self.data_buf)
            if self.rgb:
                self.image = frame_data.reshape((self.stFrameInfo.nHeight, self.stFrameInfo.nWidth, 3))
                self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
            else:
                self.image = frame_data.reshape((self.stFrameInfo.nHeight, self.stFrameInfo.nWidth))
        else:
            self.logger.info("Get image failed.")
            self.image = None
            self.status = False

    def stop(self):
        ret = self.cam.MV_CC_StopGrabbing()
        if ret != 0:
            self.logger.info("Stop Camera failed!")
            sys.exit()
