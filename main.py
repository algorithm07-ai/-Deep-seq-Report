from evo2_runner import run_evo2
from report_generator import generate_report
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any
import logging

# 查询GO数据库（示例模板）
def query_go_database(go_term: str):
    """
    查询GO数据库，返回GO术语详细信息。
    实际应用中可调用BioServices、MyGene等API，或本地数据库。
    """
    # TODO: 替换为实际查询逻辑
    return [{"go_id": go_term, "description": "GO术语描述（示例）"}]

# 查询KEGG数据库（示例模板）
def query_kegg_database(protein_id: str):
    """
    查询KEGG数据库，返回相关通路。
    可用Bio.KEGG、bioservices.kegg等Python库，或直接访问REST API。
    """
    # TODO: 替换为实际查询逻辑
    return [f"pathway_{protein_id}_A", f"pathway_{protein_id}_B"]

# 查询PubMed文献（示例模板）
def query_pubmed(query: str):
    """
    查询PubMed，返回相关文献列表。
    可用Entrez（BioPython）、pymed等库。
    """
    # TODO: 替换为实际查询逻辑
    return [
        {"title": f"{query} 相关文献1", "pmid": "123456"},
        {"title": f"{query} 相关文献2", "pmid": "789012"}
    ]

def enrich_protein_prediction(prediction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    为蛋白质预测结果添加生物学上下文（并发优化、异常处理、结构化输出）
    """
    enriched_data = prediction_data.copy()
    proteins = enriched_data.get("predictions", [])

    def enrich_single_protein(protein):
        try:
            go_terms = query_go_database(protein.get("predicted_go_term", ""))
        except Exception as e:
            logging.warning(f"GO查询失败: {e}")
            go_terms = []
        try:
            pathways = query_kegg_database(protein.get("protein_id", ""))
        except Exception as e:
            logging.warning(f"KEGG查询失败: {e}")
            pathways = []
        try:
            publications = query_pubmed(
                f"{protein.get('protein_id', '')} {protein.get('go_term_name', '')}"
            )
        except Exception as e:
            logging.warning(f"PubMed查询失败: {e}")
            publications = []
        protein["go_term_context"] = go_terms
        protein["pathways"] = pathways
        protein["relevant_publications"] = publications
        return protein

    # 并发处理每个蛋白
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_idx = {executor.submit(enrich_single_protein, p): idx for idx, p in enumerate(proteins)}
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                proteins[idx] = future.result()
            except Exception as e:
                logging.error(f"蛋白{idx}注释失败: {e}")

    enriched_data["predictions"] = proteins
    return enriched_data

def main():
    if len(sys.argv) < 3:
        print("用法: python main.py <input_fasta> <output_report.md>")
        sys.exit(1)
    input_fasta = sys.argv[1]
    output_report = sys.argv[2]
    output_dir = "evo2_output"
    # 1. 调用evo2分析
    evo2_result = run_evo2(input_fasta, output_dir)
    # 2. 丰富蛋白预测结果
    enriched_result = enrich_protein_prediction(evo2_result)
    # 3. 生成报告
    report_md = generate_report(enriched_result)
    with open(output_report, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"报告已生成: {output_report}")

if __name__ == "__main__":
    main()
