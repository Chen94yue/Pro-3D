'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-11 17:54:41
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-20 10:39:36
FilePath: /BasePipeline/configs/complementary_gray_code_phaseshift/camera.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''

camera = dict(
    type='HikrobotCamera',
    dill_path="C:\Program Files (x86)\Common Files\MVS\Runtime\Win64_x64\MvCameraControl.dll",
    camera_serial='J79613572',
    camera_device_id='2bdf:0001',
    # patterns_number = 22,   # 如果是列表，将在拍摄过程中进行参数的切换
    exposure_time=35000,
    gain=1,
    gamma=1,
    rgb=False,
    log_file='logs/camera.log',
    log_level='INFO'
)
