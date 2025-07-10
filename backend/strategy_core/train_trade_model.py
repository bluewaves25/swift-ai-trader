import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class TradeValidationModel(nn.Module):
    def __init__(self):
        super(TradeValidationModel, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(3, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)

async def fetch_data():
    try:
        trades_resp = supabase.table("trades").select("volume, price, symbol").execute()
        sentiments_resp = supabase.table("sentiments").select("symbol, combined_score").execute()
    except Exception as e:
        print(f" Failed to fetch data from Supabase: {e}")
        return None, None

    trades = trades_resp.data
    sentiments = sentiments_resp.data

    dataset = []
    for trade in trades:
        sentiment = next((s for s in sentiments if s["symbol"] == trade["symbol"]), None)
        if not sentiment:
            continue

        if not all(k in trade for k in ("volume", "price")) or "combined_score" not in sentiment:
            continue

        # Optional: You can log any missing data for review

        # Sample label: 1 for trades > $50, else 0 (you may change this logic later)
        label = 1 if trade["volume"] * trade["price"] > 50 else 0
        dataset.append([
            float(trade["volume"]),
            float(trade["price"]),
            float(sentiment["combined_score"]),
            label
        ])

    if len(dataset) < 10:
        print(" Not enough data to train. Found:", len(dataset))
        return None, None

    np_data = np.array(dataset)
    X = np_data[:, :3].astype(np.float32)
    y = np_data[:, 3:].astype(np.float32)

    return torch.tensor(X), torch.tensor(y)

async def train():
    X, y = await fetch_data()
    if X is None or y is None:
        return

    model = TradeValidationModel()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    for epoch in range(200):
        outputs = model(X)
        loss = criterion(outputs, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 50 == 0:
            print(f" Epoch {epoch+1}/200 | Loss: {loss.item():.4f}")

    torch.save(model.state_dict(), "trade_model.pt")
    print(" Model trained and saved to trade_model.pt")

if __name__ == "__main__":
    asyncio.run(train())
