import csv

def extract_columns():
    # 输入和输出文件路径
    input_file = 'collect.csv'
    output_file = 'collect_new.csv'
    
    # 读取原始CSV文件
    rows_to_write = []
    
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # 创建新的CSV文件头
        fieldnames = ['品级', '现代行政区划', '年号']
        rows_to_write.append(fieldnames)
        
        # 处理每一行数据
        for row in reader:
            # 提取需要的列
            rank = row.get('品级', '')
            modern_region = row.get('现代行政区划', '')
            era = row.get('年号', '')
            
            # 添加到输出行
            rows_to_write.append([rank, modern_region, era])
    
    # 写入新的CSV文件
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows_to_write)
    
    print(f"数据已成功提取并保存到 {output_file}")

if __name__ == "__main__":
    extract_columns()