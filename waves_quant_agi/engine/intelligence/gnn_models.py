import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv

class CorrelationGNN(nn.Module):
    """
    🕸️ Graph Neural Network to model relationships between assets.
    """

    def __init__(self, num_features, hidden_dim=64):
        super().__init__()
        self.conv1 = GCNConv(num_features, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, 1)

    def forward(self, data):
        """
        data: PyG Data object with x (features), edge_index
        """
        x, edge_index = data.x, data.edge_index
        x = F.relu(self.conv1(x, edge_index))
        x = self.conv2(x, edge_index)
        return x
