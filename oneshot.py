'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-11 16:57:32
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-20 16:52:23
FilePath: /BasePipeline/oneshot.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
import argparse
from pro3d.utils.configs import Config
from pro3d.utils.logging import get_logger
from pro3d.decoder import build_decoder
from pro3d.camera import build_camera
from pro3d.projector import build_projector

def parse_args():
    parser = argparse.ArgumentParser(
        description=' Get one shot')
    parser.add_argument('config', help='config file path')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    cfg = Config.fromfile(args.config)
    logger = get_logger(name='oneshot', log_file=cfg.log_file, log_level=cfg.log_level)
    logger.info("Get ")
    decoder = build_decoder(cfg.method.decoder)
    # camera = build_camera(cfg.camera)
    projector = build_projector(cfg.projector)
    print(projector)

if __name__ == '__main__':
    main()