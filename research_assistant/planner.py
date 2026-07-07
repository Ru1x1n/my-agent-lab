import json
from openai import OpenAI
import config

client = OpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.DEEPSEEK_BASE_URL,
    timeout=30.0,      # 超过 30 秒没响应就报超时
    max_retries=0,     # 关掉它自带的重试，用我们自己的 retry
)

def plan(question):
    """把一个复杂问题拆成几个子问题。"""
    prompt = f"""请把下面这个复杂问题，拆解成 2-4 个更小、更具体的子问题，
    以便逐个查资料回答。只输出一个 JSON 数组，例如 ['子问题 1', '子问题 2']，不要有别的文字。

复杂问题: {question}"""

    response = client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content.strip()
    # 模型有时会用 `json` 包裹，去掉它
    text = text.replace("`json`", "").replace("`", "").strip()
    try:
        return json.loads(text)  # 转成 Python 列表
    except Exception:
        return [question]  # 万一解析失败，就当作单个问题处理


def judge_complexity(question):
    """判断问题是简单还是复杂。返回 'simple' 或 'complex'。"""
    prompt = f"""判断下面这个问题是「简单」还是「复杂」。\n
    简单：能一步查到答案的单一问题（如差旅费多少钱）。\n
    复杂：需要对比、综合多个方面、或跨多个主题的问题（如对比 A 和 B 的异同）。\n
    只回答一个词：simple 或 complex，不要有别的回答。

问题: {question}"""

    response = client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    result = response.choices[0].message.content.strip().lower()
    # 兜底：只要包含 complex 就算复杂，否则简单
    return "complex" if "complex" in result else "simple"