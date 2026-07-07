# evaluation/evaluate.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from openai import OpenAI
import time
from metrics import metrics


# 关键：让这个文件能 import 到上一层的主项目模块


import config
from loader import load_all_documents, clean_text
from rag import build_knowledge_base, search
from assistant import answer
from testset import test_set
from assistant import answer, deep_research
from agents import research_team
# 裁判用的客户端（复用你的 DeepSeek）
judge_client = OpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.DEEPSEEK_BASE_URL,
)
def llm_judge(question, expected, reply):
    """让模型判断实际回答是否正确。返回 True/False。"""
    prompt = f"""你是一个严格的评分员。请判断「实际回答」是否正确回答了问题。
只要实际回答表达的意思与「标准答案」一致（即使措辞不同），就算正确。
只回答一个词：正确 或 错误。

问题：{question}
标准答案：{expected}
实际回答：{reply}"""

    resp = judge_client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    verdict = resp.choices[0].message.content.strip()
    return "正确" in verdict
# ---------- 指标1：回答准确率 ----------
def evaluate_accuracy(ask_func, mode_name):
    """测准确率，同时统计平均耗时和平均token消耗。"""
    correct = 0
    total_time = 0
    # 记录测试前的 token 累计值
    tokens_before = metrics.total_input + metrics.total_output
    calls_before = metrics.call_count

    for item in test_set:
        start = time.time()
        reply = ask_func(item["question"])
        total_time += time.time() - start

        if llm_judge(item["question"], item["expected"], reply):
            correct += 1

    # 这轮消耗的 token = 测试后 - 测试前
    tokens_used = (metrics.total_input + metrics.total_output) - tokens_before
    calls_used = metrics.call_count - calls_before

    n = len(test_set)
    acc = correct / n
    avg_time = total_time / n
    avg_tokens = tokens_used / n

    print(f"\n【{mode_name}】")
    print(f"  准确率：{acc:.1%}（{correct}/{n}）")
    print(f"  平均耗时：{avg_time:.2f} 秒/题")
    print(f"  平均Token：{avg_tokens:.0f} token/题")
    print(f"  平均调用：{calls_used/n:.1f} 次/题")
    return acc, avg_time, avg_tokens
def judge_retrieval_hit(question, expected, retrieved_text):
    """让模型判断检索内容里是否包含能回答问题的信息。返回 True/False。"""
    prompt = f"""判断下面的「检索内容」里，是否包含能回答问题的信息（与标准答案相关即可）。
只回答一个词：包含 或 不包含。

问题：{question}
标准答案：{expected}
检索内容：{retrieved_text}"""
    resp = judge_client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return "包含" in resp.choices[0].message.content
# ---------- 指标2：检索命中率 ----------
def evaluate_retrieval():
    hit = 0
    for item in test_set:
        docs = search(item["question"])
        combined = " ".join(docs)
        if judge_retrieval_hit(item["question"], item["expected"], combined):  # 用裁判
            hit += 1
    rate = hit / len(test_set)
    print(f"检索命中率（LLM裁判）：{rate:.1%}（{hit}/{len(test_set)}）")
    return rate

# ---------- 参数对比：chunk_size ----------
def compare_chunk_sizes():
    docs_raw = load_all_documents(config.DOCUMENTS_DIR)
    for d in docs_raw:
        d.page_content = clean_text(d.page_content)

    results = {}
    for size in [100, 300, 500, 800]:
        config.CHUNK_SIZE = size
        build_knowledge_base(docs_raw)
        rate = evaluate_retrieval()
        results[size] = rate
        print(f"chunk_size={size} → 命中率 {rate:.1%}\n")
    print("对比结果：", results)
    return results


if __name__ == "__main__":
    # ===== 先建知识库（所有测试的前提）=====
    docs = load_all_documents(config.DOCUMENTS_DIR)
    for d in docs:
        d.page_content = clean_text(d.page_content)
    build_knowledge_base(docs)

    # ===== 1. 检索命中率（用 LLM 裁判）=====
    print("\n" + "=" * 50)
    print("【检索命中率】")
    evaluate_retrieval()

    # ===== 2. 三种模式准确率对比 =====
    print("\n" + "=" * 50)
    print("【三种模式准确率对比】")
    evaluate_accuracy(answer, "普通问答")
    evaluate_accuracy(deep_research, "深度研究")
    evaluate_accuracy(research_team, "多Agent协作")

    # ===== 3. chunk_size 参数对比 =====
    # 注意：这个会重建知识库多次，跑完记得知识库是最后一个 size 的状态
    # print("\n" + "=" * 50)
    # print("【chunk_size 参数对比】")
    # compare_chunk_sizes()

    # ===== 4. 错题分析 =====
    print("\n" + "=" * 50)
    print("【错题分析】")
    for item in test_set:
         reply = answer(item["question"])
         if not llm_judge(item["question"], item["expected"], reply):
             print(f"\n问题：{item['question']}")
             print(f"标准答案：{item['expected']}")
             print(f"实际回答：{reply}")
             docs_found = search(item["question"])
             print(f"检索到：{' | '.join(d[:30] for d in docs_found)}")
             print("-" * 50)