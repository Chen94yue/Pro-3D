'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-20 10:52:43
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-24 15:40:37
FilePath: /BasePipeline/pro3d/projector/builder.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
from ..utils.registry import Registry, build_from_cfg

PROJECTOR = Registry('projector')


def build_projector(cfg):
    projector = build_from_cfg(cfg, PROJECTOR)
    return projector
