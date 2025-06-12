import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.font_manager as fm
import platform

# 检测操作系统并设置合适的中文字体
def setup_chinese_font():
    system = platform.system()
    print(f"当前操作系统: {system}")
    
    # 列出系统中的所有字体
    font_list = [f.name for f in fm.fontManager.ttflist]
    print("系统中可用的字体:")
    chinese_fonts = []
    
    # 检查常见的中文字体
    potential_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'FangSong', 'KaiTi', 'STHeiti', 'STKaiti', 'STSong', 'STFangsong', 'Arial Unicode MS', 'WenQuanYi Micro Hei']
    
    for font in potential_fonts:
        if font in font_list:
            chinese_fonts.append(font)
            print(f"找到中文字体: {font}")
    
    if chinese_fonts:
        # 使用找到的第一个中文字体
        font_name = chinese_fonts[0]
        print(f"使用字体: {font_name}")
        matplotlib.rcParams['font.family'] = font_name
    else:
        print("未找到中文字体，将使用系统默认字体")
        # 尝试使用系统默认字体
        if system == 'Windows':
            matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
        elif system == 'Darwin':  # macOS
            matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'Songti SC']
        else:  # Linux
            matplotlib.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Droid Sans Fallback']
    
    matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 设置中文字体支持
setup_chinese_font()

# 使用matplotlib内置样式而不是seaborn
plt.style.use('ggplot')  # 使用ggplot样式，这是matplotlib内置的一种美观样式

# 创建存储图片的文件夹
os.makedirs('visualization_results', exist_ok=True)

# 读取CSV文件（使用UTF-8编码）
try:
    df = pd.read_csv('standardized_data.csv', encoding='utf-8')
    print("成功读取文件")
except Exception as e:
    print(f"读取文件失败: {e}")
    exit(1)

# 重命名列以便于处理
df.columns = ['品级', '地区', '时期']

# 检查缺失值情况
missing_values = df.isna().sum()
print("\n缺失值统计:")
print(missing_values)
print(f"\n总行数: {len(df)}, 有效数据行数: {len(df.dropna())}")

# 将数字品级转换为文字品级
def convert_to_rank_text(rank):
    rank_dict = {
        1: '一品',
        2: '二品',
        3: '三品',
        4: '四品',
        5: '五品',
        6: '六品',
        7: '七品',
        8: '八品',
        9: '九品'
    }
    return rank_dict.get(rank, str(rank))

# 1. 品级饼图
def create_rank_pie_chart():
    print("正在创建品级饼图...")
    # 将数字品级转换为文字品级
    df['品级文字'] = df['品级'].apply(convert_to_rank_text)
    
    # 按照品级顺序排序（一品到九品）
    rank_order = ['一品', '二品', '三品', '四品', '五品', '六品', '七品', '八品', '九品']
    rank_counts = df['品级文字'].value_counts()
    
    # 按照指定顺序重新排列数据
    ordered_data = []
    ordered_labels = []
    
    for rank in rank_order:
        if rank in rank_counts.index:
            ordered_data.append(rank_counts[rank])
            ordered_labels.append(rank)
    
    # 创建优雅的颜色方案
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(ordered_data)))
    
    # 创建饼图
    plt.figure(figsize=(12, 8), facecolor='white')
    wedges, texts, autotexts = plt.pie(
        ordered_data, 
        labels=ordered_labels, 
        autopct='%d%%',  # 使用整数百分比
        textprops={'fontsize': 12, 'color': '#444444'},
        colors=colors,
        startangle=90,  # 从顶部开始
        shadow=True,    # 添加阴影效果
        wedgeprops={
            'edgecolor': 'white',
            'linewidth': 2,
            'alpha': 0.8
        }
    )
    
    # 添加品级人数标签（整数）
    for i, autotext in enumerate(autotexts):
        autotext.set_text(f'{int(ordered_data[i])}人')
        autotext.set_color('#444444')
    
    plt.title('官员品级分布', fontsize=16, pad=20, color='#333333')
    
    # 添加图例，按品级顺序排列
    plt.legend(
        wedges, 
        [f"{label}（{int(count)}人）" for label, count in zip(ordered_labels, ordered_data)],
        title="品级分布",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        frameon=True,
        facecolor='white',
        edgecolor='#DDDDDD'
    )
    
    plt.tight_layout()
    
    # 保存图片，使用白色背景
    plt.savefig('visualization_results/rank_distribution_pie.png', 
                dpi=300, 
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none')
    print("品级饼图已保存至 visualization_results/rank_distribution_pie.png")
    plt.close()

# 2. 地区分布热力图
def create_region_heatmap():
    print("正在创建地区分布热力图...")
    
    # 统计每个地区的人数（处理多地区情况）
    def count_regions(series):
        region_counts = {}
        for value in series.dropna():
            # 将地区按逗号分割（支持中英文逗号）
            regions = [r.strip() for r in str(value).replace('、', ',').replace('，', ',').split(',')]
            for region in regions:
                if region:  # 确保地区名不为空
                    region_counts[region] = region_counts.get(region, 0) + 1
        return pd.Series(region_counts)

    region_counts = count_regions(df['地区']).sort_values(ascending=False)
    
    # 创建热力图
    plt.figure(figsize=(14, 10), facecolor='white')
    
    # 创建一个表格形式的热力图
    region_data = region_counts.reset_index()
    region_data.columns = ['地区', '人数']
    
    # 添加说明文字
    print("\n注意：对于包含多个地区的记录（如'广东，山西'），每个地区都已被单独计入统计。")
    
    # 将数据重塑为矩阵形式
    n_regions = len(region_data)
    n_cols = 5  # 每行显示5个地区
    n_rows = (n_regions + n_cols - 1) // n_cols
    
    # 创建一个新的图形
    fig, ax = plt.subplots(figsize=(15, 10), facecolor='white')
    ax.axis('off')  # 隐藏坐标轴
    
    # 绘制热力图表格
    cell_width = 1.0 / n_cols
    cell_height = 1.0 / n_rows
    
    # 创建自定义颜色映射
    colors = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c']
    n_bins = 8
    custom_cmap = LinearSegmentedColormap.from_list("custom", colors, N=n_bins)
    
    max_count = max(region_data['人数'])
    
    for i, (_, row) in enumerate(region_data.iterrows()):
        col = i % n_cols
        row_idx = i // n_cols
        
        # 计算单元格位置
        x = col * cell_width
        y = 1.0 - (row_idx + 1) * cell_height
        
        # 计算颜色强度
        intensity = row['人数'] / max_count
        color = custom_cmap(intensity)
        
        # 绘制矩形
        rect = plt.Rectangle(
            (x, y), 
            cell_width, 
            cell_height, 
            facecolor=color,
            edgecolor='#FFFFFF',
            linewidth=2,
            alpha=0.9
        )
        ax.add_patch(rect)
        
        # 添加文本
        plt.text(
            x + cell_width/2, 
            y + cell_height*0.7, 
            f"{row['地区']}", 
            ha='center', 
            va='center', 
            fontsize=12,
            color='#333333',
            fontweight='bold'
        )
        plt.text(
            x + cell_width/2, 
            y + cell_height*0.3, 
            f"{int(row['人数'])}人", 
            ha='center', 
            va='center', 
            fontsize=10,
            color='#666666'
        )
    
    # 添加标题
    plt.title('各地区官员人数分布', fontsize=16, pad=20, color='#333333')
    
    # 添加颜色条
    sm = plt.cm.ScalarMappable(cmap=custom_cmap, norm=plt.Normalize(0, max_count))
    sm.set_array([])
    cbar = plt.colorbar(
        sm, 
        ax=ax, 
        orientation='horizontal',
        fraction=0.05,
        pad=0.05
    )
    cbar.set_label('官员人数', color='#333333')
    
    # 设置颜色条的刻度为整数
    max_count_int = int(max_count)
    ticks = list(range(0, max_count_int + 1))
    if len(ticks) > 10:
        step = max(1, max_count_int // 10)
        ticks = list(range(0, max_count_int + 1, step))
        if max_count_int not in ticks:
            ticks.append(max_count_int)
    
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"{tick}" for tick in ticks])
    
    plt.tight_layout()
    plt.savefig(
        'visualization_results/region_distribution_heatmap.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white',
        edgecolor='none'
    )
    print("地区分布热力图已保存至 visualization_results/region_distribution_heatmap.png")
    plt.close()

# 3. 年号分布柱状图
def create_reign_bar_chart():
    print("正在创建年号分布柱状图...")
    
    # 统计每个年号的人数
    reign_counts = df['时期'].value_counts()
    
    # 定义年号顺序（按照历史顺序）
    # 明代年号
    ming_reigns = ['永乐', '成化', '正德', '嘉靖', '萬曆', '泰昌', '天啓', '崇禎']
    # 清代年号
    qing_reigns = ['順治', '顺治', '康熙', '雍正', '乾隆', '嘉慶', '道光', '咸丰', '同治', '光绪']
    # 合并所有年号按历史顺序
    reign_order = ming_reigns + qing_reigns
    
    # 按照历史顺序重新排列数据
    ordered_reigns = []
    ordered_counts = []
    
    for reign in reign_order:
        if reign in reign_counts:
            ordered_reigns.append(reign)
            ordered_counts.append(int(reign_counts[reign]))
    
    # 创建柱状图
    plt.figure(figsize=(10, 6), facecolor='white')
    
    # 创建渐变色
    colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(ordered_reigns)))
    
    # 绘制柱状图
    bars = plt.bar(
        ordered_reigns, 
        ordered_counts,
        color=colors,
        edgecolor='white',
        linewidth=2,
        alpha=0.8
    )
    
    # 美化图表
    plt.title('清代各年号官员人数分布', fontsize=16, pad=20, color='#333333')
    plt.xlabel('年号', fontsize=14, color='#444444')
    plt.ylabel('人数', fontsize=14, color='#444444')
    
    # 设置背景网格
    plt.grid(True, axis='y', linestyle='--', alpha=0.3)
    
    # 设置y轴为整数刻度
    max_count = max(ordered_counts)
    plt.yticks(range(0, max_count + 1), color='#666666')
    plt.xticks(color='#666666')
    
    # 在柱子上标注具体数值
    for bar in bars:
        height = int(bar.get_height())
        plt.text(
            bar.get_x() + bar.get_width()/2.,
            height,
            f'{height}人',
            ha='center',
            va='bottom',
            color='#333333',
            fontweight='bold'
        )
    
    # 添加轻微的阴影效果
    for bar in bars:
        bar.set_zorder(1)
    ax = plt.gca()
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.savefig(
        'visualization_results/reign_distribution_bar.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white',
        edgecolor='none'
    )
    print("年号分布柱状图已保存至 visualization_results/reign_distribution_bar.png")
    plt.close()

# 4. 地区关联网络图
def create_region_network():
    print("正在创建地区关联网络图...")
    
    # 统计地区共现情况
    region_pairs = []
    for value in df['地区'].dropna():
        regions = [r.strip() for r in str(value).replace('、', ',').replace('，', ',').split(',')]
        if len(regions) > 1:  # 只处理多地区的情况
            for i in range(len(regions)):
                for j in range(i + 1, len(regions)):
                    if regions[i] and regions[j]:  # 确保地区名不为空
                        region_pairs.append(tuple(sorted([regions[i], regions[j]])))
    
    # 统计每对地区共现的次数
    from collections import Counter
    pair_counts = Counter(region_pairs)
    
    if pair_counts:  # 只有在有共现地区时才创建图表
        # 创建网络图
        plt.figure(figsize=(12, 8), facecolor='white')
        
        # 获取所有唯一地区
        unique_regions = set()
        for pair in pair_counts:
            unique_regions.update(pair)
        
        # 计算节点位置（简单圆形布局）
        import math
        n_regions = len(unique_regions)
        angles = np.linspace(0, 2*np.pi, n_regions, endpoint=False)
        radius = 5
        pos = {region: (radius*math.cos(angle), radius*math.sin(angle)) 
               for region, angle in zip(unique_regions, angles)}
        
        # 绘制连线
        max_count = max(pair_counts.values())
        for (region1, region2), count in pair_counts.items():
            x1, y1 = pos[region1]
            x2, y2 = pos[region2]
            width = count / max_count * 3  # 根据共现次数调整线宽
            alpha = count / max_count * 0.8 + 0.2  # 根据共现次数调整透明度
            plt.plot([x1, x2], [y1, y2], '-', color='#4292c6', 
                    linewidth=width, alpha=alpha)
        
        # 绘制节点和标签
        for region, (x, y) in pos.items():
            plt.scatter(x, y, s=200, color='#08519c', alpha=0.6)
            plt.text(x*1.1, y*1.1, region, ha='center', va='center', 
                    fontsize=10, color='#333333')
        
        plt.title('地区关联网络图\n（连线表示地区共同出现，线条粗细表示共现频率）', 
                 fontsize=16, pad=20, color='#333333')
        plt.axis('off')
        plt.tight_layout()
        
        plt.savefig(
            'visualization_results/region_network.png',
            dpi=300,
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none'
        )
        print("地区关联网络图已保存至 visualization_results/region_network.png")
    else:
        print("未发现地区共现情况，跳过创建地区关联网络图")
    
    plt.close()

# 执行所有可视化函数
if __name__ == "__main__":
    print("开始数据可视化...")
    print("\n数据预览:")
    print(df.head())
    print("\n数据统计:")
    print(df.describe())
    
    create_rank_pie_chart()
    create_region_heatmap()
    create_reign_bar_chart()
    create_region_network()  # 添加新的可视化函数
    print("\n所有可视化任务完成！")