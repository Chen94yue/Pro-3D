'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-18 17:44:24
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-18 17:48:46
FilePath: /BasePipeline/pro3d/decoder/base_module.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
# Copyright (c) OpenMMLab. All rights reserved.
import copy
import warnings
from abc import ABCMeta
from collections import defaultdict
from logging import FileHandler
from typing import Iterable, Optional
from pro3d.utils.logging import get_logger, logger_initialized, print_log

import torch.nn as nn


class BaseModule(nn.Module, metaclass=ABCMeta):
    """Base module for all modules in openmmlab.
    ``BaseModule`` is a wrapper of ``torch.nn.Module`` with additional
    functionality of parameter initialization. Compared with
    ``torch.nn.Module``, ``BaseModule`` mainly adds three attributes.
    - ``init_cfg``: the config to control the initialization.
    - ``init_weights``: The function of parameter initialization and recording
      initialization information.
    - ``_params_init_info``: Used to track the parameter initialization
      information. This attribute only exists during executing the
      ``init_weights``.
    Args:
        init_cfg (dict, optional): Initialization config dict.
    """

    def __init__(self, init_cfg: Optional[dict] = None):
        """Initialize BaseModule, inherited from `torch.nn.Module`"""

        # NOTE init_cfg can be defined in different levels, but init_cfg
        # in low levels has a higher priority.

        super().__init__()
        # define default value of init_cfg instead of hard code
        # in init_weights() function
        self._is_init = False

        self.init_cfg = copy.deepcopy(init_cfg)

        # Backward compatibility in derived classes
        # if pretrained is not None:
        #     warnings.warn('DeprecationWarning: pretrained is a deprecated \
        #         key, please consider using init_cfg')
        #     self.init_cfg = dict(type='Pretrained', checkpoint=pretrained)

    @property
    def is_init(self) -> bool:
        return self._is_init

    def _dump_init_info(self, logger_name: str) -> None:
        """Dump the initialization information to a file named
        `initialization.log.json` in workdir.
        Args:
            logger_name (str): The name of logger.
        """

        logger = get_logger(logger_name)

        with_file_handler = False
        # dump the information to the logger file if there is a `FileHandler`
        for handler in logger.handlers:
            if isinstance(handler, FileHandler):
                handler.stream.write(
                    'Name of parameter - Initialization information\n')
                for name, param in self.named_parameters():
                    handler.stream.write(
                        f'\n{name} - {param.shape}: '
                        f"\n{self._params_init_info[param]['init_info']} \n")
                handler.stream.flush()
                with_file_handler = True
        if not with_file_handler:
            for name, param in self.named_parameters():
                print_log(
                    f'\n{name} - {param.shape}: '
                    f"\n{self._params_init_info[param]['init_info']} \n ",
                    logger=logger_name)

    def __repr__(self):
        s = super().__repr__()
        if self.init_cfg:
            s += f'\ninit_cfg={self.init_cfg}'
        return s
