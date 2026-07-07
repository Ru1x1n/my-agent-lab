# rag.py
from zhipuai import ZhipuAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
import config

zhipu = ZhipuAI(api_key=config.ZHIPU_API_KEY)

# 知识库：存每个文档块和它的向量
knowledge_base = []


def embed(text):
    """把文字转成向量。"""
    resp = zhipu.embeddings.create(model=config.EMBED_MODEL, input=text)
    return resp.data[0].embedding


def cosine_similarity(a, b):
    """计算两个向量的相似度。"""
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb)


def build_knowledge_base(documents):
    """把文档切块、向量化，建立知识库。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)
    print(f"文档被切成了 {len(chunks)} 块，正在向量化...")

    knowledge_base.clear()
    for c in chunks:
        vec = embed(c.page_content)
        knowledge_base.append({"text": c.page_content, "vector": vec})
    print(f"知识库就绪，共 {len(knowledge_base)} 块。")


def search(query, k=None):
    """检索最相关的 k 个文档块。"""
    if k is None:
        k = config.TOP_K
    if not knowledge_base:
        return []
    q_vec = embed(query)
    scored = [(cosine_similarity(q_vec, item["vector"]), item["text"])
              for item in knowledge_base]
    scored.sort(reverse=True)
    return [text for score, text in scored[:k]]