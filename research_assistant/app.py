# app.py
import streamlit as st
import tempfile
import os

import config
from loader import load_all_documents, clean_text
from rag import build_knowledge_base
from assistant import answer, deep_research
from agents import research_team
from metrics import metrics
from langchain_community.document_loaders import TextLoader, PyPDFLoader

# ========== 页面配置 ==========
st.set_page_config(page_title="智能研究助手", page_icon="🔍", layout="centered")
st.title("🔍 智能研究助手")
st.caption("基于 RAG 与多智能体协作，能读懂文档并深度研究")


# ========== 预置知识库（启动时加载示例文档）==========
@st.cache_resource
def init_default_kb():
    docs = load_all_documents(config.DOCUMENTS_DIR)
    for d in docs:
        d.page_content = clean_text(d.page_content)
    build_knowledge_base(docs)
    return True

init_default_kb()

# 标记知识库来源（默认用预置的）
if "kb_source" not in st.session_state:
    st.session_state.kb_source = "预置示例文档"


# ========== 处理用户上传的文档 ==========
def build_kb_from_uploads(uploaded_files):
    all_docs = []
    for uf in uploaded_files:
        suffix = ".pdf" if uf.name.lower().endswith(".pdf") else ".txt"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uf.getvalue())
            tmp_path = tmp.name
        try:
            if suffix == ".pdf":
                docs = PyPDFLoader(tmp_path).load()
            else:
                docs = TextLoader(tmp_path, encoding="utf-8").load()
            for d in docs:
                d.page_content = clean_text(d.page_content)
            all_docs.extend(docs)
        finally:
            os.remove(tmp_path)
    build_knowledge_base(all_docs)
    return len(all_docs)


# ========== 侧边栏 ==========
with st.sidebar:
    st.header("⚙️ 设置")
    mode = st.radio("回答模式", ["普通问答", "深度研究", "多Agent协作"])

    st.markdown("---")
    st.header("📄 上传你的文档")
    st.caption("可上传自己的 txt / pdf，构建专属知识库")
    uploaded_files = st.file_uploader(
        "选择文档", type=["txt", "pdf"], accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded_files and st.button("用这些文档建知识库"):
        with st.spinner("正在处理文档..."):
            n = build_kb_from_uploads(uploaded_files)
        st.session_state.kb_source = f"用户上传（{len(uploaded_files)} 个文件）"
        st.session_state.messages = []
        st.success(f"已处理完成，共 {n} 段内容，可以提问了！")

    if st.button("恢复预置文档"):
        init_default_kb.clear()          # 清缓存
        init_default_kb()                # 重新建预置库
        st.session_state.kb_source = "预置示例文档"
        st.session_state.messages = []
        st.success("已恢复预置文档知识库。")

    st.markdown("---")
    st.markdown(f"**当前知识库：** {st.session_state.kb_source}")

    st.markdown("---")
    st.markdown("### 📊 本次会话统计")
    st.metric("模型调用次数", metrics.call_count)
    st.metric("消耗 Token", metrics.total_input + metrics.total_output)
    st.metric("预估成本", f"{metrics.cost():.4f} 元")

    st.markdown("---")
    st.markdown("### 关于")
    st.markdown("基于 RAG + 多智能体的研究助手")
    st.markdown("技术栈：Python · LangGraph · DeepSeek · 智谱")
    if st.button("清空对话"):
        st.session_state.messages = []
        st.rerun()


# ========== 聊天历史 ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# ========== 问答 ==========
if prompt := st.chat_input("问我关于文档的任何问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                if mode == "深度研究":
                    reply = deep_research(prompt)
                elif mode == "多Agent协作":
                    reply = research_team(prompt)
                else:
                    reply = answer(prompt)
            except Exception as e:
                reply = "抱歉，处理时出了点问题，请稍后再试。"
                st.error(f"错误详情：{e}")
        st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})