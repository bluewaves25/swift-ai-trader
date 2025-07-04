class ScalpingStrategy:
    def analyze(self, data: dict):
        current_price = data['close'][-1]
        sma_short = sum(data['close'][-5:]) / 5
        sma_long = sum(data['close'][-20:]) / 20

        if current_price > sma_short > sma_long:
            return {'signal': 'buy', 'confidence': 0.9, 'stop_loss': current_price * 0.995, 'take_profit': current_price * 1.005}
        elif current_price < sma_short < sma_long:
            return {'signal': 'sell', 'confidence': 0.9, 'stop_loss': current_price * 1.005, 'take_profit': current_price * 0.995}
        return {'signal': 'hold', 'confidence': 0.5}