import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def test_regime_stability(returns: np.ndarray, n_clusters: int = 3) -> dict:
    """
    Tests the stability of market regimes using KMeans clustering.

    Args:
        returns (np.ndarray): 2D array of time-series returns/features.
        n_clusters (int): Number of regimes/clusters to detect.

    Returns:
        dict: {
            "n_clusters": int,
            "cluster_counts": list[int],
            "cluster_std_devs": list[float]
        }
    """
    if len(returns.shape) == 1:
        returns = returns.reshape(-1, 1)

    scaler = StandardScaler()
    scaled_returns = scaler.fit_transform(returns)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(scaled_returns)

    counts = [int(np.sum(labels == i)) for i in range(n_clusters)]
    stabilities = []

    for i in range(n_clusters):
        cluster_data = scaled_returns[labels == i]
        if len(cluster_data) > 1:
            std_dev = np.std(cluster_data)
        else:
            std_dev = 0.0
        stabilities.append(round(float(std_dev), 4))

    return {
        "n_clusters": n_clusters,
        "cluster_counts": counts,
        "cluster_std_devs": stabilities
    }
