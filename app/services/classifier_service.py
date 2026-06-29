import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle
import os

class ClassifierService:
    def __init__(self):
        """
        Model matrix architecture definitions storage references.
        """
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        
        # FIX: Removed the deprecated 'multi_class' parameter.
        # Scikit-learn will dynamically switch to multinomial routing based on the target variables array.
        self.model = LogisticRegression(solver='lbfgs', max_iter=200)
        self.is_trained = False
        self.tier_mapping = {0: "simple", 1: "moderate", 2: "complex"}

    def generate_synthetic_data(self):
        """
        Creates mathematical training corpus arrays mimicking production telemetry weights.
        """
        # Feature structures templates mappings
        simple_prompts = [
            "What is the capital of France?", "Who wrote Romeo and Juliet?",
            "Extract names from text", "List down items inside this bucket",
            "Give me the definition of photosynthesis", "Hello how are you today"
        ] * 20
        
        moderate_prompts = [
            "Summarize the following document for enterprise tracking parameters",
            "Classify these structural data tables inside appropriate storage",
            "Generate a generic feedback email response format based on these keywords",
            "Review this simple text file structure and explain its key highlights",
            "Convert this paragraph layout into simple clear pointers format"
        ] * 20
        
        complex_prompts = [
            "Write a multi-threaded Python optimization routine handling concurrency locks",
            "Debug this compound database execution trace yielding memory leak exceptions",
            "Design an complete system architectural layout for distributed cluster messaging queue",
            "Compute mathematical vector transforms optimization spaces dynamically",
            "Create custom regular expression patterns sorting deep nested polymorphic json structures"
        ] * 20

        X_raw = simple_prompts + moderate_prompts + complex_prompts
        # Labels: 0 = Simple, 1 = Moderate, 2 = Complex
        y = np.array([0]*len(simple_prompts) + [1]*len(moderate_prompts) + [2]*len(complex_prompts))
        return X_raw, y

    def train_baseline_model(self):
        """
        Executes internal optimization solver loops fitting coefficients metrics maps.
        """
        X_raw, y = self.generate_synthetic_data()
        X_vectors = self.vectorizer.fit_transform(X_raw)
        self.model.fit(X_vectors, y)
        self.is_trained = True

    def predict_tier(self, prompt: str) -> str:
        """
        Evaluates incoming inference payload string mapping it to system tier names targets.
        """
        if not self.is_trained:
            # Automatic fallback guardrail initialization preventing blank evaluations state
            self.train_baseline_model()

        # Transformation step projecting raw string into fitted vocabulary coordinates system
        features = self.vectorizer.transform([prompt])
        prediction_id = self.model.predict(features)[0]
        
        # Pull explicit classification confidence matrix probability array tracking profiles
        probabilities = self.model.predict_proba(features)[0]
        confidence = float(probabilities[prediction_id])
        
        return self.tier_mapping.get(prediction_id, "moderate"), confidence