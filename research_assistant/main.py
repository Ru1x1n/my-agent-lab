# main.py
import time
import config
from loader import load_all_documents, clean_text
from rag import build_knowledge_base
from assistant import answer, deep_research
from memory import ConversationMemory
from graph import app

def main():
    # 1) 加载并清洗文档
    print("正在加载文档...")
    docs = load_all_documents(config.DOCUMENTS_DIR)
    for d in docs:
        d.page_content = clean_text(d.page_content)

    # 2) 建立知识库
    build_knowledge_base(docs)

    # 3) 创建对话记忆
    memory = ConversationMemory(max_turns=10)

    # 4) 选择模式
    print("\n" + "=" * 50)
    print("研究助手就绪！请选择模式：")
    print("  1 = 普通问答（一步检索，速度快）")
    print("  2 = 深度研究（拆解任务，多步推理）")
    mode = input("输入 1 或 2：").strip()

    if mode == "2":
        ask_func = deep_research
        mode_name = "深度研究"
    else:
        ask_func = answer
        mode_name = "普通问答"

    print(f"\n已进入【{mode_name}】模式。")
    print("命令：quit=退出  switch=切换模式  new=清空记忆开始新话题\n")

    # 5) 交互式问答
    while True:
        q = input("\n你的问题：").strip()

        if q.lower() == "quit":
            print("再见！")
            break

        if q.lower() == "switch":
            if ask_func == answer:
                ask_func = deep_research
                mode_name = "深度研究"
            else:
                ask_func = answer
                mode_name = "普通问答"
            print(f"已切换到【{mode_name}】模式。")
            continue

        if q.lower() == "new":
            memory.clear()
            print("已开始新话题，记忆已清空。")
            continue

        if not q:
            continue

        # 计时并回答（两种模式都传入记忆）

        start = time.time()
        try:
            ans = ask_func(q, memory=memory)
            elapsed = time.time() - start
            print(f"\n{'=' * 50}")
            print(f"【{mode_name}】回答：\n{ans}")
            print(f"[耗时 {elapsed:.2f} 秒]")
        except Exception as e:
            print("\n抱歉，处理时出了点问题，请稍后再试。")
            print(f"（错误详情：{e}）")   # 调试用，正式版可删


if __name__ == "__main__":
    main()