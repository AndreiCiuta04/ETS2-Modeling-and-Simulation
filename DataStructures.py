from dataclasses import dataclass
"""
Shared immutable data structures used across the ETS simulation.

These dataclasses represent the "messages" exchanged between agents and the market:
- Decision: a limit order submitted by an agent (buy/sell, quantity, price)
- Trade: an executed transaction after market clearing
"""

@dataclass(frozen=True)
class Decision:
    """
        Represents a limit order submitted by a firm.

        Attributes:

        agent_id:
            Unique firm identifier.
        side:
            Either "buy" or "sell".
        quantity:
            Order volume in allowances (tons CO2).
        price:
            Limit price for the order.
        """
    agent_id: int
    side: str
    quantity: float
    price: float


@dataclass(frozen=True)
class Trade:
    """
        Represents an executed trade between two firms.

        Attributes:

        buyer_id:
            Firm id of the buyer.
        seller_id:
            Firm id of the seller.
        quantity:
            Executed volume in allowances.
        price:
            Execution price (uniform daily clearing price).
        """
    buyer_id: int
    seller_id: int
    quantity: float
    price: float
