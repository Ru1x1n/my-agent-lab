### 3.1 一次加载整个文件夹的文档

import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader

def load_all_documents(folder):
    all_docs = []
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        try:
            if filename.endswith(".txt"):
                docs = TextLoader(path, encoding="utf-8").load()
            elif filename.endswith(".pdf"):
                docs = PyPDFLoader(path).load()
            else:
                continue
            all_docs.extend(docs)
            print(f"已加载: {filename}")
        except Exception as e:
            print(f"[警告] {filename} 加载失败，已跳过: {e}")
    return all_docs


### 3.2 清洗文档杂质

def clean_text(text):
    """清洗文档里的杂质。"""
    # 去掉一些已知的干扰语句（按你的实际情况补充）
    junk_phrases = ["以下是提取的文字内容：", "--"]
    for junk in junk_phrases:
        text = text.replace(junk, "")
    # 把连续的多个空行压成一个
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)