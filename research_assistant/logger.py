import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),                          # 输出到屏幕
        logging.FileHandler("agent.log", encoding="utf-8"),  # 也存文件
    ],
)
logger = logging.getLogger("research_assistant")