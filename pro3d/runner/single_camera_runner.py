'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-20 18:03:37
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-20 18:16:11
FilePath: /BasePipeline/pro3d/runner/single_camera_runner.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
from .base_runner import BaseRunner
from .builder import RUNNERS


@RUNNERS.register_module()
class SingleCameraRunner(BaseRunner):
    pass