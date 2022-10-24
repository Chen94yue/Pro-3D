'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-20 19:31:37
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-24 15:41:42
FilePath: /BasePipeline/pro3d/utils/load_calibrate.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
import cv2


def load_calibrate_param(xml_file):
    cv_file = cv2.FileStorage(xml_file, cv2.FILE_STORAGE_READ)
    img_shape = cv_file.getNode("img_shape").mat().astype(int).squeeze()
    rotation = cv_file.getNode("rotation").mat()
    translation = cv_file.getNode("translation").mat()
    cam_int = cv_file.getNode("cam_int").mat()
    cam_dist = cv_file.getNode("cam_dist").mat()
    proj_int = cv_file.getNode("proj_int").mat()
    proj_dist = cv_file.getNode("proj_dist").mat()
    return img_shape, rotation, translation, cam_int, cam_dist, proj_int, proj_dist
