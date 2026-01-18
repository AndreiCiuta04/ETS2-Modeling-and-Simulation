import math
import random
from RiskPattern import RiskPattern


class Risk:
    """
    Represents a time-dependent risk (aggressiveness) profile.

    Risk governs how strongly a firm adjusts its bid or ask
    relative to economic valuation and regulatory anchors.
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
        Initializes a risk trajectory.

        :param pattern: selected RiskPattern
        :param start_risk: initial aggressiveness
        :param end_risk: final aggressiveness
        :param horizon: number of simulation days
        :param seed: optional RNG seed
        :param n_steps: number of steps for stepwise patterns
        :param noise_std: volatility for random pattern
        """
        self.pattern = pattern
        self.start_risk = float(start_risk)
        self.end_risk = float(end_risk)
        self.horizon = int(horizon)
        self.n_steps = max(1, int(n_steps))
        self.noise_std = float(noise_std)

        self._rng = random.Random(seed)

        if self.horizon > 1:
            self.step_days = sorted(
                self._rng.sample(range(1, self.horizon), k=min(self.n_steps, self.horizon - 1))
            )
        else:
            self.step_days = []

    def value(self, day: int) -> float:
        """
        Returns the risk level α(t) for a given day.

        :param day: current simulation day (1-based)
        :return: aggressiveness α(t) ∈ [0, 1]
        """
        day = max(1, min(day, self.horizon))
        t = day / self.horizon

        if self.pattern == RiskPattern.CONSTANT:
            val = self.start_risk

        elif self.pattern == RiskPattern.LINEAR_DECREASING:
            val = self.start_risk * (1 - t) + self.end_risk * t

        elif self.pattern == RiskPattern.LINEAR_INCREASING:
            val = self.end_risk * (1 - t) + self.start_risk * t

        elif self.pattern == RiskPattern.CONCAVE_DECREASING:
            val = self.start_risk * (1 - math.sqrt(t)) + self.end_risk * math.sqrt(t)

        elif self.pattern == RiskPattern.CONVEX_DECREASING:
            val = self.start_risk * (1 - t ** 2) + self.end_risk * (t ** 2)

        elif self.pattern == RiskPattern.STEPWISE_DECREASING:
            val = self.start_risk
            step = (self.start_risk - self.end_risk) / len(self.step_days)
            for d in self.step_days:
                if day >= d:
                    val -= step

        elif self.pattern == RiskPattern.STEPWISE_INCREASING:
            val = self.end_risk
            step = (self.start_risk - self.end_risk) / len(self.step_days)
            for d in self.step_days:
                if day >= d:
                    val += step

        elif self.pattern == RiskPattern.RANDOM_STEPWISE:
            base = self.start_risk * (1 - t) + self.end_risk * t
            val = base + self._rng.normalvariate(0, self.noise_std)

        else:
            raise ValueError("Unsupported risk pattern")

        return max(0.0, min(1.0, val))
