# agents.py
from openai import OpenAI
import config
from rag import search
from utils import retry
from metrics import metrics
from logger import logger

client = OpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.DEEPSEEK_BASE_URL,
    timeout=30.0,
    max_retries=0,
)


# ========== 检索 Agent ==========
def retrieval_agent(question):
    """检索 Agent：从知识库找相关资料。"""
    docs = search(question, k=5)
    context = "\n\n".join(docs) if docs else "（没有找到相关资料）"
    logger.info("  [检索Agent] 已找到相关资料")
    return context


# ========== 分析 Agent ==========
def analysis_agent(question, context):
    """分析 Agent：分析资料，提炼要点。"""
    prompt = f"""你是一名专业的分析师。请阅读下面的资料，
针对问题提炼出关键要点、数据和它们之间的关联。
只做分析，不用写成完整文章。

问题：{question}
资料：{context}"""
    resp = retry(lambda: client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    ))
    usage = resp.usage
    metrics.add(usage.prompt_tokens, usage.completion_tokens)
    analysis = resp.choices[0].message.content
    logger.info("  [分析Agent] 已完成分析")
    return analysis


# ========== 写作 Agent（可接收审核反馈） ==========
def writing_agent(question, analysis, feedback=""):
    """写作 Agent：把分析组织成清晰的最终答案。可根据审核反馈改进。"""
    feedback_part = f"\n\n上一稿的问题（请改进）：{feedback}" if feedback else ""
    prompt = f"""你是一名优秀的撰稿人。请根据下面的分析，
为用户的问题写一个清晰、有条理、易读的最终回答。{feedback_part}

问题：{question}
分析：{analysis}"""
    resp = retry(lambda: client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    ))
    usage = resp.usage
    metrics.add(usage.prompt_tokens, usage.completion_tokens)
    answer = resp.choices[0].message.content
    logger.info("  [写作Agent] 已完成写作")
    return answer


# ========== 审核 Agent ==========
def review_agent(question, context, answer):
    """审核 Agent：检查答案质量，返回是否合格 + 理由。"""
    prompt = f"""你是一名严格的审核员。请检查下面的「答案」是否合格。
标准：1) 是否忠于资料、没有编造；2) 是否完整回答了问题；3) 是否条理清晰。

如果合格，第一行只回复：PASS
如果不合格，第一行只回复：FAIL，第二行简要说明问题所在。

问题：{question}
资料：{context}
答案：{answer}"""
    resp = retry(lambda: client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    ))
    usage = resp.usage
    metrics.add(usage.prompt_tokens, usage.completion_tokens)
    result = resp.choices[0].message.content.strip()
    passed = result.upper().startswith("PASS")
    logger.info(f"  [审核Agent] {'通过' if passed else '打回：' + result}")
    return passed, result


# ========== 主管：带反馈回环的研究团队 ==========
def research_team(question, memory=None, max_revisions=2):
    """主管：协调多个 Agent 完成研究，带审核-返工的反馈回环。"""
    logger.info(f"【团队启动】{question}")

    # 检索 + 分析
    context = retrieval_agent(question)
    analysis = analysis_agent(question, context)

    # 写作 + 审核 的循环
    feedback = ""
    answer = ""
    for round_num in range(max_revisions + 1):
        answer = writing_agent(question, analysis, feedback)
        passed, review = review_agent(question, context, answer)
        if passed:
            logger.info(f"  [团队] 第 {round_num+1} 稿通过")
            break
        else:
            feedback = review
            logger.info(f"  [团队] 第 {round_num+1} 稿被打回，准备重写")
    else:
        logger.info("  [团队] 达到最大修改次数，返回当前最佳稿")

    logger.info("【团队完成】")

    # 存入记忆（如果传了）
    if memory is not None:
        memory.add("user", question)
        memory.add("assistant", answer)

    return answer


# ========== 单独测试 ==========
if __name__ == "__main__":
    import time
    from loader import load_all_documents, clean_text
    from rag import build_knowledge_base

    docs = load_all_documents(config.DOCUMENTS_DIR)
    for d in docs:
        d.page_content = clean_text(d.page_content)
    build_knowledge_base(docs)

    question = "一个入职2个月的研发新人，能远程办公吗？他的工资是多少？能休年假吗？"

    start = time.time()
    ans = research_team(question)
    elapsed = time.time() - start

    print("=" * 50)
    print("最终答案：")
    print(ans)
    print(f"\n[多 Agent 团队耗时 {elapsed:.2f} 秒]")
    print(metrics.report())   # 打印 token 和成本统计