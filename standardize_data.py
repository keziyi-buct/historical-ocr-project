from langchain_deepseek import ChatDeepSeek
import csv
import json
import time
import re

def format_with_deepseek(row: dict, max_retries: int = 3) -> dict:
    """使用DeepSeek处理每一行数据"""
    llm = ChatDeepSeek(
        model="deepseek-chat",
        api_key="sk-0838692af6684aa082ba0c7249d566cf"
    )
    
    # 构造提示词
    prompt = f"""请分析以下清代官职品级和地区信息，按照要求进行标准化处理：

原始数据：
品级: {row['品级']}
地区: {row['现代行政区划']}
年号: {row['年号']}

处理要求：
1. 品级转换：
   - 将官职品级转换为1-9的数字（如"一品"转为"1"，"从一品"也转为"1"）
   - 如果出现多个品级，选择最高的一个
   - 如果无法确定具体品级，则留空
   - 示例：
     * "一品"、"正一品"、"从一品" → "1"
     * "二品"、"正二品"、"从二品" → "2"
     * "三品"、"正三品"、"从三品" → "3"
     * 依此类推

2. 地区规范化：
   - 只保留省份或直辖市名称（如"广东"、"北京"）
   - 多个地区用顿号"、"分隔
   - 去掉"省"、"市"、"自治区"等后缀
   - 示例：
     * "山东省" → "山东"
     * "北京市" → "北京"
     * "新疆維吾爾自治區" → "新疆"

请严格按照以下JSON格式返回结果，不要包含任何其他文本：
{{
    "rank": "数字1-9，如果无法确定则留空",
    "region": "规范化后的地区名称，如果无法确定则留空",
    "era": "{row['年号']}"
}}"""

    for attempt in range(max_retries):
        try:
            # 获取响应
            response = llm.invoke(prompt)
            
            # 尝试解析JSON
            try:
                result = json.loads(response.content)
                return result
            except json.JSONDecodeError:
                # 尝试从响应中提取JSON
                match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if match:
                    try:
                        result = json.loads(match.group())
                        return result
                    except json.JSONDecodeError:
                        pass
                
                # 如果这不是最后一次尝试，等待后重试
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    time.sleep(wait_time)
                    continue
                
                # 如果是最后一次尝试，返回空值
                return {
                    "rank": "",
                    "region": "",
                    "era": row['年号']
                }
                
        except Exception as e:
            print(f"处理时出错：{str(e)}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                time.sleep(wait_time)
                continue
            
            return {
                "rank": "",
                "region": "",
                "era": row['年号']
            }

def process_csv():
    """处理CSV文件"""
    input_file = 'collect_new.csv'
    output_file = 'standardized_data.csv'
    
    # 读取输入文件并处理每一行
    processed_rows = []
    total_rows = 0
    
    print("开始读取数据...")
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total_rows = len(rows)
        
        for i, row in enumerate(rows, 1):
            print(f"\n处理第 {i}/{total_rows} 行...")
            result = format_with_deepseek(row)
            processed_rows.append(result)
            print(f"完成第 {i} 行处理")
    
    # 写入输出文件
    print("\n开始写入处理后的数据...")
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # 写入表头
        writer.writerow(['品级', '地区', '年号'])
        
        # 写入数据
        for row in processed_rows:
            writer.writerow([
                row.get('rank', ''),
                row.get('region', ''),
                row.get('era', '')
            ])
    
    print(f"\n处理完成！结果已保存到 {output_file}")
    print(f"共处理 {total_rows} 行数据")

if __name__ == "__main__":
    process_csv()