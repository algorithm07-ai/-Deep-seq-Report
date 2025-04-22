import subprocess
import os

def run_evo2(input_fasta: str, output_dir: str) -> dict:
    """
    调用本地evo2命令行进行蛋白质分析。
    input_fasta: 输入的fasta文件路径
    output_dir: evo2输出结果目录
    返回：解析后的evo2结果字典
    """
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        "evo2",  # 确保evo2已在PATH或用绝对路径
        "--input", input_fasta,
        "--output", output_dir
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"evo2 failed: {result.stderr}")
    return parse_evo2_output(output_dir)

def parse_evo2_output(output_dir: str) -> dict:
    """
    解析evo2输出目录下的主要分析结果。
    """
    # 这里只做示例，实际需根据evo2输出文件结构调整
    structure_file = os.path.join(output_dir, "structure.txt")
    annotation_file = os.path.join(output_dir, "annotation.txt")
    structure = open(structure_file).read() if os.path.exists(structure_file) else "N/A"
    annotation = open(annotation_file).read() if os.path.exists(annotation_file) else "N/A"
    return {
        "structure": structure,
        "annotation": annotation,
        "output_dir": output_dir
    }
