'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-20 18:26:14
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-20 18:27:49
FilePath: /BasePipeline/pro3d/rebuilder/builder.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
from ..utils.registry import Registry, build_from_cfg

REBUILDER = Registry('rebuilder')

def build_rebuilder(cfg):
    rebuilder = build_from_cfg(cfg, REBUILDER)
    return rebuilder