from DataStructures import Trade, Decision


class Market:
    """
    Represents the allowance trading market.

    The market collects firm decisions, matches compatible
    buy and sell orders, and produces a daily allowance price.

    The market has no strategic behavior.
    """

    def __init__(self, initial_price: float | None = None):
        """
        Initializes the market.

        :param initial_price: optional starting allowance price
        """
        self.last_price = initial_price
        self.daily_volume = 0.0

        self.price_history = []
        self.volume_history = []

    def clear(self, decisions):
        """
        Clears the market for a single trading day.

        Market clearing means:
        - sorting buy orders by descending price,
        - sorting sell orders by ascending price,
        - matching orders while bids ≥ asks,
        - determining transaction prices,
        - updating the market-clearing price.
        """
        buys = [d for d in decisions if d and d.side == "buy" and d.quantity > 0]
        sells = [d for d in decisions if d and d.side == "sell" and d.quantity > 0]

        buys.sort(key=lambda d: d.price, reverse=True)
        sells.sort(key=lambda d: d.price)

        trades = []
        self.daily_volume = 0.0

        i = j = 0

        while i < len(buys) and j < len(sells) and buys[i].price >= sells[j].price:
            buy, sell = buys[i], sells[j]
            qty = min(buy.quantity, sell.quantity)
            price = 0.5 * (buy.price + sell.price)

            trades.append(Trade(buy.agent_id, sell.agent_id, qty, price))
            self.daily_volume += qty
            self.last_price = price

            buys[i] = Decision(buy.agent_id, buy.side, buy.quantity - qty, buy.price)
            sells[j] = Decision(sell.agent_id, sell.side, sell.quantity - qty, sell.price)

            if buys[i].quantity <= 1e-12:
                i += 1
            if sells[j].quantity <= 1e-12:
                j += 1

        self.price_history.append(self.last_price if self.last_price is not None else 0.0)
        self.volume_history.append(self.daily_volume)

        return trades
