import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# --- 工具 1：计算器 ---
def calculator(expression: str) -> str:
    """计算一个数学表达式，比如 '135 * 89'。"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算出错: {e}"

# --- 工具 2：查当前时间 ---
def get_current_time() -> str:
    """返回当前的日期和时间。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，当用户需要算数时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的算式，例如 '135 * 89'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期和时间，当用户问现在几点、今天几号时使用",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]


available_tools = {
    "calculator": calculator,
    "get_current_time": get_current_time,
}

def run_tool(name, arguments):
    """根据模型给的名字和参数，执行对应的工具。"""
    func = available_tools.get(name)
    if func is None:
        return f"找不到工具: {name}"
    # arguments 是模型给的 JSON 字符串，先转成字典
    args = json.loads(arguments)
    return func(**args)



# --- Agent 主循环 ---
def run_agent(user_question):
    # messages 会不断累积：问题、模型的决定、工具的结果……
    messages = [
        {"role": "system", "content": "你是一个助手，能使用工具。需要算数或查时间时，调用对应工具。"},
        {"role": "user", "content": user_question},
    ]

    # 最多循环 5 次，防止意外死循环
    for step in range(5):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,  # 把工具清单交给模型
        )

        msg = response.choices[0].message

        # 情况 A：模型没要求用工具 -> 它直接给了答案，结束
        if not msg.tool_calls:
            return msg.content

        # 情况 B：模型要求用工具
        # 先把模型这条「我要用工具」的消息存进历史
        messages.append(msg)

        # 可能一次要用多个工具，逐个执行
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            arguments = tool_call.function.arguments
            print(f"【工具】模型决定调用：{name}，参数：{arguments}")

            result = run_tool(name, arguments)
            print(f"【结果】工具返回: {result}")

            # 把工具结果喂回给模型
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

        # 循环回到开头，模型看到工具结果后继续

    return "（达到最大步数，未能得出最终答案）"

# --- 测试入口 ---
if __name__ == "__main__":
    questions = [
        "你好，你是谁？",                     # 不需要工具
        "135 乘以 89 等于多少？",            # 需要计算器
        "现在几点了？",                     # 需要时间工具
        "现在的分钟数乘以 60 是多少秒？",   # 可能连用两个工具
    ]
    for q in questions:
        print(f"\n{'-'*50}")
        print(f"提问: {q}")
        answer = run_agent(q)
        print(f"最终回答: {answer}")