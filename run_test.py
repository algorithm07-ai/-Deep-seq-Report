#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
功能测试脚本 - 用于测试DeepSeq-Report的基本功能
"""

import os
import sys
import json
from src.report_generator import generate_report
from src.protein_analysis import analyze_sequence

def main():
    print("DeepSeq-Report 功能测试")
    print("-" * 50)
    
    # 测试目录设置
    test_dir = "test_output"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # 1. 测试报告生成
    print("\n1. 测试报告生成功能")
    try:
        input_file = "examples/sample_input.json"
        output_file = f"{test_dir}/test_report.md"
        
        print(f"  正在从 {input_file} 生成报告...")
        generate_report(input_file, output_file)
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"  ✓ 成功生成报告: {output_file} ({file_size} 字节)")
            
            # 显示报告的前几行
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.readlines()[:10]
                print("\n  报告预览:")
                print("  " + "  ".join(content))
        else:
            print(f"  ✗ 报告生成失败!")
    except Exception as e:
        print(f"  ✗ 报告生成出错: {str(e)}")
    
    # 2. 测试蛋白质分析
    print("\n2. 测试蛋白质序列分析功能")
    try:
        # 示例蛋白质序列
        sequence = "MKCPECGKSFSQRANLQRHQRTHTGEK"
        
        print(f"  分析序列: {sequence}")
        results = analyze_sequence(sequence)
        
        # 保存分析结果
        analysis_file = f"{test_dir}/sequence_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"  ✓ 分析成功，结果保存到: {analysis_file}")
        print(f"  序列长度: {results['sequence_length']}")
        print(f"  分子量: {results['molecular_weight']} Da")
        print(f"  疏水性: {results['physicochemical_properties']['hydrophobic_percent']}%")
        print(f"  二级结构预测: 螺旋 {results['secondary_structure']['helix_fraction'] * 100:.1f}%")
    except Exception as e:
        print(f"  ✗ 序列分析出错: {str(e)}")
    
    # 3. 测试错误处理
    print("\n3. 测试错误处理")
    
    # 3.1 测试无效序列
    print("\n  3.1 测试无效蛋白质序列")
    try:
        invalid_sequence = "ABC123XYZ"
        print(f"  分析无效序列: {invalid_sequence}")
        analyze_sequence(invalid_sequence)
        print("  ✗ 测试失败: 应当引发异常但未发生")
    except ValueError as e:
        print(f"  ✓ 正确处理异常: {str(e)}")
    except Exception as e:
        print(f"  ✗ 意外异常: {str(e)}")
    
    # 3.2 测试无效JSON
    print("\n  3.2 测试无效JSON")
    try:
        # 创建无效JSON文件
        invalid_json = f"{test_dir}/invalid.json"
        with open(invalid_json, 'w') as f:
            f.write("{invalid json")
        
        output_file = f"{test_dir}/invalid_report.md"
        print(f"  处理无效JSON: {invalid_json}")
        generate_report(invalid_json, output_file)
        print("  ✗ 测试失败: 应当引发异常但未发生")
    except json.JSONDecodeError:
        print("  ✓ 正确处理JSON解析异常")
    except Exception as e:
        print(f"  ✗ 意外异常: {str(e)}")
    
    print("\n测试完成!")
    print("-" * 50)

if __name__ == "__main__":
    main() 