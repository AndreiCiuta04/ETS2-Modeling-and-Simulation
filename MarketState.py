class MarketState:
    """
    Represents a snapshot of the current market state.

    MarketState provides limited, read-only information to agents
    so they can make trading decisions.
    """

    """
    Initializes a market state snapshot.

    @param last_price most recent trade price
    @param best_bid highest outstanding buy price
    @param best_ask lowest outstanding sell price
    @param volume trading volume in the current time step
    @param volatility measure of recent price variability
    """
    def __init__(
        self,
        last_price: float,
        best_bid: float | None,
        best_ask: float | None,
        volume: float,
        volatility: float
    ):
        pass
