import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from tavily import TavilyClient

load_dotenv()

# 用 ChatOpenAI 对象接入 DeepSeek（因为 DeepSeek 兼容 OpenAI 接口）
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def calculator(expression: str) -> str:
    """计算数学表达式，当用户需要算数时使用。expression 是算式，例如 '135 * 89'。"""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算出错: {e}"

@tool
def get_current_time() -> str:
    """获取当前日期和时间，当用户问现在几点，今天几号时使用。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def web_search(query: str) -> str:
    """联网搜索最新信息。涉及实时、最新信息时使用，query 是搜索关键词。"""
    try:
        response = tavily.search(query=query, max_results=3)
        results = [f"标题: {r['title']}\n 内容: {r['content']}" for r in response["results"]]
        return "\n\n".join(results)
    except Exception as e:
        return f"搜索出错: {e}"

tools=[calculator,get_current_time,web_search]

agent=create_react_agent(llm,tools)

if __name__ == "__main__":
    today = datetime.now().strftime("%Y年%m月%d日")
    questions = [
    "135 乘以 89 等于多少？",
    "现在几点了？",
    "请搜索最新消息，最近有什么重要的 AI 新闻？",
    ]
for q in questions:
    print(f"\n{'='*50}")
    print(f"提问: {q}")
    # 把当前日期放进 system 提示，避免它搜错年份（Day 3 学到的教训）
    result = agent.invoke({
    "messages": [
    ("system", f"今天是 {today}。查最新信息时，搜索词要带上当前年月。"),
    ("user", q),
    ]
    })
    # 最终回答在 messages 列表的最后一条

    print(f"最终回答: {result['messages'][-1].content}")