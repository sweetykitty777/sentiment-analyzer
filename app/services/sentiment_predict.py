from enum import Enum

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class SentimentPredictLevel(str, Enum):
    VERY_NEGATIVE = "VERY_NEGATIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    POSITIVE = "POSITIVE"
    VERY_POSITIVE = "VERY_POSITIVE"


mapper = {
    0: SentimentPredictLevel.VERY_NEGATIVE,
    1: SentimentPredictLevel.NEGATIVE,
    2: SentimentPredictLevel.NEUTRAL,
    3: SentimentPredictLevel.POSITIVE,
    4: SentimentPredictLevel.VERY_POSITIVE,
}

model_name = "tabularisai/robust-sentiment-analysis"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


class SentimentPredict:
    def predict(self, value: str) -> SentimentPredictLevel:
        inputs = tokenizer(value.lower(), return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)

        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        probabilities_np = probabilities.numpy()
        predicted_class = np.argmax(probabilities_np, axis=-1)

        return mapper[predicted_class[0]]
