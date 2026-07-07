🔍 智能研究助手（Intelligent Research Assistant）


一个基于 RAG 与多智能体协作的研究型问答系统，能读懂用户文档、拆解复杂问题、多 Agent 分工协作并自我审核修正。



🌐 在线 Demo：https://my-agent-lab-cargxkbtdrri8houpxbdey.streamlit.app/ |　💻 源码： 本仓库


📖 项目简介

这是一个面向「文档研究」场景的智能助手。用户上传自己的文档（或使用预置示例），即可就文档内容进行提问。系统不仅能做基础的检索问答，还能针对复杂问题自动拆解、调度多个专职 Agent 协作完成研究，并通过审核机制自我修正，降低幻觉与遗漏。

项目从零构建，涵盖了现代 AI Agent 开发的核心技术栈：检索增强生成（RAG）、任务规划、多智能体协作、反馈回环、错误处理、可观测性与系统评测。


✨ 核心功能


📚 文档问答（RAG）：支持 txt / pdf 文档，向量化后基于语义检索作答
🧩 任务拆解：复杂问题自动拆解为子问题，逐个研究再综合
🚦 智能路由：自动判断问题难易，简单直答、复杂深挖，兼顾效率与质量
🤝 多 Agent 协作：检索、分析、写作三个专职 Agent 流水线协作
✅ 自我审核修正：审核 Agent 对答案把关，不合格自动打回重写（Reflection）
🧠 对话记忆：支持多轮连贯追问
🛡️ 稳定性保障：API 重试、超时控制、错误兜底
📊 可观测性：日志、Token 消耗与成本统计、分段计时
🌐 Web 界面：Streamlit 网页，支持文档上传、模式切换、实时统计



🏗️ 技术架构

技术栈


语言：Python 3.12
对话模型：DeepSeek（deepseek-chat）
向量化：智谱 AI（embedding-3）
编排框架：LangGraph
界面：Streamlit
检索：自实现余弦相似度语义检索


模块设计（关注点分离）

模块职责config.py统一配置（密钥、模型、参数）loader.py多文档加载与清洗rag.py向量化与语义检索（RAG 核心）planner.py任务拆解与难易判断assistant.py普通问答与深度研究agents.py多 Agent 协作（检索/分析/写作/审核）graph.pyLangGraph 智能路由memory.py对话记忆utils.py重试等工具logger.py / metrics.py日志与成本统计app.pyStreamlit 界面evaluate.py / testset.py评测集与自动评测

三种回答模式


普通问答：一次检索 + 生成，快速直答
深度研究：拆解为子问题 → 逐个检索回答 → 综合汇总
多 Agent 协作：检索 Agent → 分析 Agent → 写作 Agent → 审核 Agent（带反馈回环）



📊 效果评估

在 60 题评测集上的实测结果（评测集覆盖多主题、多难度，含抗幻觉测试）：
![alt text](../1e5a9c91-311d-4105-91c3-32ad5a85900c.png)

⚠️ 下表数字请替换为你自己实测的真实数据



三种模式对比（同一复杂问题实测）

模式回答完整度耗时特点普通问答部分（漏答跨章节信息）~4s一次检索深度研究完整~17s拆解后分别检索多 Agent 协作完整且严谨~10s分工协作多 Agent + 审核完整、严谨、无过度推断~22s自我修正

关键发现：单次检索在跨章节复杂问题上会遗漏信息；任务拆解与多 Agent 协作能显著提升回答完整度；审核 Agent 能识别并修正模型的过度推断（如把「研发部门有项目奖金」错误套用到试用期新人），有效降低幻觉。


🚀 快速开始

环境要求


Python 3.12
DeepSeek、智谱 AI 的 API 密钥


安装

bash# 克隆仓库
git clone https://github.com/你的用户名/仓库名.git
cd 仓库名/research_assistant

# 创建虚拟环境
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

配置密钥

在项目根目录创建 .env 文件：

DEEPSEEK_API_KEY=你的DeepSeek密钥
ZHIPU_API_KEY=你的智谱密钥
TAVILY_API_KEY=你的Tavily密钥

运行

bash# 网页界面
streamlit run app.py

# 命令行
python main.py


📁 项目结构

research_assistant/
├── app.py              # Streamlit 网页界面
├── main.py             # 命令行入口
├── config.py           # 配置
├── loader.py           # 文档加载与清洗
├── rag.py              # RAG 检索核心
├── planner.py          # 任务拆解 / 难易判断
├── assistant.py        # 普通问答 / 深度研究
├── agents.py           # 多 Agent 协作
├── graph.py            # LangGraph 智能路由
├── memory.py           # 对话记忆
├── utils.py            # 工具（重试等）
├── logger.py           # 日志
├── metrics.py          # Token / 成本统计
├── evaluate.py         # 自动评测
├── testset.py          # 评测集
├── requirements.txt    # 依赖
└── documents/          # 预置示例文档


🧠 技术亮点


完整的 RAG 管线：文档加载 → 清洗 → 切块 → 向量化 → 语义检索 → 生成，并通过参数调优提升检索命中率。
多智能体协作系统：将研究任务分解为检索、分析、写作、审核四个专职 Agent，通过流水线与反馈回环协作，是当前前沿的 Agent 架构范式。
自我修正机制（Reflection）：审核 Agent 对答案质量把关，识别编造与遗漏，不合格则带着修改意见退回重写，有效降低幻觉。
智能路由：基于 LLM 的难易判断，动态选择处理策略，兼顾简单问题的响应速度与复杂问题的回答质量。
工程完备性：错误重试、超时控制、优雅降级、统一日志、Token/成本追踪——从「能跑的 demo」到「可靠的系统」。
系统化评测：构建评测集，使用 LLM-as-judge 量化检索命中率与回答准确率，数据驱动地定位瓶颈与优化。



📝 开发过程

本项目历时约 20 天从零构建，完整记录见 开发日志.md。开发过程中解决了大量真实工程问题：Python 版本兼容、底层库编译冲突（torch/chromadb）、embedding 方案选型、跨模块导入、云端部署密钥管理等。


📄 License

MIT License