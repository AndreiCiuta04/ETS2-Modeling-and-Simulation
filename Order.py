class Order:
    """
    Represents a trading instruction submitted by an agent to the market.

    An Order expresses intent only.
    It does not guarantee execution.
    """

    """
    Initializes an order submitted by an agent.

    @param agent_id identifier of the submitting agent
    @param side BUY or SELL
    @param quantity number of allowances to trade
    @param limit_price maximum (BUY) or minimum (SELL) acceptable price;
                        None indicates a market order
    """
    def __init__(
        self,
        agent_id: int,
        side,
        quantity: float,
        limit_price: float | None
    ):
        pass
