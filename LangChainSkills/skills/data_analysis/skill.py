"""
Data Analysis Skill

功能：
- 统计计算
- 数据可视化
- 数据摘要
"""

from pathlib import Path
from typing import List
from langchain_core.tools import tool, BaseTool
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from core.base_skill import BaseSkill, SkillMetadata


class DataAnalysisSkill(BaseSkill):
    """数据分析 Skill"""

    @property
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="data_analysis",
            description="数据分析和可视化能力，包括统计计算、图表生成、数据摘要等",
            version="1.0.0",
            tags=["data", "statistics", "visualization", "analysis"],
            dependencies=["pandas", "numpy", "matplotlib"],
            author="MuyuCheney"
        )

    def get_loader_tool(self) -> BaseTool:
        """返回 Loader Tool"""
        skill_instance = self

        @tool
        def skill_data_analysis(runtime) -> Command:
            """
            Load data analysis capabilities.

            Call this tool when you need to:
            - Calculate statistics (mean, median, std, etc.)
            - Generate charts and visualizations
            - Summarize and analyze data
            """
            instructions = skill_instance.get_instructions()

            return Command(
                update={
                    "messages": [ToolMessage(
                        content=instructions,
                        tool_call_id=runtime.tool_call_id
                    )],
                    "skills_loaded": ["data_analysis"]
                }
            )

        return skill_data_analysis

    def get_tools(self) -> List[BaseTool]:
        """返回实际工具"""
        return [
            self._create_calculate_statistics_tool(),
            self._create_generate_chart_tool(),
            self._create_data_summary_tool(),
            self._create_correlation_analysis_tool()
        ]

    def _create_calculate_statistics_tool(self) -> BaseTool:
        """创建统计计算工具"""
        @tool
        def calculate_statistics(data: List[float], metrics: str = "all") -> str:
            """
            Calculate statistical metrics for numerical data.

            Args:
                data: List of numerical values
                metrics: Comma-separated metrics to calculate
                        (e.g., "mean,median,std" or "all")

            Returns:
                Statistical results in formatted text
            """
            try:
                import numpy as np
                import json

                if not data:
                    return "Error: Empty data list provided"

                arr = np.array(data)
                results = {}

                all_metrics = ["mean", "median", "std", "var", "min", "max",
                              "q25", "q75", "count"]

                metrics_to_calc = all_metrics if metrics == "all" else [
                    m.strip() for m in metrics.split(",")
                ]

                for metric in metrics_to_calc:
                    if metric == "mean":
                        results["mean"] = float(np.mean(arr))
                    elif metric == "median":
                        results["median"] = float(np.median(arr))
                    elif metric == "std":
                        results["std"] = float(np.std(arr))
                    elif metric == "var":
                        results["variance"] = float(np.var(arr))
                    elif metric == "min":
                        results["min"] = float(np.min(arr))
                    elif metric == "max":
                        results["max"] = float(np.max(arr))
                    elif metric == "q25":
                        results["25th_percentile"] = float(np.percentile(arr, 25))
                    elif metric == "q75":
                        results["75th_percentile"] = float(np.percentile(arr, 75))
                    elif metric == "count":
                        results["count"] = len(arr)

                formatted_output = "Statistical Analysis Results:\n\n"
                for key, value in results.items():
                    formatted_output += f"- {key}: {value:.4f}\n"

                return formatted_output

            except ImportError:
                return "Error: numpy not installed. Install with: pip install numpy"
            except Exception as e:
                return f"Error calculating statistics: {str(e)}"

        return calculate_statistics

    def _create_generate_chart_tool(self) -> BaseTool:
        """创建图表生成工具"""
        @tool
        def generate_chart(
            data: List[float],
            chart_type: str = "line",
            output_path: str = "chart.png",
            title: str = "Data Visualization"
        ) -> str:
            """
            Generate a chart from data.

            Args:
                data: List of numerical values
                chart_type: Type of chart (line, bar, histogram, pie)
                output_path: Path to save the chart image
                title: Chart title

            Returns:
                Success message with chart location
            """
            try:
                import matplotlib.pyplot as plt
                import numpy as np

                if not data:
                    return "Error: Empty data list provided"

                plt.figure(figsize=(10, 6))

                if chart_type == "line":
                    plt.plot(data, marker='o')
                    plt.ylabel("Value")
                    plt.xlabel("Index")
                elif chart_type == "bar":
                    plt.bar(range(len(data)), data)
                    plt.ylabel("Value")
                    plt.xlabel("Index")
                elif chart_type == "histogram":
                    plt.hist(data, bins=20, edgecolor='black')
                    plt.ylabel("Frequency")
                    plt.xlabel("Value")
                elif chart_type == "pie":
                    plt.pie(data, labels=[f"Item {i+1}" for i in range(len(data))],
                           autopct='%1.1f%%')
                else:
                    return f"Error: Unsupported chart type '{chart_type}'. " \
                           f"Use: line, bar, histogram, or pie"

                plt.title(title)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()

                return f"Successfully generated {chart_type} chart: {output_path}"

            except ImportError:
                return "Error: matplotlib not installed. Install with: pip install matplotlib"
            except Exception as e:
                return f"Error generating chart: {str(e)}"

        return generate_chart

    def _create_data_summary_tool(self) -> BaseTool:
        """创建数据摘要工具"""
        @tool
        def summarize_data(data: List[float]) -> str:
            """
            Generate a comprehensive summary of the data.

            Args:
                data: List of numerical values

            Returns:
                Detailed data summary including statistics and insights
            """
            try:
                import numpy as np

                if not data:
                    return "Error: Empty data list provided"

                arr = np.array(data)

                summary = f"""
Data Summary Report
==================

Dataset Size: {len(arr)}

Central Tendency:
- Mean: {np.mean(arr):.4f}
- Median: {np.median(arr):.4f}
- Mode: Not available for continuous data

Spread:
- Standard Deviation: {np.std(arr):.4f}
- Variance: {np.var(arr):.4f}
- Range: {np.max(arr) - np.min(arr):.4f}

Extremes:
- Minimum: {np.min(arr):.4f}
- Maximum: {np.max(arr):.4f}

Quartiles:
- 25th Percentile: {np.percentile(arr, 25):.4f}
- 50th Percentile (Median): {np.percentile(arr, 50):.4f}
- 75th Percentile: {np.percentile(arr, 75):.4f}
- IQR: {np.percentile(arr, 75) - np.percentile(arr, 25):.4f}

Data Quality:
- Missing Values: 0
- Zero Values: {np.sum(arr == 0)}
- Negative Values: {np.sum(arr < 0)}
"""
                return summary

            except ImportError:
                return "Error: numpy not installed. Install with: pip install numpy"
            except Exception as e:
                return f"Error generating summary: {str(e)}"

        return summarize_data

    def _create_correlation_analysis_tool(self) -> BaseTool:
        """创建相关性分析工具"""
        @tool
        def analyze_correlation(data_x: List[float], data_y: List[float]) -> str:
            """
            Analyze correlation between two datasets.

            Args:
                data_x: First dataset
                data_y: Second dataset

            Returns:
                Correlation analysis results
            """
            try:
                import numpy as np

                if len(data_x) != len(data_y):
                    return "Error: Datasets must have the same length"

                if not data_x or not data_y:
                    return "Error: Empty dataset provided"

                arr_x = np.array(data_x)
                arr_y = np.array(data_y)

                correlation = np.corrcoef(arr_x, arr_y)[0, 1]

                # 相关性强度解释
                if abs(correlation) >= 0.9:
                    strength = "Very Strong"
                elif abs(correlation) >= 0.7:
                    strength = "Strong"
                elif abs(correlation) >= 0.5:
                    strength = "Moderate"
                elif abs(correlation) >= 0.3:
                    strength = "Weak"
                else:
                    strength = "Very Weak"

                direction = "Positive" if correlation > 0 else "Negative"

                result = f"""
Correlation Analysis Results
============================

Pearson Correlation Coefficient: {correlation:.4f}

Interpretation:
- Strength: {strength}
- Direction: {direction}

{'The variables show a strong relationship.' if abs(correlation) >= 0.7 else 'The variables show a weak relationship.'}
"""
                return result

            except ImportError:
                return "Error: numpy not installed. Install with: pip install numpy"
            except Exception as e:
                return f"Error analyzing correlation: {str(e)}"

        return analyze_correlation


def create_skill(skill_dir: Path) -> BaseSkill:
    """
    工厂函数：创建 Skill 实例
    """
    return DataAnalysisSkill(skill_dir)
