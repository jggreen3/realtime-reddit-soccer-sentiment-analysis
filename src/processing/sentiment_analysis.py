"""This module defines a sentiment classification class which predicts the sentiment for 
incoming social media comments"""

import os
import logging
import dotenv
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

class SentimentAnalysisModel:
    """
    This class defines a sentiment prediction model based on the twitter-roberta-base-sentiment
    model from the HuggingFace hub.
    """
    def __init__(self):
        self.model_name = os.getenv('MODEL_NAME')
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.config = AutoConfig.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)

    def preprocess(self, text: str) -> str:
        """
        Preprocesses the input text.

        Args:
            text (str): The input text to be preprocessed.

        Returns:
            str: The preprocessed text.
        """
        # Basic preprocessing steps (can be expanded in the future)
        return text.strip()

    def predict(self, text: str) -> tuple[str, float]:

        """
        Predicts sentiment for incoming processed text

        Args:
            Text (str): text to be processed

        Returns:
            Tuple[str, float]: Top scoring classification label and prediction score.
        """

        try:
            processed_text = self.preprocess(text)
            encoded_input = self.tokenizer(processed_text, return_tensors='pt')
            output = self.model(**encoded_input)
            scores = output.logits.detach().numpy()[0]
            scores = softmax(scores)
            top_l, top_s = self._get_top_prediction(scores)
            logger.info("Predicted sentiment: %s with score: %s", top_l, top_s)
            return top_l, top_s
        except Exception as e:
            logger.error("Error during prediction: %s", e)
            raise

    def _get_top_prediction(self, scores: np.ndarray) -> tuple[str, float]:
        """
        Extracts the top prediction label and score.

        Args:
            scores (np.ndarray): Array of sentiment scores.

        Returns:
            Tuple[str, float]: The label and score of the top prediction.
        """
        ranking = np.argsort(scores)[::-1]
        top_label = self.config.id2label[ranking[0]]
        top_score = scores[ranking[0]]
        return top_label, top_score
    