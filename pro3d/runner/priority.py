'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-11 14:52:10
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-24 15:41:30
FilePath: /BasePipeline/pro3d/runner/priority.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
# Copyright (c) OpenMMLab. All rights reserved.
from enum import Enum
from typing import Union


class Priority(Enum):
    """Hook priority levels.
    +--------------+------------+
    | Level        | Value      |
    +==============+============+
    | HIGHEST      | 0          |
    +--------------+------------+
    | VERY_HIGH    | 10         |
    +--------------+------------+
    | HIGH         | 30         |
    +--------------+------------+
    | ABOVE_NORMAL | 40         |
    +--------------+------------+
    | NORMAL       | 50         |
    +--------------+------------+
    | BELOW_NORMAL | 60         |
    +--------------+------------+
    | LOW          | 70         |
    +--------------+------------+
    | VERY_LOW     | 90         |
    +--------------+------------+
    | LOWEST       | 100        |
    +--------------+------------+
    """

    HIGHEST = 0
    VERY_HIGH = 10
    HIGH = 30
    ABOVE_NORMAL = 40
    NORMAL = 50
    BELOW_NORMAL = 60
    LOW = 70
    VERY_LOW = 90
    LOWEST = 100


def get_priority(priority: Union[int, str, Priority]) -> int:
    """Get priority value.
    Args:
        priority (int or str or :obj:`Priority`): Priority.
    Returns:
        int: The priority value.
    """
    if isinstance(priority, int):
        if priority < 0 or priority > 100:
            raise ValueError('priority must be between 0 and 100')
        return priority
    elif isinstance(priority, Priority):
        return priority.value
    elif isinstance(priority, str):
        return Priority[priority.upper()].value
    else:
        raise TypeError('priority must be an integer or Priority enum value')
