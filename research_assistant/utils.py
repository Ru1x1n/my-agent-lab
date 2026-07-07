import time

def retry(func, max_attempts=3, delay=2):
    """重试执行一个函数，失败就等一会儿再试，最多 max_attempts 次。"""
    for attempt in range(1, max_attempts + 1):
        try:
            return func()  # 尝试执行
        except Exception as e:
            print(f"【重试】第 {attempt} 次失败: {e}")
            if attempt < max_attempts:
                time.sleep(delay)  # 等一会儿再试
            else:
                print(f"【重试】多次失败，放弃。")
                raise  # 试到最后还没失败，才真正报错