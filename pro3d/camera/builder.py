'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-18 18:43:35
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-24 15:38:24
FilePath: /BasePipeline/pro3d/camera/builder.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
from ..utils.registry import Registry, build_from_cfg

CAMERA = Registry('camera')


def build_camera(cfg):
    camera = build_from_cfg(cfg, CAMERA)
    return camera
