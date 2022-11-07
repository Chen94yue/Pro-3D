<!--
 * @Author: chenyue93 chenyue21@jd.com
 * @Date: 2022-11-03 16:10:17
 * @LastEditors: chenyue93 chenyue21@jd.com
 * @LastEditTime: 2022-11-07 10:59:38
 * @FilePath: /Pro-3D/README.md
 * @Description: 
 * 
 * Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
-->
# Pro-3D

[简体中文](https://github.com/Chen94yue/Pro-3D/blob/main/README.md) | [English]()

## 简介

Pro-3D是行业第一个通用结构光3D相机成像算法及流程的纯Python环境下的开源工作。该工作将结构光相机3D成像抽象为四大模块，分别为`camera`，`decoder`，`projector`，`rebuilder`，并通过`runner`进行连接，构成整体的成像pipeline。

Pro-3D的组织架构学习借鉴了OpenMMLab搭建的mmcv框架。由于3D成像算法相比于深度学习，Pro-3D对mmcv中的核心组件进行了功能的精简，并针对3D成像任务，增加了一些新的功能。因为整体延续了mmcv优秀的组织架构，Pro-3D具有一下特点：
- 统一可扩展的 io api
- 支持用户扩展丰富的成像算法算子
- 统一的 hook 机制以及可以直接使用的抽象 runner
- 高度灵活的 cfg 模式和注册器机制

如果您使用过OpenMMLab的任何一套训练工具，都能够快速上手Pro-3D

此外，Pro-3D将pytorch首次应用于3D成像的解码阶段，将复杂的cuda编程工作简化为简单的pytorch tensor计算，并且能够利用pytorch一键部署至GPU，大大降低了GPU部署的难度。

## 架构说明

Pro-3D的整体架构如下图所示

![Pro-3D架构](https://github.com/Chen94yue/Pro-3D/blob/main/docs/imgs/pro3d.png?raw=true)

- **Modules**：
  - **Camera**：用于控制链接的相机，主要提供相机拍摄参数的动态设置，和相机拍照取图的功能。
  - **Projector**：用于控制光机，主要用于控制光机的投影参数和投影的开始和关闭。
  - **Decoder**：结构光解码模块，用于实现各种结构光的解码能力。
  - **Rebuilder**：3D重建模块，用于将空间解码结果转化为3D点云数据。

- **Hooks**:
  - **Before Shot**：用于在拍摄前调整各项参数和指标，实现自适应拍摄。
  - **Pro-Process**：用于预处理获取到的原始空间编码图像数据。
  - **Post-Process**：用于后处理生成的点云数据。

### 使用和扩展

基于Pro-3D提供cfg，用户可以灵活的通过配置文件调整整个流程的所有参数以测试各种算法和硬件参数配置的效果。在调用时只需要指定特定的配置文件即可。配置文件的使用和编写方式和mmcv完全一致。

demo：
```shell
python oneshot.py configs/complementary_gray_code_phaseshift/complementary_gray_code_phaseshift_period10.py
```

如果您需要增加自己的Module，灵活的注册机制能够比免您对代理进行重构。以接入一款新的相机为例：

- 在`third`中增加相关相机的SDK文件。
- 在`pro3d/camera`中增加新的camera module，具体需要提供的相机控制功能，参考`pro3d/camera/base_camera.py`




