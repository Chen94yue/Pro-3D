# Copyright (c) OpenMMLab. All rights reserved.
import copy
import logging
import os.path as osp
import warnings
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from typing import (Any, Callable, Dict, List, Optional, Tuple, Union,
                    no_type_check)

from .hooks import HOOKS, Hook
from .log_buffer import LogBuffer
from .priority import Priority, get_priority
from ..utils.path import mkdir_or_exist
from ..utils.registry import build_from_cfg

class BaseRunner(metaclass=ABCMeta):
    def __init__(self,
                 camera,
                 projector,
                 decoder,
                 work_dir: Optional[str] = None,
                 logger: Optional[logging.Logger] = None,
                 ) -> None:
        # check the type of `logger`
        if not isinstance(logger, logging.Logger):
            raise TypeError(f'logger must be a logging.Logger object, '
                            f'but got {type(logger)}')

        self.camera = camera
        self.projector = projector
        self.decoder = decoder
        self.logger = logger
        # create work_dir
        if isinstance(work_dir, str):
            self.work_dir: Optional[str] = osp.abspath(work_dir)
            mkdir_or_exist(self.work_dir)
        elif work_dir is None:
            self.work_dir = None
        else:
            raise TypeError('"work_dir" must be a str or None')

        # get method name from the model class
        self._decoder_name = self.decoder.__class__.__name__
        self._camera_name = self.camera.__class__.__name__
        self._projector_name = self.projector.__class__.__name__
        self.mode: Optional[str] = None
        self._hooks: List[Hook] = []
        self._epoch = 0
        self._iter = 0
        self._inner_iter = 0
        self.log_buffer = LogBuffer()

    @property
    def decoder_name(self) -> str:
        """str: Name of the method, usually the method class name."""
        return self._decoder_name

    @property
    def camera_name(self) -> str:
        """str: Name of the camera."""
        return self._camera_name

    @property
    def projector_name(self) -> str:
        """str: Name of the dlp."""
        return self._dlp_name

    @property
    def hooks(self) -> List[Hook]:
        """list[:obj:`Hook`]: A list of registered hooks."""
        return self._hooks

    @abstractmethod
    def run(self, **kwargs) -> Any:
        pass

    def register_hook(self,
                      hook: Hook,
                      priority: Union[int, str, Priority] = 'NORMAL') -> None:
        """Register a hook into the hook list.
        The hook will be inserted into a priority queue, with the specified
        priority (See :class:`Priority` for details of priorities).
        For hooks with the same priority, they will be triggered in the same
        order as they are registered.
        Args:
            hook (:obj:`Hook`): The hook to be registered.
            priority (int or str or :obj:`Priority`): Hook priority.
                Lower value means higher priority.
        """
        assert isinstance(hook, Hook)
        if hasattr(hook, 'priority'):
            raise ValueError('"priority" is a reserved attribute for hooks')
        priority = get_priority(priority)
        hook.priority = priority  # type: ignore
        # insert the hook to a sorted list
        inserted = False
        for i in range(len(self._hooks) - 1, -1, -1):
            if priority >= self._hooks[i].priority:  # type: ignore
                self._hooks.insert(i + 1, hook)
                inserted = True
                break
        if not inserted:
            self._hooks.insert(0, hook)

    def register_hook_from_cfg(self, hook_cfg: Dict) -> None:
        """Register a hook from its cfg.
        Args:
            hook_cfg (dict): Hook config. It should have at least keys 'type'
              and 'priority' indicating its type and priority.
        Note:
            The specific hook class to register should not use 'type' and
            'priority' arguments during initialization.
        """
        hook_cfg = hook_cfg.copy()
        priority = hook_cfg.pop('priority', 'NORMAL')
        hook = build_from_cfg(hook_cfg, HOOKS)
        self.register_hook(hook, priority=priority)

    def call_hook(self, fn_name: str) -> None:
        """Call all hooks.
        Args:
            fn_name (str): The function name in each hook to be called, such as
                "before_train_epoch".
        """
        for hook in self._hooks:
            getattr(hook, fn_name)(self)

    def get_hook_info(self) -> str:
        # Get hooks info in each stage
        stage_hook_map: Dict[str, list] = {stage: [] for stage in Hook.stages}
        for hook in self.hooks:
            try:
                priority = Priority(hook.priority).name  # type: ignore
            except ValueError:
                priority = hook.priority  # type: ignore
            classname = hook.__class__.__name__
            hook_info = f'({priority:<12}) {classname:<35}'
            for trigger_stage in hook.get_triggered_stages():
                stage_hook_map[trigger_stage].append(hook_info)

        stage_hook_infos = []
        for stage in Hook.stages:
            hook_infos = stage_hook_map[stage]
            if len(hook_infos) > 0:
                info = f'{stage}:\n'
                info += '\n'.join(hook_infos)
                info += '\n -------------------- '
                stage_hook_infos.append(info)
        return '\n'.join(stage_hook_infos)

 