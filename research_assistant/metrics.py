PRICE_INPUT = 1.0    # 示意值，务必换成真实价格
PRICE_OUTPUT = 2.0   # 示意值，务必换成真实价格

class Metrics:
    def __init__(self):
        self.total_input = 0
        self.total_output = 0
        self.call_count = 0

    def add(self, input_tokens, output_tokens):
        self.total_input += input_tokens
        self.total_output += output_tokens
        self.call_count += 1

    def cost(self):
        return (self.total_input * PRICE_INPUT +
                self.total_output * PRICE_OUTPUT) / 1_000_000

    def report(self):
        return (f"共调用 {self.call_count} 次，"
                f"输入 {self.total_input} token，输出 {self.total_output} token，"
                f"约 {self.cost():.4f} 元")

metrics = Metrics()   # 全局实例