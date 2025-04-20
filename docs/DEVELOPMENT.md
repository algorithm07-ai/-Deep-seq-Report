# DeepSeq-Report 开发文档

## 项目概述

DeepSeq-Report 是一个蛋白质功能预测报告生成器，使用 DeepSeek API 自动从蛋白质序列分析结果生成专业报告。本文档提供开发指南和技术细节。

## 系统架构

### 组件构成

1. **Report Generator (`src/report_generator.py`)**
   - 处理JSON数据和生成报告的主脚本
   - 处理文件I/O并支持多种编码
   - 管理API交互

2. **Protein Analysis (`src/protein_analysis.py`)**
   - 处理蛋白质序列的分析功能
   - 提供结构预测和功能注释

3. **API Integration (`src/api_integration.py`)**
   - 处理DeepSeek API集成
   - 实现提示工程
   - 管理API响应处理

4. **实用工具 (`src/utils/`)**
   - `file_io.py`: 文件读写实用工具
   - `formatting.py`: 报告格式化工具

### 数据流

```
[evo2_results.json] → [Report Generator] → [DeepSeek API] → [Markdown Report]
```

## 开发环境设置

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境

```bash
# 创建.env文件
cp .env.example .env
# 编辑.env文件，添加你的API密钥
```

## 编码规范

1. **代码风格**
   - 遵循PEP 8指南
   - 使用有意义的变量名
   - 添加全面的注释

2. **安全性**
   - 不要提交API密钥
   - 使用环境变量存储敏感信息
   - 验证输入数据

3. **错误处理**
   - 实现适当的异常处理
   - 提供清晰的错误消息
   - 记录重要操作

## 测试指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_error_handling.py
```

### 测试类型

1. **功能测试**
   - 报告生成功能
   - 序列分析功能
   - API集成功能

2. **集成测试**
   - 组件间交互
   - 端到端工作流

3. **错误处理测试**
   - 无效输入处理
   - API错误处理
   - 文件I/O错误处理

## 常见问题排查

### 编码错误
- 检查文件编码
- 验证Windows兼容性
- 使用适当的编码处理程序

### API问题
- 验证API密钥
- 检查网络连接
- 验证请求格式

### 输出格式
- 验证Markdown语法
- 检查部分格式化
- 验证内容结构

## 贡献指南

1. Fork仓库
2. 创建功能分支
3. 提交更改并添加测试
4. 创建Pull Request

## 未来计划

1. **增强功能**
   - 批处理支持
   - 其他输出格式
   - 自定义报告模板

2. **性能优化**
   - 缓存机制
   - 并行处理
   - 响应优化

3. **用户界面**
   - 网页界面
   - 命令行参数
   - 配置GUI 