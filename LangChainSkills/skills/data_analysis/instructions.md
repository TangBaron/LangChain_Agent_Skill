# Data Analysis Skill

数据分析能力已激活！

## 可用工具

### 1. calculate_statistics
计算数据的统计指标。

**使用场景**：
- 快速获取数据概览
- 计算均值、中位数、标准差等
- 数据质���检查

**参数**：
- `data`: 数值列表
- `metrics`: 要计算的指标（"all" 或 "mean,median,std"）

**示例**：
```python
calculate_statistics(
    data=[10, 20, 30, 40, 50],
    metrics="all"
)
```

### 2. generate_chart
生成数据可视化图表。

**使用场景**：
- 数据趋势分析
- 分布可视化
- 报告图表生成

**参数**：
- `data`: 数值列表
- `chart_type`: 图表类型（line, bar, histogram, pie）
- `output_path`: 保存路径
- `title`: 图表标题

**示例**：
```python
generate_chart(
    data=[10, 20, 30, 40, 50],
    chart_type="line",
    output_path="trend.png",
    title="Sales Trend"
)
```

### 3. summarize_data
生成全面的数据摘要报告。

**使用场景**：
- 数据探索分析（EDA）
- 生成统计报告
- 数据质量评估

**参数**：
- `data`: 数值列表

**示例**：
```python
summarize_data(data=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
```

### 4. analyze_correlation
分析两个数据集之间的相关性。

**使用场景**：
- 变量关系分析
- 特征选择
- 预测建模准备

**参数**：
- `data_x`: ��一个数据集
- `data_y`: 第二个数据集

**示例**：
```python
analyze_correlation(
    data_x=[1, 2, 3, 4, 5],
    data_y=[2, 4, 6, 8, 10]
)
```

## 工作流程建议

1. **数据探索阶段**：
   - 先使用 `summarize_data` 获取整体概览
   - 使用 `calculate_statistics` 计算关键指标

2. **数据分析阶段**：
   - 使用 `analyze_correlation` 分析变量关系
   - 使用 `generate_chart` 可视化趋势

3. **报告生成阶段**：
   - 组合使用多个工具生成完整分析报告
   - 导出图表用于展示

## 最佳实践

- **数据清洗**：在分析前确保数据质量
- **合理选择图表**：
  - 趋势分析 → line chart
  - 对比分析 → bar chart
  - 分布分析 → histogram
  - 占比分析 → pie chart
- **结合使用**：统计 + 可视化 = 更好的洞察

## 注意事项

- 需要安装 `numpy`、`matplotlib` 库
- 大数据集建议分批处理
- 图表生成需要有写入权限的目录
