class MLModel:
    def __init__(self):
        self.feature_weights = [0.30, 0.35, 0.20, 0.10, 0.05]

    def predict_delay(self, features):
        import numpy as np
        features = np.array(features)
        raw_delay = np.dot(features, self.feature_weights) * 30
        delay = max(0, min(60, raw_delay))
        confidence = 0.70 + (1 - abs(features[0] - 0.5)) * 0.25
        return int(round(delay)), round(min(0.95, confidence), 2)
