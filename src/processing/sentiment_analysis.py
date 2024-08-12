"""This module defines a sentiment classification class which predicts the sentiment for 
incoming social media comments"""


from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax


class SentimentAnalysisModel:
    """
    This class defines a sentiment prediction model based on the twitter-roberta-base-sentiment
    model from the HuggingFace hub.
    """
    def __init__(self):
        self.model_name = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.config = AutoConfig.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)

    def preprocess(self, text):
        """Placeholder for future pre-processing steps"""
        # TODO: Preprocess the data lol
        return text

    def predict(self, text):
        """
        Predicts sentiment for incoming processed text

        Args:
            Text (str): text to be processed

        Returns:
            top_l (str): Top scoring classification label. One of: Positive, negative, neutral
            top_s (float): Prediction score on the range 0<score<1
        """

        processed_text = self.preprocess(text)
        encoded_input = self.tokenizer(processed_text, return_tensors='pt')

        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        ranking = np.argsort(scores)
        ranking = ranking[::-1]
        top_l = self.config.id2label[ranking[0]]
        top_s = scores[ranking[0]]
        return top_l, top_s
