'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-17 11:23:44
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-18 18:36:05
FilePath: /BasePipeline/pro3d/decoder/builder.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
from ..utils.registry import Registry, build_from_cfg

DECODER = Registry('decoder')


def build_decoder(cfg):
    decoder = build_from_cfg(cfg, DECODER)
    return decoder