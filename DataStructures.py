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
    Limit order submitted by a firm to the market.

    @param agent_id: Unique firm identifier submitting the order.
    @param side: Either "buy" or "sell".
    @param quantity: Order volume in allowances (tons CO2).
    @param price: Limit price of the order.
    """
    agent_id: int
    side: str
    quantity: float
    price: float


@dataclass(frozen=True)
class Trade:
    """
    Executed transaction produced by the market clearing mechanism.

    @param buyer_id: Firm id of the buyer.
    @param seller_id: Firm id of the seller.
    @param quantity: Executed volume in allowances (tons CO2).
    @param price: Execution price (typically the daily uniform clearing price).
    """
    buyer_id: int
    seller_id: int
    quantity: float
    price: float
