from typing import TypedDict
from langgraph.graph import StateGraph, END
from planner import judge_complexity
from assistant import answer, deep_research

# 定义在图里流转的「状态」
class State(TypedDict):
    question: str  # 用户问题
    complexity: str  # 难易判断结果
    result: str  # 最终答案

# 节点1：判断难易
def route_node(state):
    level = judge_complexity(state["question"])
    print(f"【路由】判断为：{level}")
    return {"complexity": level}

# 节点2：普通问答
def simple_node(state):
    result = answer(state["question"])
    return {"result": result}

# 节点3：深度研究
def complex_node(state):
    result = deep_research(state["question"])
    return {"result": result}


def decide_route(state):
    if state["complexity"] == "complex":
        return "complex"  # 去深度研究节点
    else:
        return "simple"  # 去普通问答节点

## 2.4 把节点和边组装成图

# 创建图
graph = StateGraph(State)

# 加入三个节点
graph.add_node("route", route_node)
graph.add_node("simple", simple_node)
graph.add_node("complex", complex_node)

# 设置入口：先进 route 节点判断
graph.set_entry_point("route")

# 条件边：route 判断后，按 decide_route 的返回值分流
graph.add_conditional_edges("route", decide_route, {
    "simple": "simple",  # 返回 simple → 去 simple 节点
    "complex": "complex",  # 返回 complex → 去 complex 节点
})

# 两个执行节点做完就结束
graph.add_edge("simple", END)
graph.add_edge("complex", END)

# 编译成可运行的应用
app = graph.compile()


if __name__ == "__main__":
    # 先建知识库（关键！之前就是漏了这步）
    import config
    from loader import load_all_documents, clean_text
    from rag import build_knowledge_base

    print("正在加载文档...")
    docs = load_all_documents(config.DOCUMENTS_DIR)
    for d in docs:
        d.page_content = clean_text(d.page_content)
    build_knowledge_base(docs)

    # 测试智能路由
    questions = [
        "差旅费一线城市每天多少钱？",
        "对比研发和市场部门在远程办公和奖金上的差异",
    ]
    for q in questions:
        print(f"\n{'='*50}")
        print(f"问题: {q}")
        result = app.invoke({"question": q})
        print(f"回答: {result['result']}")