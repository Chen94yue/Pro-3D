'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-11 17:48:08
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-24 14:55:00
FilePath: /BasePipeline/configs/complementary_gray_code_phaseshift/complementary_gray_code_phaseshift_period10.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
_base_ = [
    './camera.py',
    './projector.py', '../_base_/default_runtime.py'
]

camera_info = dict(
    type = 'Jupiter-S4-12',
    serial = '00000001',
    guid = '00000001',
    producer = 'JDT',
    version = '0.0.1'
)

method = dict(
    decoder = dict(
        type = 'ComplementaryGraycode',
        ps_img_num=3,
        gc_img_num=8,
        bg_thr=4, 
        wavelength=10, 
        downsample_ratio=4,
        col_only=False, 
        cuda=False
    ),
    rebuilder = dict(
        type = 'GraycodeCrossRebuilder',
        calibrate_param_file = "/Users/chenyue/Projects/BasePipeline/calibrate_files/calibration_result_ps_3m.xml", 
        proj_shape = (1140, 912), 
        downsample_ratio = 4,
    ),
    pre_porcess = True,
    pre_process_cfg = dict(
        type = 'ImageCrop',
        crop_x = 0, 
        crop_y = 230,
        crop_w = 2400,
        crop_h = 1730,
        downsample_ratio = 4,
    ),
    post_process = True,
    post_process_cfg = dict(
        type = "RangeFilter",
        min_distance = 1500, # mm
        max_distance = 4500,
    ),
    get_depth = True,
    get_color = False,
    runner = dict(
        type = 'SingleCameraRunner',
    ),
)

