from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    """
    Represents a limit order submitted by a firm.
    """
    agent_id: int
    side: str
    quantity: float
    price: float


@dataclass(frozen=True)
class Trade:
    """
    Represents an executed trade between two firms.
    """
    buyer_id: int
    seller_id: int
    quantity: float
    price: float
