'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-11 17:31:26
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-17 10:59:18
FilePath: /BasePipeline/configs/_base_/default_runtime.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
network_device_name = 'eth0'
camera_service_port = 9001
grpc = dict(
    max_massage_length=100*1024*1024
)
log_level = 'INFO'
log_file = 'logs/default.log'
