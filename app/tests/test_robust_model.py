import pytest

from app.services.sentiment_predict import SentimentPredict, SentimentPredictLevel

test_data = [
    ("I am very clever", SentimentPredictLevel.VERY_POSITIVE),
    ("I am dumb", SentimentPredictLevel.VERY_NEGATIVE),
    ("You job offerring does not look great", SentimentPredictLevel.NEGATIVE),
    (
        "My work helped my company to increase revenue by 50%",
        SentimentPredictLevel.POSITIVE,
    ),
    ("I like cats", SentimentPredictLevel.NEUTRAL),
    ("", SentimentPredictLevel.NEUTRAL),
]


@pytest.mark.parametrize("text, expected", test_data)
def test_sentiment_predict(text: str, expected: SentimentPredictLevel):
    sentiment_predict = SentimentPredict()
    assert sentiment_predict.predict(text) == expected
