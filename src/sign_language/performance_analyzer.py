"""Analisis de desempeno para los intentos confirmados de aprendizaje."""

from dataclasses import dataclass
from typing import Any, Mapping

from src.config import MAX_ATTEMPTS
from src.languages import normalize_language, t

MIN_RECOMMENDATION_PERCENTAGE = 70.0
GOOD_PERFORMANCE_PERCENTAGE = 85.0


@dataclass(frozen=True)
class PerformanceAnalysis:
    attempts: int
    correct: int
    incorrect: int
    accuracy: float
    message: str
    recommendation: str

    def as_dict(self) -> dict:
        return {
            "attempts": self.attempts,
            "correct": self.correct,
            "incorrect": self.incorrect,
            "accuracy": self.accuracy,
            "message": self.message,
            "recommendation": self.recommendation,
        }


class LearningPerformanceAnalyzer:
    """Calcula el desempeno sin depender de la interfaz ni de la base de datos.

    Los mensajes se generan en el idioma de aprendizaje (es, en, pt).
    """

    def __init__(self, language: str = "es") -> None:
        self.language = normalize_language(language)

    def analyze(self, stats: Mapping[str, Any] | None, letter: str, language: str | None = None) -> PerformanceAnalysis:
        lang = normalize_language(language) if language else self.language
        stats = stats or {}
        attempts = max(0, int(stats.get("attempts", 0)))
        correct = max(0, int(stats.get("correct", 0)))
        incorrect = max(0, int(stats.get("incorrect", 0)))

        # La base guarda ambos contadores; se prioriza el total recibido para no inventar intentos.
        if attempts == 0:
            attempts = correct + incorrect
        correct = min(correct, attempts)
        incorrect = min(incorrect, attempts - correct)
        accuracy = round((correct / attempts) * 100, 2) if attempts else 0.0 # calcula el porcentaje de aciertos

        if attempts < MAX_ATTEMPTS:  # despues aplicamos estas reglas
            return PerformanceAnalysis(
                attempts=attempts,
                correct=correct,
                incorrect=incorrect,
                accuracy=accuracy,
                message=t(lang, "perf_continue"),
                recommendation="continue",
            )

        if accuracy < MIN_RECOMMENDATION_PERCENTAGE:  # cuando es menos del 70  muestra estos mensajes:
            message = t(lang, "perf_practice", letter=letter, correct=correct, attempts=attempts)
            recommendation = "practice"
        elif accuracy < GOOD_PERFORMANCE_PERCENTAGE:
            message = t(lang, "perf_optional", letter=letter, correct=correct, attempts=attempts)
            recommendation = "optional_practice"
        else:
            message = t(lang, "perf_good", letter=letter, correct=correct, attempts=attempts)
            recommendation = "good"

        return PerformanceAnalysis(
            attempts=attempts,
            correct=correct,
            incorrect=incorrect,
            accuracy=accuracy,
            message=message,
            recommendation=recommendation,
        )