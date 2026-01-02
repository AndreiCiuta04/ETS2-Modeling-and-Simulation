class Market:
    """
    Represents the trading environment in which agents submit orders
    and trades are executed.

    The Market owns the order book, matches orders, records trades,
    and maintains the current market price.
    """

    def __init__(self, initial_price: float):
        """
        Initializes the market.

        @param initial_price starting price of allowances
        """
        self.last_price = initial_price
        self.order_book = None
        self.trade_log = []

    """
    Submits an order to the market.

    The order is added to the order book but not executed immediately.
    Execution occurs when match_orders() is called.

    @param order the order submitted by an agent
    @return None
    """
    def submit_order(self, order):
        pass

    """
    Matches buy and sell orders stored in the order book.

    This method applies the market's matching rules, generates trades,
    updates the last traded price, and records executed trades.

    @return None
    """
    def match_orders(self) -> None:
        pass

    """
    Returns a snapshot of the current market state.

    The returned MarketState contains summary information such as
    price, best bid, best ask, volume, and volatility.

    Agents use this information to make trading decisions.

    @return MarketState
    """
    def get_state(self):
        pass
