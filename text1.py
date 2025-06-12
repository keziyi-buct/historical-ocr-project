import requests
import base64
from langchain_deepseek import ChatDeepSeek
from typing import Dict, Any

# 使用固定的access_token
BAIDU_ACCESS_TOKEN = "24.081096eaf8d4fc4da0e1673c768b1c71.2592000.1751519898.282335-119109042"

def extract_text_from_image(image_path: str) -> Dict[str, Any]:
    """使用百度OCR从图片中提取文字"""
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"
    
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

def format_text_with_deepseek(text: str) -> str:
    """使用DeepSeek对文本进行整理和分段"""
    # 初始化DeepSeek客户端
    llm = ChatDeepSeek(
        model="deepseek-chat",
        api_key="sk-0838692af6684aa082ba0c7249d566cf"
    )
    
    # 构造提示词
    prompt = f"""请帮我将下面的文字整理成易读的格式，划分标点，按照内容逻辑分段，保持原文原字：

{text}

请直接返回整理后的文字，不需要其他解释。"""

    # 获取响应
    response = llm.invoke(prompt)
    return response.content

def main():
    # 1. 指定图片路径
    image_path = 'two.jpg'  # 请确保图片文件存在
    
    try:
        # 2. 提取图片文字
        print("正在进行OCR识别...")
        ocr_result = extract_text_from_image(image_path)
        
        # 3. 处理OCR结果
        raw_text = process_ocr_result(ocr_result)
        if not raw_text:
            print("未能从图片中提取到文字")
            return
            
        print("\n原始提取文字：")
        print("-" * 50)
        print(raw_text)
        print("-" * 50)
        
        # 4. 使用DeepSeek整理文字
        print("\n正在使用DeepSeek整理文字...")
        formatted_text = format_text_with_deepseek(raw_text)
        
        print("\n整理后的文字：")
        print("-" * 50)
        print(formatted_text)
        print("-" * 50)
        
    except Exception as e:
        print(f"处理过程中出现错误：{str(e)}")

if __name__ == "__main__":
    main()