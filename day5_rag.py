import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from zhipuai import ZhipuAI

load_dotenv()

# 智谱 embedding 客户端
zhipu = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))


def embed(text):
    """把一段文字转成向量。"""
    resp = zhipu.embeddings.create(model="embedding-3", input=text)
    return resp.data[0].embedding


def cosine_similarity(a, b):
    """算两个向量的相似度（余弦相似度）。值越接近 1 越相似。"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b)


# ========== 第一步：准备阶段（读文档 → 切块 → 逐块向量化）==========

# 1) 读取文档
loader = TextLoader("my_doc.txt", encoding="utf-8")
documents = loader.load()

# 2) 切块
splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
chunks = splitter.split_documents(documents)
print(f"文档被切成了 {len(chunks)} 块")

# 3) 把每一块都转成向量，存进一个简单的列表（这就是我们的"向量库"）
print("正在向量化...")
knowledge_base = []
for c in chunks:
    vec = embed(c.page_content)
    knowledge_base.append({"text": c.page_content, "vector": vec})
print("向量化完成，向量库已就绪！")


# ========== 第二步：检索（找出和问题最相似的几块）==========

def search(query, k=2):
    """把问题转成向量，和库里每一块比相似度，返回最像的 k 块。"""
    query_vec = embed(query)
    # 给每一块算一个相似度分数
    scored = []
    for item in knowledge_base:
        score = cosine_similarity(query_vec, item["vector"])
        scored.append((score, item["text"]))
    # 按分数从高到低排序，取前 k 个
    scored.sort(reverse=True)
    return [text for score, text in scored[:k]]


# ========== 第三步：基于检索到的内容回答 ==========

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def ask(question):
    # 1) 检索相关内容
    docs = search(question, k=2)
    context = "\n".join(docs)

    # 2) 拼提示词
    prompt = f"""请根据下面的资料回答问题。如果资料里没有相关信息，就直接说"资料里没有提到"，不要编造。

资料：
{context}

问题：{question}"""

    # 3) 让模型作答
    return llm.invoke(prompt).content


# ========== 测试 ==========
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("【检索测试】")
    query = "差旅费能报多少钱？"
    print(f"问题: {query}")
    print("检索到的相关内容:")
    for i, text in enumerate(search(query, k=2), 1):
        print(f"  [{i}] {text}")

    print("\n" + "=" * 50)
    print("【完整 RAG 问答】")
    for q in ["差旅费能报多少？", "入职两年有几天年假？", "公司在哪个城市？"]:
        print(f"\n问题：{q}")
        print(f"回答：{ask(q)}")