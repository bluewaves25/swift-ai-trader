class BreakoutStrategy:
    def analyze(self, data: dict):
        recent_high = max(data['high'][-20:])
        recent_low = min(data['low'][-20:])
        current_price = data['close'][-1]

        if current_price > recent_high:
            return {'signal': 'buy', 'confidence': 0.85, 'stop_loss': recent_low, 'take_profit': current_price * 1.02}
        elif current_price < recent_low:
            return {'signal': 'sell', 'confidence': 0.85, 'stop_loss': recent_high, 'take_profit': current_price * 0.98}
        return {'signal': 'hold', 'confidence': 0.5}