import torch
import torch.nn as nn

class MarketTransformer(nn.Module):
    """
    🧠 Transformer model to understand sequences of market data (price, volume, etc.).
    """

    def __init__(self, input_dim=16, model_dim=64, num_heads=4, num_layers=2):
        super().__init__()
        encoder_layer = nn.TransformerEncoderLayer(d_model=model_dim, nhead=num_heads)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.input_proj = nn.Linear(input_dim, model_dim)
        self.output = nn.Linear(model_dim, 1)

    def forward(self, x):
        """
        :param x: Tensor of shape (seq_len, batch_size, input_dim)
        """
        x = self.input_proj(x)
        x = self.encoder(x)
        return self.output(x.mean(dim=0))  # Aggregate over time
