# PDF Processing Skill

PDF 处理能力已激活！

## 可用工具

### 1. pdf_to_csv
将 PDF 中的表格转换为 CSV 格式。

**使用场景**：
- 提取财务报表
- 转换数据表格
- 导出结构化数据

**参数**：
- `file_path`: PDF 文件路径

**示例**：
```python
pdf_to_csv(file_path="/path/to/report.pdf")
```

### 2. extract_pdf_text
从 PDF 中提取文本内容。

**使用场景**：
- 读取文档内容
- 文本分析
- 信息提取

**参数**：
- `file_path`: PDF 文件路径
- `page_numbers`: 页码（如 "1,3,5" 或 "all"）

**示例**：
```python
extract_pdf_text(file_path="/path/to/document.pdf", page_numbers="all")
```

### 3. parse_pdf_tables
解析并分析 PDF 中的表格结构。

**使用场景**：
- 分析表格布局
- 获取表格元数据
- 结构化数据提取

**参数**：
- `file_path`: PDF 文件路径

**示例**：
```python
parse_pdf_tables(file_path="/path/to/data.pdf")
```

## 最佳实践

1. **先提取后处理**：对于复杂 PDF，先用 `extract_pdf_text` 查看内容
2. **表格优先**：如果 PDF 包含表格，优先使用 `pdf_to_csv` 或 `parse_pdf_tables`
3. **分页处理**：大文件可分页提取以提高性能

## 注意事项

- 需要安装 `pdfplumber` 和 `pandas` 库
- 扫描版 PDF 需要先进行 OCR 处理
- 复杂表格可能需要手动调整提取参数
