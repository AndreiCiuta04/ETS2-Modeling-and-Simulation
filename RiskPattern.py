from enum import Enum, auto


class RiskPattern(Enum):
    """
    Enumeration of time-dependent risk (aggressiveness) patterns.
    """

    CONSTANT = auto()
    """Risk remains constant over time."""

    LINEAR_DECREASING = auto()
    """Risk decreases linearly over the year."""

    LINEAR_INCREASING = auto()
    """Risk increases linearly over the year."""

    CONCAVE_DECREASING = auto()
    """Risk drops quickly early and flattens later."""

    CONVEX_DECREASING = auto()
    """Risk decreases slowly early and sharply near the end."""

    STEPWISE_DECREASING = auto()
    """Risk decreases in discrete steps."""

    STEPWISE_INCREASING = auto()
    """Risk increases in discrete steps."""

    RANDOM_STEPWISE = auto()
    """Risk follows a noisy, irregular stepwise trajectory."""
