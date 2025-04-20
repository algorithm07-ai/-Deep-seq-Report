# DeepSeq-Report 用户指南

## 简介

DeepSeq-Report 是一个蛋白质功能预测报告生成器，设计用于处理来自 evo2 工具包的蛋白质序列分析结果，并生成格式化的专业报告。本工具使用 DeepSeek API 增强报告内容，提供更深入的蛋白质功能解析。

## 安装

### 前提条件

- Python 3.7 或更高版本
- pip（Python 包管理器）

### 步骤

1. 克隆仓库：
   ```bash
   git clone https://github.com/algorithm07-ai/-Deep-seq-Report.git
   cd -Deep-seq-Report
   ```

2. 安装依赖项：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   ```bash
   cp .env.example .env
   ```
   
4. 编辑 `.env` 文件，添加您的 DeepSeek API 密钥：
   ```
   DEEPSEEK_API_KEY=your_api_key_here
   ```

## 使用方法

### 基本用法

DeepSeq-Report 可以通过两种方式使用：作为 Python 模块导入或通过命令行运行。

#### 作为 Python 模块

```python
from src.report_generator import generate_report

# 生成报告
generate_report('path/to/input.json', 'output_report.md')
```

#### 命令行运行

```bash
python src/report_generator.py input.json output_report.md
```

### 输入格式

DeepSeq-Report 接受 JSON 格式的输入文件，结构如下：

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

### 输出格式

生成的报告是 Markdown 格式，包含以下部分：

- **执行摘要**：分析概览，包括高/中/低置信度预测的数量。
- **关键预测**：高置信度预测的详细列表。
- **中/低置信度说明**：中低置信度预测的备注。
- **方法论**：使用的分析方法和参数的详细信息。

## 高级功能

### 蛋白质序列分析

除了生成报告外，DeepSeq-Report 还提供蛋白质序列分析功能：

```python
from src.protein_analysis import analyze_sequence

# 分析蛋白质序列
sequence = "MKCPECGKSFSQRANLQRHQRTHTGEK"
results = analyze_sequence(sequence)

# 打印结果
print(f"序列长度: {results['sequence_length']}")
print(f"分子量: {results['molecular_weight']} Da")
```

分析结果包括：
- 序列长度和分子量
- 氨基酸组成
- 物理化学特性（疏水性、电荷等）
- 区域识别（疏水区域、带电区域）
- 二级结构预测

### 自定义 API 设置

您可以在 `.env` 文件中自定义 API 设置：

```
DEEPSEEK_API_URL=https://api.deepseek.com/v1/
REQUEST_TIMEOUT=60
```

## 故障排除

### 常见问题

1. **API 密钥错误**
   - 错误信息：`Authentication failed: Invalid API key`
   - 解决方案：检查 `.env` 文件中的 API 密钥是否正确设置

2. **JSON 解析错误**
   - 错误信息：`Invalid JSON format`
   - 解决方案：验证输入 JSON 文件的格式是否正确

3. **编码问题**
   - 症状：报告中出现乱码
   - 解决方案：DeepSeq-Report 会自动检测和处理多种编码，但有时可能需要显式指定编码

### 获取帮助

如果您遇到任何问题或有改进建议，请在 GitHub 仓库创建 Issue：
[https://github.com/algorithm07-ai/-Deep-seq-Report/issues](https://github.com/algorithm07-ai/-Deep-seq-Report/issues)

## 示例

项目包含示例文件，您可以用它们来测试功能：

```bash
# 运行功能测试脚本
python run_test.py

# 处理示例输入
python src/report_generator.py examples/sample_input.json output/example_report.md
```

## 贡献

我们欢迎对项目的贡献！请参阅 [DEVELOPMENT.md](DEVELOPMENT.md) 了解开发指南。 