import logging

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)


class ClassifierService:
    """Service to classify incoming text prompts into complexity tiers."""

    def __init__(self) -> None:
        """Initializes features and model components."""
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words="english")

        # Scikit-learn will dynamically switch to multinomial routing based on the target variables array.
        self.model = LogisticRegression(solver="lbfgs", max_iter=200)
        self.is_trained = False
        self.tier_mapping = {0: "simple", 1: "moderate", 2: "complex"}
        logger.debug("Initialized ClassifierService with LogisticRegression.")

    def generate_synthetic_data(self) -> tuple[list[str], np.ndarray]:
        """
        Creates mathematical training corpus arrays mimicking production telemetry weights.

        Returns:
            Tuple[List[str], np.ndarray]: A tuple of training texts (X) and class labels (y).
        """
        simple_prompts = [
            "What is the capital of France?",
            "Who wrote Romeo and Juliet?",
            "Extract names from text",
            "List down items inside this bucket",
            "Give me the definition of photosynthesis",
            "Hello how are you today",
        ] * 20

        moderate_prompts = [
            "Summarize the following document for enterprise tracking parameters",
            "Classify these structural data tables inside appropriate storage",
            "Generate a generic feedback email response format based on these keywords",
            "Review this simple text file structure and explain its key highlights",
            "Convert this paragraph layout into simple clear pointers format",
        ] * 20

        complex_prompts = [
            "Write a multi-threaded Python optimization routine handling concurrency locks",
            "Debug this compound database execution trace yielding memory leak exceptions",
            "Design an complete system architectural layout for distributed cluster messaging queue",
            "Compute mathematical vector transforms optimization spaces dynamically",
            "Create custom regular expression patterns sorting deep nested polymorphic json structures",
        ] * 20

        X_raw = simple_prompts + moderate_prompts + complex_prompts
        y = np.array(
            [0] * len(simple_prompts) + [1] * len(moderate_prompts) + [2] * len(complex_prompts)
        )
        return X_raw, y

    def train_baseline_model(self) -> None:
        """
        Executes internal optimization solver loops fitting coefficients metrics maps.
        """
        logger.info("Training baseline prompt complexity NLP classifier...")
        X_raw, y = self.generate_synthetic_data()
        X_vectors = self.vectorizer.fit_transform(X_raw)
        self.model.fit(X_vectors, y)
        self.is_trained = True
        logger.info("Baseline NLP classifier trained successfully.")

    def predict_tier(self, prompt: str) -> tuple[str, float]:
        """
        Evaluates incoming inference payload string mapping it to system tier names targets.

        Args:
            prompt (str): Ingested text payload from client.

        Returns:
            Tuple[str, float]: The classified tier (simple, moderate, complex) and its confidence score.
        """
        if not self.is_trained:
            logger.info("Classifier model not trained. Triggering auto-training baseline...")
            self.train_baseline_model()

        # Project raw string into vocabulary space coordinates
        features = self.vectorizer.transform([prompt])
        prediction_id = int(self.model.predict(features)[0])

        # Pull explicit classification confidence matrix probability array tracking profiles
        probabilities = self.model.predict_proba(features)[0]
        confidence = float(probabilities[prediction_id])

        tier = self.tier_mapping.get(prediction_id, "moderate")
        logger.debug("Classified prompt. Tier: %s, Confidence: %.4f", tier, confidence)
        return tier, confidence
