"""
PDF Processing Skill

功能：
- PDF 转 CSV
- 提取 PDF 文本
- PDF 表格解析
"""

from pathlib import Path
from typing import List
from langchain_core.tools import tool, BaseTool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from core.base_skill import BaseSkill, SkillMetadata


class PDFProcessingSkill(BaseSkill):
    """PDF 处理 Skill"""

    @property
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="pdf_processing",
            description="PDF 文档处理能力，包括文本提取、表格转换、格式解析等",
            version="1.0.0",
            tags=["pdf", "document", "conversion", "extraction"],
            dependencies=["pdfplumber", "pandas"],
            author="MuyuCheney"
        )

    def get_loader_tool(self) -> BaseTool:
        """返回 Loader Tool"""
        skill_instance = self

        @tool
        def skill_pdf_processing(runtime) -> Command:
            """
            Load PDF processing capabilities.

            Call this tool when you need to:
            - Convert PDF to CSV
            - Extract text from PDF documents
            - Parse tables in PDF files
            """
            instructions = skill_instance.get_instructions()

            return Command(
                update={
                    "messages": [ToolMessage(
                        content=instructions,
                        tool_call_id=runtime.tool_call_id
                    )],
                    "skills_loaded": ["pdf_processing"]
                }
            )

        return skill_pdf_processing

    def get_tools(self) -> List[BaseTool]:
        """返回实际工具"""
        return [
            self._create_pdf_to_csv_tool(),
            self._create_extract_text_tool(),
            self._create_parse_tables_tool()
        ]

    def _create_pdf_to_csv_tool(self) -> BaseTool:
        """创建 PDF 转 CSV 工具"""
        @tool
        def pdf_to_csv(file_path: str) -> str:
            """
            Convert PDF tables to CSV format.

            Args:
                file_path: Path to the PDF file

            Returns:
                CSV formatted string containing extracted table data
            """
            try:
                # 实际实现（需要安装 pdfplumber）
                import pdfplumber
                import pandas as pd
                import io

                rows = []
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        tables = page.extract_tables()
                        for table in tables:
                            rows.extend(table)

                if not rows:
                    return "No tables found in the PDF"

                df = pd.DataFrame(rows[1:], columns=rows[0] if rows else None)
                csv_output = df.to_csv(index=False)

                return f"Successfully converted PDF to CSV:\n```csv\n{csv_output}\n```"

            except ImportError:
                return "Error: pdfplumber or pandas not installed. Install with: pip install pdfplumber pandas"
            except Exception as e:
                return f"Error converting PDF to CSV: {str(e)}"

        return pdf_to_csv

    def _create_extract_text_tool(self) -> BaseTool:
        """创建文本提取工具"""
        @tool
        def extract_pdf_text(file_path: str, page_numbers: str = "all") -> str:
            """
            Extract text content from PDF.

            Args:
                file_path: Path to the PDF file
                page_numbers: Page numbers to extract (e.g., "1,3,5" or "all")

            Returns:
                Extracted text content
            """
            try:
                import pdfplumber

                with pdfplumber.open(file_path) as pdf:
                    if page_numbers == "all":
                        pages_to_extract = range(len(pdf.pages))
                    else:
                        pages_to_extract = [int(p.strip()) - 1 for p in page_numbers.split(",")]

                    text_content = []
                    for i in pages_to_extract:
                        if 0 <= i < len(pdf.pages):
                            page_text = pdf.pages[i].extract_text()
                            text_content.append(f"--- Page {i+1} ---\n{page_text}")

                    result = "\n\n".join(text_content)
                    return f"Extracted text from {len(text_content)} pages:\n\n{result}"

            except ImportError:
                return "Error: pdfplumber not installed. Install with: pip install pdfplumber"
            except Exception as e:
                return f"Error extracting text from PDF: {str(e)}"

        return extract_pdf_text

    def _create_parse_tables_tool(self) -> BaseTool:
        """创建表格解析工具"""
        @tool
        def parse_pdf_tables(file_path: str) -> str:
            """
            Parse and analyze tables in PDF.

            Args:
                file_path: Path to the PDF file

            Returns:
                JSON formatted table data with metadata
            """
            try:
                import pdfplumber
                import json

                tables_data = []

                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        tables = page.extract_tables()
                        for table_num, table in enumerate(tables):
                            tables_data.append({
                                "page": page_num + 1,
                                "table_index": table_num + 1,
                                "rows": len(table),
                                "columns": len(table[0]) if table else 0,
                                "data": table
                            })

                if not tables_data:
                    return "No tables found in the PDF"

                return json.dumps(tables_data, indent=2, ensure_ascii=False)

            except ImportError:
                return "Error: pdfplumber not installed. Install with: pip install pdfplumber"
            except Exception as e:
                return f"Error parsing tables: {str(e)}"

        return parse_pdf_tables


def create_skill(skill_dir: Path) -> BaseSkill:
    """
    工厂函数：创建 Skill 实例

    这是 Registry 自动加载时调用的入口函数
    """
    return PDFProcessingSkill(skill_dir)
