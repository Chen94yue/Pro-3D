'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-11 11:09:59
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-11 14:29:49
FilePath: /BasePipeline/basePipeline/runner/hooks/hook.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
# Copyright (c) OpenMMLab. All rights reserved.
from utils.registry import Registry
from utils.misc import is_method_overridden

HOOKS = Registry('hook')


class Hook:
    stages = ('before_shot', 'get_patterns', 'pre_processing', 'reconstruct',
              'post_processing', 'after_shot')

    def before_shot(self, runner):
        pass

    def get_patterns(self, runner):
        pass

    def pre_processing(self, runner):
        pass

    def reconstruct(self, runner):
        pass

    def post_processing(self, runner):
        pass

    def after_shot(self, runner):
        pass

    def get_triggered_stages(self):
        trigger_stages = set()
        for stage in Hook.stages:
            if is_method_overridden(stage, Hook, self):
                trigger_stages.add(stage)

        return [stage for stage in Hook.stages if stage in trigger_stages]