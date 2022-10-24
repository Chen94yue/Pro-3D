'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-11 16:57:32
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-24 15:42:34
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
from pro3d.rebuilder import build_rebuilder
from pro3d.runner import build_runner


def parse_args():
    parser = argparse.ArgumentParser(
        description=' Get one shot')
    parser.add_argument('config', help='config file path')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    cfg = Config.fromfile(args.config)
    logger = get_logger(name='oneshot', log_file=cfg.log_file,
                        log_level=cfg.log_level)
    logger.info("Get ")
    decoder = build_decoder(cfg.method.decoder)
    camera = build_camera(cfg.camera)
    projector = build_projector(cfg.projector)
    rebuilder = build_rebuilder(cfg.method.rebuilder)
    runner = build_runner(
        cfg.method.runner,
        default_args=dict(
            camera=camera,
            projector=projector,
            decoder=decoder,
            rebuilder=rebuilder,
            logger=logger,
        ))
    if cfg.method.pre_process:
        pre_process_config = cfg.method.pre_process_cfg
    if cfg.method.post_process:
        post_process_config = cfg.method.post_process_cfg
    runner.register_shot_hooks(
        pre_process_config=pre_process_config,
        post_process_config=post_process_config,
    )

    while True:
        points, depth, color = runner.run()
        print(points.shape)
        print(depth.shape)
        print(color.shape)
        input("Next?")


if __name__ == '__main__':
    main()
