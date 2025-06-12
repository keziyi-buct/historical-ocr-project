import pandas as pd
import numpy as np
from textwrap import fill

def view_csv_content():
    # 读取CSV文件
    try:
        df = pd.read_csv('collect.csv')
        
        # 显示基本信息
        print("\n=== CSV文件基本信息 ===")
        print(f"总行数: {len(df)}")
        print(f"总列数: {len(df.columns)}")
        print(f"列名: {', '.join(df.columns)}")
        
        # 显示缺失值统计
        print("\n=== 缺失值统计 ===")
        missing_stats = df.isnull().sum()
        for column, missing_count in missing_stats.items():
            print(f"{column}: {missing_count} 个缺失值")
        
        # 显示每行详细内容
        print("\n=== 详细内容 ===")
        for index, row in df.iterrows():
            print(f"\n--- 第{index + 1}行（文件夹：{row['文件夹']}） ---")
            
            # 显示除原文外的其他字段
            other_fields = [col for col in df.columns if col != '原文']
            for field in other_fields:
                value = row[field]
                if pd.isna(value):
                    print(f"{field}: [空]")
                else:
                    print(f"{field}: {value}")
            
            # 显示原文（如果存在）
            if pd.notna(row['原文']):
                print("\n原文:")
                # 将原文按照80个字符宽度重新格式化，保持中文完整性
                formatted_text = fill(str(row['原文']), width=80, break_long_words=False, break_on_hyphens=False)
                print(formatted_text)
            else:
                print("\n原文: [空]")
            
            print("-" * 80)  # 分隔线
        
        # 显示简单统计
        print("\n=== 统计信息 ===")
        # 统计非空年号的分布
        era_counts = df['年号'].value_counts()
        if not era_counts.empty:
            print("\n年号分布:")
            print(era_counts)
        
        # 统计非空品级的分布
        rank_counts = df['品级'].value_counts()
        if not rank_counts.empty:
            print("\n品级分布:")
            print(rank_counts)
        
        # 统计非空地区的分布
        region_counts = df['地区'].value_counts()
        if not region_counts.empty:
            print("\n地区分布:")
            print(region_counts)
            
    except FileNotFoundError:
        print("错误：找不到collect.csv文件")
    except Exception as e:
        print(f"发生错误：{str(e)}")

if __name__ == "__main__":
    view_csv_content()