# 清代官员封赏文书信息提取与可视化系统

## 项目概述

本项目通过OCR技术提取清代封赏文书图片中的文字信息，结合大语言模型(DeepSeek)进行结构化处理，最终生成官员品级、地区分布和历史时期等多维度的可视化图表。

## 工作流程

1. **数据提取阶段**
   - `test8.py`: 处理`collect`文件夹中的图片，使用百度OCR提取文字信息.collect文件夹的图片太多了,
   - 通过网盘下载：通过网盘分享的文件：collect.zip
     链接: https://pan.baidu.com/s/1TPFE0lxL4HM4-UPJ6JAZdw 提取码: c5hg
   - 提取官员品级、受封年号、地区等关键信息，存储为`collect.csv`

2. **数据提炼阶段**
   - `extract_data.py`: 从`collect.csv`中提取用于可视化的关键列，生成`collect_new.csv`
   - 使用DeepSeek LLM对数据进行标准化处理，生成`standardized_data.csv`

3. **可视化阶段**
   - `visualize_historical_data.py`: 基于标准化数据生成多种可视化图表
   - 图表保存在`visualization_results`文件夹中

## 测试Demo

1. **单图片处理测试**
   - `text1.py`: 处理单张图片(`two.jpg`)，用于调试和快速测试

2. **网页版处理工具**
   - 解压一下text-ocr-web.zip，然后运行，可在浏览器中上传图片进行处理
   - 提供更简单的交互界面，更加友好

## 环境配置

1. 安装依赖:
```bash
pip install -r requirements.txt
```
环境这里的话，还需要根据自己的电脑配置调整才行
2. 需要配置:
   - 百度OCR API访问权限
   - DeepSeek API密钥
这里说明一下，我放入了自己的，可以直接使用，但是费用不多，同时30天后就过期。
## 使用说明

1. 将待处理的清代封赏文书图片放入`collect`文件夹
2. 按顺序运行:
```bash
python test8.py
python extract_data.py
python visualize_historical_data.py
```
3. 查看`visualization_results`文件夹中的可视化结果

## 文件结构

```
project/
├── collect/               # 原始图片文件夹
├── visualization_results/ # 可视化结果
├── test8.py               # 批量图片处理脚本
├── extract_data.py        # 数据提炼脚本
├── visualize_historical_data.py # 可视化脚本
├── text1.py               # 单图片测试脚本
├── requirements.txt       # 依赖列表
└── README.md             # 本说明文件
```
