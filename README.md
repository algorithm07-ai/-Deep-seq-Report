# DeepSeq-Report

蛋白质功能预测报告生成器 - 一个使用DeepSeek API自动生成蛋白质功能预测结果报告的系统。

## 项目概述

本项目提供了一个使用DeepSeek API自动生成蛋白质功能预测结果报告的系统。系统处理来自evo2工具包的蛋白质序列分析结果，并生成专业的Markdown格式报告。

### 核心功能

- 处理evo2蛋白质序列分析结果
- 生成格式化的Markdown报告
- 支持多种编码（UTF-8、GBK）
- 提供专业的报告结构和格式化
- 安全的API密钥管理
- 蛋白质序列分析功能

## 安装

```bash
# Clone the repository
git clone https://github.com/algorithm07-ai/-Deep-seq-Report.git
cd -Deep-seq-Report

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DeepSeek API key
```

## 使用方法

### 基本用法

```python
from src.report_generator import generate_report

# Generate a report from JSON data
generate_report('path/to/evo2_results.json', 'output_report.md')
```

### 运行功能测试

项目包含一个功能测试脚本，可以用来测试核心功能：

```bash
# Run the test script
python run_test.py
```

测试脚本会：
1. 测试报告生成功能
2. 测试蛋白质序列分析功能
3. 测试错误处理机制

### 蛋白质序列分析

除了报告生成外，DeepSeq-Report还提供蛋白质序列分析功能：

```python
from src.protein_analysis import analyze_sequence

# 分析蛋白质序列
sequence = "MKCPECGKSFSQRANLQRHQRTHTGEK"
results = analyze_sequence(sequence)

# 打印结果
print(f"序列长度: {results['sequence_length']}")
print(f"分子量: {results['molecular_weight']} Da")
```

## 输入格式

系统接受以下JSON格式的输入:

```json
{
  "metadata": {
    "input_file": "string",
    "evo2_model": "string",
    "analysis_type": "string",
    "timestamp": "string",
    "confidence_threshold": number
  },
  "predictions": [
    {
      "protein_id": "string",
      "predicted_go_term": "string",
      "go_term_name": "string",
      "confidence_score": number,
      "notes": "string"
    }
  ]
}
```

## 输出格式

生成的报告采用以下Markdown格式:

```markdown
# evo2 Protein Function Prediction Summary Report

## Executive Summary
[Analysis summary paragraph]

## Key Predictions
- **[Protein_ID]:** Predicted function details...

## Moderate/Low Confidence Notes
- **[Protein_ID]:** Confidence details...

## Methodology
- Technical details...
```

## 文档

- [用户指南](docs/USER_GUIDE.md) - 详细的使用说明和高级功能介绍
- [开发文档](docs/DEVELOPMENT.md) - 为开发者提供的技术细节和贡献指南

## 示例

查看 `examples` 目录中的示例文件，了解输入格式。
查看 `test_output` 目录中的示例结果，了解输出格式。

## 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。 