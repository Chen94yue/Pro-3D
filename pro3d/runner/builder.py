'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-11 10:46:49
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-17 11:26:54
FilePath: /BasePipeline/pro3d/runner/builder.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
# Copyright (c) OpenMMLab. All rights reserved.
import copy
from typing import Optional

from ..utils.registry import Registry

RUNNERS = Registry('runner')
RUNNER_BUILDERS = Registry('runner builder')


def build_runner_constructor(cfg: dict):
    return RUNNER_BUILDERS.build(cfg)


def build_runner(cfg: dict, default_args: Optional[dict] = None):
    runner_cfg = copy.deepcopy(cfg)
    constructor_type = runner_cfg.pop('constructor',
                                      'DefaultRunnerConstructor')
    runner_constructor = build_runner_constructor(
        dict(
            type=constructor_type,
            runner_cfg=runner_cfg,
            default_args=default_args))
    runner = runner_constructor()
    return runner