class OrderBook:
    """
    Stores outstanding buy and sell orders submitted to the market.

    The OrderBook does not execute trades or apply matching logic.
    It only maintains collections of orders.
    """

    """
    Initializes an empty order book.

    Creates separate containers for buy orders (bids)
    and sell orders (asks).
    """
    def __init__(self):
        self.bids = []
        self.asks = []
