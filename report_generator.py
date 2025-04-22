from jinja2 import Template
import os

def generate_report(data: dict, template_path: str = None) -> str:
    """
    根据模板和evo2分析结果生成Deep-seq-Report风格报告。
    data: 分析结果字典
    template_path: 模板文件路径，默认为同目录下'report_template.md'
    返回：渲染后的Markdown文本
    """
    if template_path is None:
        template_path = os.path.join(os.path.dirname(__file__), 'report_template.md')
    with open(template_path, encoding='utf-8') as f:
        template = Template(f.read())
    return template.render(**data)
