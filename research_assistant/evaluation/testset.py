test_set = [
    # ===== 简单题 (15题，其中第15题为文档无法回答) =====
    {
        "question": "RAG的全称是什么？",
        "expected": "Retrieval-Augmented Generation",
        "source": "段落1"
    },
    {
        "question": "RAG框架主要包含哪两个核心组件？",
        "expected": "检索器（Retriever）和生成器（Generator）",
        "source": "段落2"
    },
    {
        "question": "文中提到的稀疏检索方法的具体名称是什么？",
        "expected": "BM25",
        "source": "段落2"
    },
    {
        "question": "密集检索使用什么技术将查询和文档映射到向量空间？",
        "expected": "嵌入模型",
        "source": "段落2"
    },
    {
        "question": "两阶段检索的第二阶段使用什么模型来提升上下文质量？",
        "expected": "重排序模型（Reranker）",
        "source": "段落2"
    },
    {
        "question": "分块过大可能给生成模型带来什么问题？",
        "expected": "淹没上下文窗口，降低信噪比",
        "source": "段落3"
    },
    {
        "question": "文本分块后，通过什么模型转换成向量？",
        "expected": "嵌入模型（如BGE、E5、OpenAI text-embedding-3）",
        "source": "段落3"
    },
    {
        "question": "向量数据库的主要用途是什么？",
        "expected": "存储文本块向量，进行快速近似最近邻搜索",
        "source": "段落3"
    },
    {
        "question": "生成阶段将检索到的片段和用户查询组合成什么？",
        "expected": "提示（Prompt）",
        "source": "段落4"
    },
    {
        "question": "提示工程要求模型在上下文不足时如何回应？",
        "expected": "说明无法回答",
        "source": "段落4"
    },
    {
        "question": "答案忠实度指标衡量什么？",
        "expected": "答案是否完全基于检索到的上下文，不包含编造事实",
        "source": "段落5"
    },
    {
        "question": "除了忠实度，文中还明确提到了哪两个RAG评估指标？",
        "expected": "答案相关性（Answer Relevance）和上下文相关性（Context Relevance）",
        "source": "段落5"
    },
    {
        "question": "当知识库缺乏相关信息时，RAG系统应展示什么能力？",
        "expected": "拒答能力（Abstention）",
        "source": "段落6"
    },
    {
        "question": "多跳问答需要整合什么类型的信息？",
        "expected": "多个分散文档中的信息",
        "source": "段落6"
    },
    {
        "question": "文中提到的向量数据库Chroma、Milvus、Pinecone中，哪些明确支持私有化本地部署？",
        "expected": "无法回答，文档未提供相关部署信息",
        "source": "文档未提供"
    },

    # ===== 难题 (15题，其中第29、30题为文档无法回答) =====
    {
        "question": "从用户提问到生成答案，RAG系统完整的处理流程包含哪些关键步骤？请按顺序简述。",
        "expected": "用户查询 -> 检索器从索引检索相关片段 -> 重排序精排 -> 片段与查询组成提示 -> 生成器生成答案。关键点：检索、重排序、提示构建、生成。",
        "source": "段落2、段落4"
    },
    {
        "question": "分块策略如何间接影响答案忠实度？请结合文本分析。",
        "expected": "分块质量决定检索到的上下文是否准确、完整。若分块不当导致上下文缺失或噪声过多，生成器可能偏离上下文，降低忠实度。",
        "source": "段落3、段落5"
    },
    {
        "question": "在RAG系统中，BM25和密集检索通常如何互补？",
        "expected": "BM25保证关键词匹配召回，密集检索捕捉语义相关性；可先用BM25粗筛，再结合密集检索或重排序进行精细筛选，形成两阶段混合检索。",
        "source": "段落2"
    },
    {
        "question": "假如用户询问‘比较产品A和产品B’，但知识库只有产品A的资料。根据文本，一个设计良好的RAG系统应怎样响应？为什么？",
        "expected": "应拒答或说明无法比较。理由：上下文不足，提示工程要求模型在信息缺乏时说明无法回答，且系统应具备拒答能力以避免幻觉。",
        "source": "段落4、段落6"
    },
    {
        "question": "Graph RAG主要应对RAG的什么挑战？它与标准RAG在信息整合方式上有何不同？",
        "expected": "应对多跳问答挑战；通过图结构索引支持多跳推理，而标准RAG通常为单步检索后直接生成。",
        "source": "段落6"
    },
    {
        "question": "解释为什么分块太大会‘淹没’生成模型的上下文窗口，以及这可能对答案质量造成哪些影响。",
        "expected": "大文本块占用大量token，挤占指令和生成空间；同时引入更多噪声，干扰模型注意力，可能导致答案冗余、不精确或偏离主题。",
        "source": "段落3、段落4"
    },
    {
        "question": "上下文相关性指标与答案忠实度指标在评估对象上有何区别？",
        "expected": "上下文相关性评估检索到的文档是否与问题相关；答案忠实度评估生成的答案是否严格依据所给上下文，两者侧重点不同。",
        "source": "段落5"
    },
    {
        "question": "为什么评估检索阶段的召回率对整体RAG系统至关重要？",
        "expected": "低召回意味着相关文档未被检索到，生成器缺少必要信息，极易导致答案不完整或产生幻觉，直接影响最终质量。",
        "source": "段落5"
    },
    {
        "question": "依据文本，拒答能力对于面向公众的RAG应用有何重要性？",
        "expected": "在知识库无信息时避免模型胡编乱造，提升系统可信度和安全性，防止误导用户。",
        "source": "段落6"
    },
    {
        "question": "多模态RAG在索引构建阶段与纯文本RAG的主要区别在哪里？",
        "expected": "需要对图像、音频等多模态数据进行处理，并使用多模态嵌入模型生成跨模态向量以支持检索。",
        "source": "段落7"
    },
    {
        "question": "智能体RAG框架可能如何改标准RAG面对复杂问题时的表现？",
        "expected": "通过动态规划分解子问题、自主选择检索策略并使用工具，实现多步推理和答案验证，提升复杂问题的处理能力。",
        "source": "段落7"
    },
    {
        "question": "文中提到‘迭代检索’提升多跳问答效果，其可能的工作机制是什么？",
        "expected": "利用当前检索到的信息生成下一步查询，逐步收集分散的证据，串联多跳推理所需的完整信息链。",
        "source": "段落6"
    },
    {
        "question": "如果要在移动设备上部署RAG系统，根据本文是否能找到性能优化相关建议？",
        "expected": "无法回答，文档未讨论移动端部署或针对性优化方案。",
        "source": "文档未提供"
    },
    {
        "question": "文本是否讨论了RAG在处理实时流式数据更新时索引维护的具体方案？",
        "expected": "无法回答，文档未涉及实时数据流或增量索引的具体内容。",
        "source": "文档未提供"
    },

  {
        "question": "提出Transformer的论文全称是什么？",
        "expected": "Attention Is All You Need",
        "source": "论文标题"
    },
    {
        "question": "Transformer模型完全摒弃了哪两种传统神经网络结构？",
        "expected": "循环神经网络和卷积神经网络（或循环和卷积）",
        "source": "模型架构"
    },
    {
        "question": "Transformer编码器由多少个相同的层堆叠而成？",
        "expected": "6",
        "source": "模型架构"
    },
    {
        "question": "解码器中比编码器多出的子层是什么？",
        "expected": "对编码器输出的多头交叉注意力（cross-attention）子层",
        "source": "模型架构"
    },
    {
        "question": "缩放点积注意力公式中，分母是什么？",
        "expected": "√dₖ （或根号d_k）",
        "source": "注意力机制"
    },
    {
        "question": "base模型中，多头注意力的头数（h）是多少？",
        "expected": "8",
        "source": "注意力机制"
    },
    {
        "question": "位置编码使用了哪两种三角函数？",
        "expected": "正弦（sin）和余弦（cos）",
        "source": "位置编码"
    },
    {
        "question": "前馈网络中使用的激活函数是什么？",
        "expected": "ReLU",
        "source": "前馈网络"
    },
    {
        "question": "论文中使用的主要优化器名称是什么？",
        "expected": "Adam",
        "source": "训练与结果"
    },
    {
        "question": "base模型中前馈网络的内层维度（d_ff）是多少？",
        "expected": "2048",
        "source": "前馈网络"
    },
    {
        "question": "论文评估模型性能的指标是什么？",
        "expected": "BLEU",
        "source": "训练与结果"
    },
    {
        "question": "Transformer base模型在WMT 2014英德翻译任务上的BLEU分数是多少？",
        "expected": "28.4",
        "source": "训练与结果"
    },
    {
        "question": "在base模型中，每个注意力头的维度d_k是多少？",
        "expected": "64",
        "source": "注意力机制"
    },
    {
        "question": "每个子层后使用的连接技术是什么？",
        "expected": "残差连接和层归一化",
        "source": "模型架构"
    },
    {
        "question": "解码器自注意力子层做了什么特殊处理以防止信息泄露？",
        "expected": "使用掩码（masking）防止关注未来位置",
        "source": "模型架构"
    },

    # ===== 难题 (15题，其中第27-30题为文档无法回答) =====
    {
        "question": "为什么在缩放点积注意力中要除以√d_k？",
        "expected": "防止点积值过大，导致softmax梯度趋近于0（或出现梯度消失），使学习变慢或不稳定",
        "source": "注意力机制"
    },
    {
        "question": "多头注意力如何使模型捕捉到不同的表示子空间？",
        "expected": "通过多个不同的线性投影将Q、K、V映射到低维空间，并行执行注意力，使每个头可关注不同位置/语义信息，拼接后融合",
        "source": "注意力机制"
    },
    {
        "question": "位置编码公式中频率项 10000^(2i/d_model) 的作用是什么？",
        "expected": "使得不同维度对应不同波长的正弦波，形成独特的编码，使模型能够区分位置并可能学习相对位置关系",
        "source": "位置编码"
    },
    {
        "question": "解码器掩码自注意力具体是如何实现的？",
        "expected": "将注意力分数矩阵中未来位置对应的值设为负无穷（-∞），经过softmax后这些位置的权重变为0",
        "source": "模型架构、注意力机制"
    },
    {
        "question": "残差连接在深层Transformer中的主要作用是什么？",
        "expected": "缓解梯度消失问题，使深层网络更容易训练，保证信息跨层流通",
        "source": "模型架构"
    },
    {
        "question": "训练时使用标签平滑对模型会产生什么影响？",
        "expected": "防止模型对预测过于自信，提高泛化能力，可能改善BLEU分数",
        "source": "训练与结果"
    },
    {
        "question": "相比循环神经网络，Transformer训练并行性更好的原因是什么？",
        "expected": "自注意力计算不依赖序列时间步，可对所有位置同时计算，而RNN需逐步处理",
        "source": "模型架构、注意力机制"
    },
    {
        "question": "给定d_model=512，h=8，请描述每个注意力头中Q和K的维度，以及拼接后输出维度。",
        "expected": "每个头Q和K的维度为64（d_model/h=512/8），拼接后输出维度为512",
        "source": "注意力机制"
    },
    {
        "question": "使用正弦/余弦位置编码相比于可学习的嵌入位置编码，有什么潜在优势？",
        "expected": "可以外推到比训练时更长的序列长度，因为它是确定性函数，无需额外训练",
        "source": "位置编码"
    },
    {
        "question": "解码器交叉注意力子层中，Q、K、V分别来自哪里？",
        "expected": "Q来自解码器前一层的输出，K和V均来自编码器的输出",
        "source": "解码器交叉注意力细节"
    },
    {
        "question": "如果不进行缩放，直接在较高维度下计算点积注意力，softmax的输出可能会呈现什么现象？",
        "expected": "点积值方差变大，softmax输出趋近于one-hot分布（某些值接近1，其余接近0），导致梯度极小，模型难以训练",
        "source": "注意力机制"
    },
    {
        "question": "Adam优化器的β1、β2和epsilon的具体数值是多少？",
        "expected": "无法回答，文档中未提供这些超参数的具体数值",
        "source": "文档未提供"
    },
    {
        "question": "论文中使用的Dropout正则化比率是多少？",
        "expected": "无法回答，文档仅说明使用了Dropout，但未给出具体比率",
        "source": "文档未提供"
    },
    {
        "question": "标签平滑中的参数epsilon（ε）被设置为多少？",
        "expected": "无法回答，文档未提供该具体数值",
        "source": "文档未提供"
    },
    {
        "question": "论文中提到的学习率warmup策略的主要目的是什么？",
        "expected": "无法回答，文档只提到warmup_steps=4000，但未解释其目的",
        "source": "文档未提供"
    }  
]