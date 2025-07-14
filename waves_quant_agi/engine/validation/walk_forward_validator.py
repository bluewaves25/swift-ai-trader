import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score

class WalkForwardValidator:
    """
    Performs walk-forward validation by splitting time series data
    into training/testing sets across multiple folds.
    """

    def __init__(self, n_splits: int = 5):
        self.n_splits = n_splits

    def validate(self, features: np.ndarray, labels: np.ndarray, model) -> dict:
        """
        Walk-forward validation of a model on provided features and labels.

        Args:
            features (np.ndarray): Feature matrix (time series order).
            labels (np.ndarray): Corresponding labels.
            model: Any ML model with fit/predict methods.

        Returns:
            dict: { 'average_accuracy': float, 'fold_accuracies': list }
        """
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        fold_accuracies = []

        for train_index, test_index in tscv.split(features):
            X_train, X_test = features[train_index], features[test_index]
            y_train, y_test = labels[train_index], labels[test_index]

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            fold_accuracies.append(round(accuracy, 4))

        avg_acc = round(np.mean(fold_accuracies), 4)
        return {
            "average_accuracy": avg_acc,
            "fold_accuracies": fold_accuracies,
            "n_splits": self.n_splits
        }

# ✅ Wrapper function to expose as expected
def walk_forward_analysis(features, labels, model, n_splits: int = 5) -> dict:
    """
    Convenience wrapper for running walk-forward validation.

    Returns:
        dict: Result of WalkForwardValidator.validate()
    """
    validator = WalkForwardValidator(n_splits=n_splits)
    return validator.validate(features, labels, model)
