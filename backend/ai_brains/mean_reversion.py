class MeanReversionStrategy:
    def analyze(self, data: dict):
        current_price = data['close'][-1]
        mean_price = sum(data['close'][-20:]) / 20
        std_price = (sum((x - mean_price) ** 2 for x in data['close'][-20:]) / 20) ** 0.5

        if current_price < mean_price - std_price:
            return {'signal': 'buy', 'confidence': 0.8, 'stop_loss': current_price * 0.99, 'take_profit': mean_price}
        elif current_price > mean_price + std_price:
            return {'signal': 'sell', 'confidence': 0.8, 'stop_loss': current_price * 1.01, 'take_profit': mean_price}
        return {'signal': 'hold', 'confidence': 0.5}