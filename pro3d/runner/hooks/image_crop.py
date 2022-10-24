'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-24 11:29:40
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-24 14:29:12
FilePath: /BasePipeline/pro3d/runner/hooks/image_crop.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
from .hook import HOOKS, Hook
import numpy as np

@HOOKS.register_module()
class ImageCrop(Hook):

    def __init__(self, crop_x, crop_y, crop_w, crop_h, downsample_ratio=1):
        self.crop_x = crop_x
        self.crop_y = crop_y
        self.crop_w = crop_w
        self.crop_h = crop_h
        self.downsample_ratio = downsample_ratio

    def pre_processing(self, runner):
        images = runner.images
        images = np.array(images)
        images = images[:, self.crop_y:self.crop_y+self.crop_h, self.crop_x:self.crop_x+self.crop_w]
        images = images[:, ::self.downsample_ratio, ::self.downsample_ratio]
        runner.images = images
