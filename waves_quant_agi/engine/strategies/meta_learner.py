from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from engine.strategies.base_strategy import BaseStrategy

class MetaLearner(BaseStrategy):
    def __init__(self):
        super().__init__()

    def optimize(self, X, y):
        grid = {
            "n_estimators": [50, 100],
            "max_depth": [3, 5, None]
        }
        model = GridSearchCV(RandomForestClassifier(), grid, cv=3)
        model.fit(X, y)
        return model.best_params_
