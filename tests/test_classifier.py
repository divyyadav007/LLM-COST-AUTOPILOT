from app.services.classifier_service import ClassifierService


def test_classifier_initialization() -> None:
    """Verifies that the classifier is correctly initialized but not yet trained."""
    classifier = ClassifierService()
    assert classifier.is_trained is False
    assert classifier.tier_mapping[0] == "simple"


def test_classifier_training() -> None:
    """Verifies that training fits the baseline TF-IDF vectorizer and logistic regression model."""
    classifier = ClassifierService()
    classifier.train_baseline_model()
    assert classifier.is_trained is True


def test_classifier_prediction() -> None:
    """Verifies that the classifier can predict the difficulty tier of a given text prompt."""
    classifier = ClassifierService()
    # Simple prompt check
    tier_simple, conf_simple = classifier.predict_tier("What is the capital of France?")
    assert tier_simple in ["simple", "moderate"]
    assert 0.0 <= conf_simple <= 1.0

    # Complex prompt check
    tier_complex, conf_complex = classifier.predict_tier(
        "Write a multi-threaded Python optimization routine handling concurrency locks"
    )
    assert tier_complex == "complex"
    assert conf_complex > 0.3
