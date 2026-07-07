# assistant.py
from openai import OpenAI
import config
from rag import search
from planner import plan
from utils import retry
from metrics import metrics
from logger import logger
import time


client = OpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.DEEPSEEK_BASE_URL,
    timeout=30.0,
    max_retries=0,
)


# ========== 普通问答（带记忆） ==========
def answer(question, memory=None):
    """基于知识库回答问题，可选带对话记忆。"""
    # 1) RAG 检索
    t0 = time.time()
    docs = search(question)
    t1 = time.time()
    logger.info(f"[计时] 检索耗时 {t1-t0:.2f}s")
    context = "\n".join(docs) if docs else "（没有检索到相关资料）"

    # 2) 组装 messages
    messages = [
        {"role": "system", "content": "你是一个研究助手，根据提供的资料回答问题。"
                                      "如果资料里能推断出答案，请合理推断；"
                                      "只有完全没有相关信息时，才说'资料里没有提到'。"},
    ]
    if memory is not None:
        messages += memory.get()

    user_msg = f"资料：\n{context}\n\n问题：{question}"
    messages.append({"role": "user", "content": user_msg})

    # 3) 调模型
    response = retry(lambda: client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=messages,
    ))
    t2 = time.time()
    logger.info(f"[计时] 模型调用耗时 {t2-t1:.2f}s")
    usage = response.usage
    metrics.add(usage.prompt_tokens, usage.completion_tokens)
    logger.info(f"[Token] 输入 {usage.prompt_tokens}, 输出 {usage.completion_tokens}")
    reply = response.choices[0].message.content

    # 4) 存记忆
    if memory is not None:
        memory.add("user", question)
        memory.add("assistant", reply)

    return reply


# ========== 深度研究（拆解 → 逐个执行 → 汇总） ==========
def deep_research(question, memory=None):
    """面对复杂问题：拆解 -> 逐个回答 -> 汇总。可选带记忆。"""
    # 第一阶段：规划
    sub_questions = plan(question)
    logger.info(f"【规划】把问题拆成了 {len(sub_questions)} 个子问题：")
    for i, sq in enumerate(sub_questions, 1):
        logger.info(f"  {i}. {sq}")

    # 第二阶段：逐个执行
    findings = []
    for sq in sub_questions:
        logger.info(f"【执行】正在研究：{sq}")
        sub_answer = answer(sq)
        findings.append(f"子问题：{sq}\n发现：{sub_answer}")

    # 第三阶段：汇总
    logger.info("【汇总】正在综合所有发现...")
    combined = "\n\n".join(findings)

    messages = [
        {"role": "system", "content": "你是一个研究助手，善于综合分步研究的发现，给出完整有条理的回答。"},
    ]
    if memory is not None:
        messages += memory.get()

    synth_prompt = f"""以下是针对一个复杂问题，分步研究得到的发现。
请综合这些发现，给出一个完整、有条理的最终回答。不要重复啰嗦。

原始问题：{question}

分步发现：
{combined}"""
    messages.append({"role": "user", "content": synth_prompt})

    # 改动：汇总调用也加上 retry + token 统计
    final = retry(lambda: client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=messages,
    ))
    usage = final.usage
    metrics.add(usage.prompt_tokens, usage.completion_tokens)
    logger.info(f"[Token] 汇总 输入 {usage.prompt_tokens}, 输出 {usage.completion_tokens}")
    result = final.choices[0].message.content

    if memory is not None:
        memory.add("user", question)
        memory.add("assistant", result)

    return result