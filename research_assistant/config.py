import os
from dotenv import load_dotenv

load_dotenv()

def get_key(name: str) -> str | None:
    """从 Streamlit Secrets 或环境变量获取密钥，优先 Secrets。"""
    # 尝试从 Streamlit Secrets 读取
    try:
        import streamlit as st
        if hasattr(st, "secrets") and name in st.secrets:
            return st.secrets[name]
    except (ImportError, AttributeError):
        # 没有 streamlit 或 secrets 不存在，忽略
        pass

    # 回退到环境变量
    return os.getenv(name)

# 获取密钥，如果缺失可以给出警告
DEEPSEEK_API_KEY = get_key("DEEPSEEK_API_KEY")
ZHIPU_API_KEY = get_key("ZHIPU_API_KEY")
TAVILY_API_KEY = get_key("TAVILY_API_KEY")

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
CHAT_MODEL = "deepseek-v4-flash"
# 可选：检查必需密钥是否存在
if not DEEPSEEK_API_KEY:
    print("警告: DEEPSEEK_API_KEY 未设置")

# RAG 参数
CHUNK_SIZE = 159
CHUNK_OVERLAP = 30
TOP_K = 4

# 文档目录
import os

# 基于 config.py 的位置定位 documents，不管从哪运行都对
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")