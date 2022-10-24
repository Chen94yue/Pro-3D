'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-24 11:30:51
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-24 14:50:13
FilePath: /BasePipeline/pro3d/runner/hooks/range_filter.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
from .hook import HOOKS, Hook
import numpy as np

@HOOKS.register_module()
class RangeFilter(Hook):
     
    def __init__(self, min_distance, max_distance):
        self.min_distance = min_distance
        self.max_distance = max_distance
    
    def post_processing(self, runner):
        mask = (runner.points[:,:,2]>self.min_distance)&\
             (runner.points[:,:,2]<self.max_distance)
        mask = np.expand_dims(mask, 2)
        runner.points = runner.points * mask