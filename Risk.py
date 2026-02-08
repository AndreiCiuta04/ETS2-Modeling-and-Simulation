import math
import random
from RiskPattern import RiskPattern

"""
Risk / aggressiveness dynamics for trading behavior.

Risk (alpha) controls how strongly a firm shifts its bid/ask towards
the previous market price (less aggressive) versus its own valuation
(more aggressive).

High alpha  -> more anchored to last market price (more like to follow the market)
Low alpha   -> closer to own valuation 
"""


class Risk:
    """
    Encapsulates a time-varying risk/aggressiveness trajectory α(t).

    The firm queries this object daily to obtain α, which is then used inside
    the trading rule to interpolate between a firm's reservation price and the
    previous market price.
    """

    def __init__(
        self,
        pattern: RiskPattern,
        start_risk: float,
        end_risk: float,
        horizon: int,
        seed: int | None = None,
        n_steps: int = 5,
        noise_std: float = 0.05,
    ):
        """
        Creates a risk trajectory with a selected pattern.

        @param pattern: Selected RiskPattern (e.g., CONSTANT, LINEAR_DECREASING, etc.).
        @param start_risk: Initial risk/aggressiveness level (typically in [0, 1]).
        @param end_risk: Final risk/aggressiveness level (typically in [0, 1]).
        @param horizon: Number of simulation days (T).
        @param seed: Optional RNG seed (used for step days and random noise patterns).
        @param n_steps: Number of steps for stepwise patterns.
        @param noise_std: Standard deviation for noise in RANDOM_STEPWISE.
        """
        self.pattern = pattern
        self.start_risk = float(start_risk)
        self.end_risk = float(end_risk)
        self.horizon = int(horizon)
        self.n_steps = max(1, int(n_steps))
        self.noise_std = float(noise_std)

        # Local RNG to keep risk trajectories reproducible and independent.
        self._rng = random.Random(seed)

        # For stepwise patterns, randomly choose step-change days (strictly within 1..horizon-1).
        if self.horizon > 1:
            self.step_days = sorted(
                self._rng.sample(
                    range(1, self.horizon),
                    k=min(self.n_steps, self.horizon - 1),
                )
            )
        else:
            self.step_days = []

    def value(self, day: int) -> float:
        """
        Returns α for that day according to the configured RiskPattern.

        @param day: Current simulation day (1-based).
        @return: Risk/aggressiveness value α in [0, 1].
        @raises ValueError: If an unsupported pattern is requested.
        """
        # Clamp day to the simulated range
        day = max(1, min(day, self.horizon))
        t = day / self.horizon  # normalized time in [0, 1]

        if self.pattern == RiskPattern.CONSTANT:
            val = self.start_risk

        elif self.pattern == RiskPattern.LINEAR_DECREASING:
            val = self.start_risk * (1 - t) + self.end_risk * t

        elif self.pattern == RiskPattern.LINEAR_INCREASING:
            val = self.end_risk * (1 - t) + self.start_risk * t

        elif self.pattern == RiskPattern.CONCAVE_DECREASING:
            # Faster early decline, slower late decline.
            val = self.start_risk * (1 - math.sqrt(t)) + self.end_risk * math.sqrt(t)

        elif self.pattern == RiskPattern.CONVEX_DECREASING:
            # Slower early decline, faster late decline.
            val = self.start_risk * (1 - t ** 2) + self.end_risk * (t ** 2)

        elif self.pattern == RiskPattern.STEPWISE_DECREASING:
            # Decrease in equal steps on the sampled step_days.
            val = self.start_risk
            step = (self.start_risk - self.end_risk) / len(self.step_days)
            for d in self.step_days:
                if day >= d:
                    val -= step

        elif self.pattern == RiskPattern.STEPWISE_INCREASING:
            # Increase in equal steps on the sampled step_days.
            val = self.end_risk
            step = (self.start_risk - self.end_risk) / len(self.step_days)
            for d in self.step_days:
                if day >= d:
                    val += step

        elif self.pattern == RiskPattern.RANDOM_STEPWISE:
            # Linear baseline plus Gaussian noise.
            base = self.start_risk * (1 - t) + self.end_risk * t
            val = base + self._rng.normalvariate(0, self.noise_std)

        else:
            raise ValueError("Unsupported risk pattern")

        # Enforce α ∈ [0, 1] to keep downstream pricing logic stable.
        return max(0.0, min(1.0, val))
