import os
from dotenv import load_dotenv
from openai import OpenAI

from zhipuai import ZhipuAI  # 注意：库名可能是 zhipuai，原代码有拼写错误，但按原样保

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# 这个列表就是「短期记忆」——它会累积整场对话
messages = [
    {"role": "system", "content": "你是一个友好的助手。"}
]

def chat(user_input):
    # 1) 把用户这句话加进记忆
    messages.append({"role": "user", "content": user_input})

    # 2) 把「整个记忆」发给模型（关键：带上全部历史）
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )
    reply = response.choices[0].message.content

    # 3) 把模型的回复也加进记忆（这样下一轮它才记得自己说过什么）
    messages.append({"role": "assistant", "content": reply})
    return reply


zhipu = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))

def embed(text):
    resp = zhipu.embeddings.create(model="embedding-3", input=text)
    return resp.data[0].embedding

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb)

# 长期记忆库（每条记忆连同它的向量一起存）
long_term_memory = []

def remember(fact):
    """把一条重要信息存进长期记忆。"""
    long_term_memory.append({"text": fact, "vector": embed(fact)})
    print(f"【记住】{fact}")

def recall(query, k=2):
    """根据当前问题，检索最相关的记忆。"""
    if not long_term_memory:
        return []

    q_vec = embed(query)
    scored = [(cosine_similarity(q_vec, m["vector"]), m["text"]) for m in long_term_memory]
    scored.sort(reverse=True)
    return [text for score, text in scored[:k]]

def chat_with_memory(user_input):
    # 1) 先从长期记忆里回忆相关内容
    memories = recall(user_input, k=2)
    memory_text = "\n".join(memories) if memories else "（暂无相关记忆）"

    # 2) 把回忆到的内容放进 system 提示
    system_prompt = f"你是一个友好的助手。以下是你记得的关于用户的信息：\n{memory_text}"

    msgs = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]
    reply = client.chat.completions.create(model="deepseek-chat", messages=msgs)
    return reply.choices[0].message.content

if __name__ == "__main__":
    # 先手动存几条长期记忆
    remember("用户的名字是小明")
    remember("用户是一名正在学习 AI 的学生")
    remember("用户喜欢喝美式咖啡")

    # 就算是全新的对话（没有短期记忆），它也能靠长期记忆回答
    print(chat_with_memory("我叫什么名字？"))      # 靠长期记忆答出小明
    print(chat_with_memory("推荐一款适合我的饮料"))  # 靠记忆知道他爱美式