import streamlit as st
import config
from loader import load_all_documents, clean_text
from rag import build_knowledge_base
from assistant import answer, deep_research
from agents import research_team

st.set_page_config(page_title="智能研究助手", page_icon="🔍", layout="centered")
st.title("🔍 智能研究助手")
st.caption("基于 RAG 与多智能体协作，能读懂你的文档并深度研究")

# 只在第一次运行时建知识库（缓存起来，避免每次交互都重建）
@st.cache_resource
def init():
    docs = load_all_documents(config.DOCUMENTS_DIR)
    for d in docs:
        d.page_content = clean_text(d.page_content)
    build_knowledge_base(docs)
    return True

init()

# 侧边栏：模式选择
with st.sidebar:
    st.header("⚙️ 设置")
    mode = st.radio("选择模式", ["普通问答", "深度研究", "多Agent协作"])
    st.markdown("---")
    st.markdown("### 关于")
    st.markdown("基于 RAG + 多智能体的研究助手")
    st.markdown("技术栈：Python · LangGraph · DeepSeek")
    if st.button("清空对话"):
        st.session_state.messages = []
        st.rerun()

# 用 session_state 保存聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 输入框 + 生成回答
if prompt := st.chat_input("问我关于文档的任何问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            if mode == "深度研究":
                reply = deep_research(prompt)
            elif mode == "多Agent协作":
                reply = research_team(prompt)
            else:
                reply = answer(prompt)
        st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})



from metrics import metrics

with st.sidebar:
    st.markdown("### 📊 本次会话统计")
    st.metric("调用次数", metrics.call_count)
    st.metric("消耗 Token", metrics.total_input + metrics.total_output)
    st.metric("预估成本", f"{metrics.cost():.4f} 元")