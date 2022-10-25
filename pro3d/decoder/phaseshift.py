'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-17 14:37:51
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-24 15:40:29
FilePath: /BasePipeline/pro3d/decoder/phaseshift.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
from .builder import DECODER
import torch
import torch.nn as nn
import math
import numpy as np


@DECODER.register_module()
class Phaseshift(nn.Module):

    def __init__(self, ps_step):
        super(Phaseshift, self).__init__()
        self.ps_step = ps_step

    def get_background(self, pimgs):
        sin_map = pimgs[0] * torch.sin(torch.tensor(2*torch.pi*0/self.ps_step))
        for i in range(1, self.ps_step):
            sin_map += (pimgs[i] * torch.sin(torch.tensor(2*torch.pi*i/self.ps_step)))
        cos_map = pimgs[0] * torch.cos(torch.tensor(2*torch.pi*0/self.ps_step))
        for i in range(1, self.ps_step):
            cos_map += (pimgs[i] * torch.cos(torch.tensor(2*torch.pi*i/self.ps_step)))
        bg = 2 / self.ps_step * torch.sqrt(sin_map**2 + cos_map**2)
        return bg

    def forward(self, pimgs):
        val1 = pimgs[0] * torch.sin(torch.tensor(2*torch.pi*0/self.ps_step))
        for i in range(1, self.ps_step):
            val1 += (pimgs[i] * torch.sin(torch.tensor(2*torch.pi*i/self.ps_step)))

        val2 = pimgs[0] * torch.cos(torch.tensor(2*torch.pi*0/self.ps_step))
        for i in range(1, self.ps_step):
            val2 += (pimgs[i] * torch.cos(torch.tensor(2*torch.pi*i/self.ps_step)))

        return torch.atan2(val1, val2)
