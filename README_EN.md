<!--
 * @Author: chenyue93 chenyue21@jd.com
 * @Date: 2022-11-07 10:48:05
 * @LastEditors: chenyue93 chenyue21@jd.com
 * @LastEditTime: 2022-11-07 15:01:53
 * @FilePath: /Pro-3D/README_EN.md
 * @Description: 
 * 
 * Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
-->
# Pro-3D

[简体中文](https://github.com/Chen94yue/Pro-3D/blob/main/README.md) | [English](https://github.com/Chen94yue/Pro-3D/blob/main/README_EN.md)

## Introduction

Pro-3D is the first structured light 3D camera open source work whit Python. The framework is combined by four parts: `camera`, `decoder`, `projector`, `rebuilder`, which are connected through `runner` to form an overall pipeline.

The organizational of Pro-3D draws on the mmcv framework built by OpenMMLab. Pro-3D has the following characteristics:
- Unified and extensible io api
- Support users to expand rich imaging algorithm operators
- Unified hook mechanism and abstract runner that can be used directly
- Highly flexible cfg schema and registrar mechanism

If you have used any training tools in OpenMMLab, you can quickly get started with Pro-3D

In addition, Pro-3D applies pytorch to the decoding structured image patterns, simplifies the complex cuda programming work into simple pytorch tensor calculation, which greatly reduces the difficulty of GPU deployment.

## Architecture description

The overall framework of Pro-3D is shown in the figure below

![Pro-3D Architecture](https://github.com/Chen94yue/Pro-3D/blob/main/docs/imgs/pro3d.png?raw=true)

- **Modules**:
  - **Camera**: used to control the linked camera, mainly provides dynamic settings of camera shooting parameters, and the function of camera taking pictures.
  - **Projector**: used to control the projector, mainly used to control the projection parameters of the projector and the start and stop of the projection.
  - **Decoder**: Structured light decoding module, used to realize the decoding capability of various structured light.
  - **Rebuilder**: 3D reconstruction module for converting spatial decoding results into 3D point cloud data.

- **Hooks**:
  - **Before Shot**: used to adjust various parameters and indicators before shooting.
  - **Pro-Process**: used to preprocess the acquired raw image data.
  - **Post-Process**: used to post-process the generated point cloud data.

### Usage and extension

Based on the cfg provided by Pro-3D, users can flexibly adjust all parameters of the entire process through configuration files to test the effects of various algorithms and hardware parameter configurations. You only need to specify a specific configuration file when running.

demo:
```shell
python oneshot.py configs/complementary_gray_code_phaseshift/complementary_gray_code_phaseshift_period10.py
````

If you need to add your own Module, the flexible registration mechanism can save you from rebuild the framework. Take connecting a new camera as an example:

- Added new camera SDK files in `third`.
- Add a new camera module in `pro3d/camera`. For the camera control functions that need to be provided, please refer to `pro3d/camera/base_camera.py`