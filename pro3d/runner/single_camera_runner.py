'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-20 18:03:37
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-24 14:50:28
FilePath: /BasePipeline/pro3d/runner/single_camera_runner.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
import copy
from .base_runner import BaseRunner
from .builder import RUNNERS
from typing import (Any, Callable, Dict, List, Optional, Tuple, Union,
                    no_type_check)
from .hooks import Hook, HOOKS
from pro3d.utils.registry import build_from_cfg
import logging
import torch


@RUNNERS.register_module()
class SingleCameraRunner(BaseRunner):

    def __init__(self, camera, projector, decoder, rebuilder, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(camera, projector, decoder, rebuilder, logger)
        self.image_number = decoder.num_of_gc_pattern_imgs + decoder.num_of_ps_pattern_imgs
        self.images = []

    def run(self):
        self.images = []
        self.projector.dlp_start()
        self.camera.start()
        for _ in range(self.image_number+1):
            self.camera.get_image()
            self.images.append(self.camera.image.copy())
        color = self.images[-1]
        self.projector.dlp_stop()
        self.camera.stop()
        self.call_hook('pre_processing')
        self.images_tensor = torch.tensor(self.images, dtype=torch.float32)
        if self.decoder.use_cuda:
            self.images_tensor = self.images_tensor.cuda()
        self.map = self.decoder(self.images_tensor)
        if self.decoder.use_cuda:
            self.map = self.map.cpu()
        self.map = self.map.numpy()
        self.points = self.rebuilder.rebuild(self.map)
        self.call_hook('post_processing')
        depth = self.points[:,:,-1]
        return self.points, depth, color
        
    def register_shot_hooks(
        self,
        camera_reset_config: Union[Dict, Hook, None] = None,
        projector_reset_config: Union[Dict, Hook, None] = None,
        pre_process_config: Union[Dict, Hook, None] = None,
        post_process_config: Union[Dict, Hook, None] = None,
    ):
        self.register_camera_reset_hook(camera_reset_config)
        self.register_projector_reset_hook(projector_reset_config)
        self.register_pre_process_hook(pre_process_config)
        self.register_post_process_hook(post_process_config)

    def register_camera_reset_hook(self, camera_reset_config: Union[Dict, Hook, None]):
        if camera_reset_config is None:
            return
        self.logger.info("Not implemented.")

    def register_projector_reset_hook(self, projector_reset_config: Union[Dict, Hook, None]):
        if projector_reset_config is None:
            return 
        self.logger.info("Not implemented.")

    def register_pre_process_hook(self, pre_process_config: Union[Dict, Hook, None]):
        if pre_process_config is None:
            return
        if isinstance(pre_process_config, dict):
            hook = build_from_cfg(pre_process_config, HOOKS)
        else:
            hook = pre_process_config
        self.register_hook(hook, property='NORMAL')

    def register_post_process_hook(self, post_process_config: Union[Dict, Hook, None]):
        if post_process_config is None:
            return
        if isinstance(post_process_config, dict):
            hook = build_from_cfg(post_process_config, HOOKS)
        else:
            hook = post_process_config
        self.register_hook(hook, property='NORMAL')

