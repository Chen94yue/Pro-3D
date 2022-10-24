'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-17 11:35:01
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-24 14:32:30
FilePath: /BasePipeline/pro3d/decoder/complementary_graycode.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''


from .builder import DECODER
import torch
import torch.nn as nn
import math
import numpy as np
from .phaseshift import Phaseshift


@DECODER.register_module()
class ComplementaryGraycode(nn.Module):

    def __init__(self,
        ps_img_num,
        gc_img_num,
        bg_thr, 
        wavelength, 
        downsample_ratio,
        col_only=False, 
        cuda=True):
        super(ComplementaryGraycode, self).__init__()
        self.phaseshift_decoder = Phaseshift(ps_img_num)
        self.num_of_ps_imgs = ps_img_num
        self.num_of_gc_imgs = gc_img_num
        self.col_only = col_only
        if self.col_only:
            self.num_of_gc_pattern_imgs = self.num_of_gc_imgs
            self.num_of_ps_pattern_imgs = self.num_of_ps_imgs
        else:
            self.num_of_gc_pattern_imgs = 2*self.num_of_gc_imgs
            self.num_of_ps_pattern_imgs = 2*self.num_of_ps_imgs
        

        self.col_batch_index = torch.tensor([i for i in range(0,self.num_of_gc_imgs)])
        self.col_batch_ratio = torch.tensor([2**(i-1) for i in range(self.num_of_gc_imgs, 0, -1)]).view(-1,1,1)
        if not col_only:
            self.row_batch_index = torch.tensor([i for i in range(self.num_of_gc_imgs, self.num_of_gc_pattern_imgs)])
            self.row_batch_ratio = torch.tensor([2**(i-1) for i in range(self.num_of_gc_imgs, 0, -1)]).view(-1,1,1)

        if cuda:
            self.col_batch_index = self.col_batch_index.cuda()
            self.col_batch_ratio = self.col_batch_ratio.cuda()
            if not col_only:
                self.row_batch_index = self.row_batch_index.cuda()
                self.row_batch_ratio = self.row_batch_ratio.cuda()
        
        self.bg_thr = bg_thr
        self.wavelength = wavelength
        self.dowansample_ratio = downsample_ratio
        self.use_cuda = cuda

    def forward(self, images):
        # decode phaseshift images
        # images = images[:,::self.dowansample_ratio,::self.dowansample_ratio]
        ps_images = images[:self.num_of_ps_pattern_imgs]
        col_bg = self.phaseshift_decoder.get_background(ps_images[:self.num_of_ps_imgs])
        if not self.col_only:
            row_bg = self.phaseshift_decoder.get_background(ps_images[self.num_of_ps_imgs:])
        else:
            row_bg = col_bg
        mask = ((col_bg>self.bg_thr)|(row_bg>self.bg_thr)).int()

        threshold = torch.mean(ps_images, 0)

        ps_col = self.phaseshift_decoder(ps_images[:self.num_of_ps_imgs])
        ps_col[torch.where(ps_col<0)] += torch.pi*2
        if not self.col_only:
            ps_row = self.phaseshift_decoder(ps_images[self.num_of_ps_imgs:])
            ps_row[torch.where(ps_row<0)] += torch.pi*2

        # decode graycode images        
        images = images[self.num_of_ps_pattern_imgs:]
        col_batch_val = images.index_select(0, self.col_batch_index)
        gray_col = torch.gt(col_batch_val, threshold)
        for i in range(1, self.numOfColImgs):
            gray_col[i] = gray_col[i] ^ gray_col[i-1]
        gray_col_k1 = gray_col[:self.numOfColImgs-1]
        gray_col_k2 = gray_col
        dec_col_k1 = torch.sum(gray_col_k1.int() * self.col_batch_ratio[1:], dim=0)
        dec_col_v2 = torch.sum(gray_col_k2.int() * self.col_batch_ratio, dim=0)
        dec_col_k2 = ((dec_col_v2+1)/2).int()
        mask1 = (ps_col <= torch.pi/2).int()
        mask2 = ((torch.pi/2 < ps_col)&(ps_col < 3*torch.pi/2)).int()
        mask3 = (3*torch.pi/2 <= ps_col).int()
        ps_col += 2*torch.pi*dec_col_k2*mask1
        ps_col += 2*torch.pi*dec_col_k1*mask2
        ps_col += (2*torch.pi*dec_col_k2-2*torch.pi)*mask3
        ps_col = (ps_col*mask*self.wavelength/2/torch.pi).unsqueeze(-1)

        if not self.col_only:
            row_batch_val = images.index_select(0, self.row_batch_index)
            gray_row = torch.gt(row_batch_val, threshold)
            for i in range(1, self.numOfRowImgs):
                gray_row[i] = gray_row[i] ^ gray_row[i-1]
            gray_row_k1 = gray_row[:self.numOfColImgs-1]
            gray_row_k2 = gray_row
            dec_row_k1 = torch.sum(gray_row_k1.int() * self.row_batch_ratio[1:], dim=0)
            dec_row_v2 = torch.sum(gray_row_k2.int() * self.row_batch_ratio, dim=0)
            dec_row_k2 = ((dec_row_v2+1)/2).int() 
            mask1 = (ps_row <= torch.pi/2).int()
            mask2 = ((torch.pi/2 < ps_row)&(ps_row < 3*torch.pi/2)).int()
            mask3 = (3*torch.pi/2 <= ps_row).int()
            ps_row += 2*torch.pi*dec_row_k2*mask1
            ps_row += 2*torch.pi*dec_row_k1*mask2
            ps_row += (2*torch.pi*dec_row_k2-2*torch.pi)*mask3
            ps_row = (ps_row*mask*self.wavelength/2/torch.pi).unsqueeze(-1)
        
        if self.col_only:
            map = ps_col
        else:
            map = torch.cat((ps_col, ps_row), dim=2)
        return map