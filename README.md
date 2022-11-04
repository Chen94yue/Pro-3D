<!--
 * @Author: chenyue93 chenyue21@jd.com
 * @Date: 2022-11-03 16:10:17
 * @LastEditors: chenyue93 chenyue21@jd.com
 * @LastEditTime: 2022-11-04 10:44:22
 * @FilePath: /Pro-3D/README.md
 * @Description: 
 * 
 * Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
-->
# Pro-3D

[简体中文]() | [English]()

## 简介

Pro-3D是行业第一个通用结构光3D相机成像算法及流程开源工作。该工作将结构光相机3D成像抽象为四大模块，分别为`camera`，`decoder`，`projector`，`rebuilder`，并通过`runner`进行连接，构成整体的成像pipeline。

Pro-3D的组织架构学习借鉴了OpenMMLab搭建的mmcv框架。由于3D成像算法相比于深度学习，Pro-3D对mmcv中的核心组件进行了功能的精简，并针对3D成像任务，增加了一些新的功能。因为整体延续了mmcv优秀的组织架构，Pro-3D具有一下特点：
- 统一可扩展的 io api
- 支持用户扩展丰富的成像算法算子
- 统一的 hook 机制以及可以直接使用的抽象 runner
- 高度灵活的 cfg 模式和注册器机制

此外，Pro-3D将pytorch首次应用于3D成像的解码阶段，将复杂的cuda编程工作简化为简单的pytorch tensor计算，并且能够利用pytorch一键部署至GPU，大大降低了GPU部署的难度。

## 架构说明

