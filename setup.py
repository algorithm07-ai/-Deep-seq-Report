from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="deep-seq-report",
    version="0.1.0",
    author="algorithm07-ai",
    author_email="1459351107@qq.com",
    description="蛋白质功能预测报告生成器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/algorithm07-ai/-Deep-seq-Report",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "deepseek-api>=1.0.0",
        "python-dotenv>=0.19.0",
        "requests>=2.26.0",
        "markdown>=3.3.0",
        "chardet>=4.0.0",
    ],
) 