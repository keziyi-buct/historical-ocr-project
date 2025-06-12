import requests
import base64
from langchain_deepseek import ChatDeepSeek
from typing import Dict, Any, List
import os
import csv
from pathlib import Path
import time
import json
import re

# 使用固定的access_token
BAIDU_ACCESS_TOKEN = "24.081096eaf8d4fc4da0e1673c768b1c71.2592000.1751519898.282335-119109042"

def extract_text_from_image(image_path: str) -> Dict[str, Any]:
    """使用百度OCR从图片中提取文字"""
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
    
    # 读取图片文件并转为base64
    with open(image_path, 'rb') as f:
        img = base64.b64encode(f.read())

    # 设置请求参数
    params = {"image": img}
    request_url = f"{request_url}?access_token={BAIDU_ACCESS_TOKEN}"
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    # 发送OCR请求
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        return response.json()
    raise Exception("OCR识别失败")

def process_ocr_result(ocr_result: Dict[str, Any]) -> str:
    """处理OCR结果，提取所有文字内容"""
    if 'words_result' not in ocr_result:
        return ""
    
    # 提取所有识别出的文字
    text = ""
    for word in ocr_result['words_result']:
        if 'words' in word:
            text += word['words'] + "\n"
    return text.strip()

def extract_json_from_text(text: str) -> Dict[str, str]:
    """从文本中提取JSON对象"""
    # 查找文本中的JSON对象（在第一个{和最后一个}之间的内容）
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            # 尝试解析找到的JSON字符串
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None

def format_text_with_deepseek(text: str, max_retries: int = 3) -> Dict[str, str]:
    """使用DeepSeek对文本进行分析，提取多个维度的信息"""
    # 初始化DeepSeek客户端
    llm = ChatDeepSeek(
        model="deepseek-chat",
        api_key="sk-0838692af6684aa082ba0c7249d566cf"
    )
    
    # 构造提示词
    prompt = f"""请分析以下清代封赏文书的内容，提取关键信息并按照要求整理原文。
如果某些信息无法确定，请将对应项留空。请提供以下信息：

1. 封赏对象（被封赏的人名）
2. 具体的封赏时间（年月日）
3. 年号（如康熙、雍正、乾隆等）
4. 相关地区（官员的管辖地区或可能长期驻留的地区）
5. 现代行政区划（将古代地区对应到现代省份名称，如广东、江苏、浙江等）
6. 官职品级（一品到九品，如果能确定具体品级请标注）
7. 整理后的原文（按现代标点符号分段，保持原文字不变）

原文内容如下：

{text}

请严格按照以下JSON格式返回结果，不要包含任何其他文本：
{{
    "person": "封赏对象姓名",
    "date": "具体封赏时间",
    "era": "年号",
    "region": "相关地区",
    "modern_region": "现代省份名称",
    "rank": "品级",
    "text": "整理后的原文"
}}"""

    for attempt in range(max_retries):
        try:
            # 获取响应
            print(f"正在尝试第 {attempt + 1} 次解析...")
            response = llm.invoke(prompt)
            
            # 打印原始响应以便调试
            print(f"DeepSeek原始响应：\n{response.content}\n")
            
            # 首先尝试直接解析JSON
            try:
                result = json.loads(response.content)
                print("成功解析JSON响应")
                return result
            except json.JSONDecodeError:
                print("直接JSON解析失败，尝试从文本中提取JSON...")
                
                # 尝试从响应中提取JSON
                result = extract_json_from_text(response.content)
                if result:
                    print("成功从文本中提取JSON")
                    return result
                
                # 如果这不是最后一次尝试，等待后重试
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 递增等待时间
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                # 如果是最后一次尝试，返回空值字典
                print("所有解析尝试都失败")
                return {
                    "person": "",
                    "date": "",
                    "era": "",
                    "region": "",
                    "modern_region": "",
                    "rank": "",
                    "text": text  # 保留原文
                }
                
        except Exception as e:
            print(f"DeepSeek处理过程中出错：{str(e)}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            
            return {
                "person": "",
                "date": "",
                "era": "",
                "region": "",
                "modern_region": "",
                "rank": "",
                "text": text  # 如果处理失败，至少返回原文
            }

def process_folder(folder_path: str) -> Dict[str, str]:
    """处理单个文件夹中的所有图片"""
    # 获取文件夹中的所有png文件并按数字排序
    image_files = sorted(
        [f for f in os.listdir(folder_path) if f.endswith('.png')],
        key=lambda x: int(x.split('.')[0])
    )
    
    if not image_files:
        print(f"警告：文件夹 {folder_path} 中没有找到png图片")
        return {
            "person": "",
            "date": "",
            "era": "",
            "region": "",
            "modern_region": "",
            "rank": "",
            "text": ""
        }
    
    # 存储所有图片的文字内容
    all_text = []
    
    # 处理每张图片
    for img_file in image_files:
        img_path = os.path.join(folder_path, img_file)
        print(f"正在处理图片：{img_path}")
        
        try:
            # OCR识别
            ocr_result = extract_text_from_image(img_path)
            # 处理OCR结果
            text = process_ocr_result(ocr_result)
            if text:
                all_text.append(text)
        except Exception as e:
            print(f"处理图片 {img_path} 时出错：{str(e)}")
    
    # 合并所有文字
    combined_text = "\n".join(all_text)
    
    if not combined_text:
        return {
            "person": "",
            "date": "",
            "era": "",
            "region": "",
            "modern_region": "",
            "rank": "",
            "text": ""
        }
    
    # 使用DeepSeek处理合并后的文字
    try:
        result = format_text_with_deepseek(combined_text)
        print(f"Deepseek已完成文字分析")
        return result
    except Exception as e:
        print(f"DeepSeek处理文件夹 {folder_path} 的文字时出错：{str(e)}")
        return {
            "person": "",
            "date": "",
            "era": "",
            "region": "",
            "modern_region": "",
            "rank": "",
            "text": combined_text
        }

def append_to_csv(file_path: str, folder_name: str, result: Dict[str, str]):
    """将处理结果追加到CSV文件"""
    # 检查文件是否存在
    file_exists = os.path.exists(file_path)
    
    # 以追加模式打开文件
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # 如果文件不存在，写入表头
        if not file_exists:
            writer.writerow(['文件夹', '封赏对象', '封赏时间', '年号', '地区', '现代行政区划', '品级', '原文'])
        
        # 写入数据行
        writer.writerow([
            folder_name,
            result.get('person', ''),
            result.get('date', ''),
            result.get('era', ''),
            result.get('region', ''),
            result.get('modern_region', ''),
            result.get('rank', ''),
            result.get('text', '')
        ])

def main():
    # 基础路径
    collect_dir = "collect"
    output_file = 'collect.csv'
    
    # 确保collect文件夹存在
    if not os.path.exists(collect_dir):
        print(f"错误：找不到 {collect_dir} 文件夹")
        return
    
    # 获取所有子文件夹并按数字排序
    subfolders = sorted(
        [f for f in os.listdir(collect_dir) if os.path.isdir(os.path.join(collect_dir, f))],
        key=lambda x: int(x)
    )
    
    if not subfolders:
        print(f"警告：{collect_dir} 文件夹中没有找到子文件夹")
        return
    
    # 如果输出文件已存在，先删除它
    if os.path.exists(output_file):
        os.remove(output_file)
    
    # 处理每个子文件夹
    for folder in subfolders:
        folder_path = os.path.join(collect_dir, folder)
        print(f"\n正在处理文件夹：{folder_path}")
        
        try:
            # 处理文件夹中的所有图片
            result = process_folder(folder_path)
            
            # 立即将结果追加到CSV文件
            append_to_csv(output_file, folder, result)
            
            print(f"文件夹 {folder} 的处理结果已保存")
            
        except Exception as e:
            print(f"处理文件夹 {folder} 时出错：{str(e)}")
            # 即使出错，也将错误信息写入CSV
            append_to_csv(output_file, folder, {
                "person": "",
                "date": "",
                "era": "",
                "region": "",
                "modern_region": "",
                "rank": "",
                "text": f"处理出错：{str(e)}"
            })
    
    print("\n所有处理完成！结果已保存到 collect.csv 文件中")

if __name__ == "__main__":
    main()