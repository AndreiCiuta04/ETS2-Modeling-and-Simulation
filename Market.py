from DataStructures import Trade, Decision
"""
Market clearing mechanism for the ETS allowance trading model.

Implements a uniform-price double auction consistent with the LaTeX specification:
- Sort buy orders descending by price
- Sort sell orders ascending by price
- Find the last crossing index k with bid[k] >= ask[k]
- Set daily clearing price to the midpoint of the marginal pair:
      P_clear = (bid[k] + ask[k]) / 2
- Execute trades at the ONE daily clearing price (allowing partial fills)
"""

class Market:
    """
    Represents the allowance trading market.

    Clearing mechanism (matches LaTeX uniform-price double auction):
    - sort buy orders by descending price
    - sort sell orders by ascending price
    - find the last index k such that bid[k] >= ask[k]
    - set P_clear = (bid[k] + ask[k]) / 2
    - execute matched trades at that same P_clear
    """

    def __init__(self, initial_price: float | None = None):
        self.last_price = initial_price
        self.daily_volume = 0.0
        self.price_history = []
        self.volume_history = []

    def clear(self, decisions):
        """
        Clears the market for a single trading day and returns executed trades.
        """
        buys = [d for d in decisions if d and d.side == "buy" and d.quantity > 0]
        sells = [d for d in decisions if d and d.side == "sell" and d.quantity > 0]

        buys.sort(key=lambda d: d.price, reverse=True)
        sells.sort(key=lambda d: d.price)

        trades = []
        self.daily_volume = 0.0

        # No orders -> no trade; keep last_price
        if not buys or not sells:
            self.price_history.append(self.last_price if self.last_price is not None else 0.0)
            self.volume_history.append(self.daily_volume)
            return trades

        # Find marginal crossing index k (largest idx with bid >= ask)
        k = -1
        max_pairs = min(len(buys), len(sells))
        for idx in range(max_pairs):
            if buys[idx].price >= sells[idx].price:
                k = idx
            else:
                break

        # No crossing -> no trades; keep last_price
        if k == -1:
            self.price_history.append(self.last_price if self.last_price is not None else 0.0)
            self.volume_history.append(self.daily_volume)
            return trades

        # Uniform clearing price from marginal pair
        P_clear = 0.5 * (buys[k].price + sells[k].price)

        # Execute at ONE daily price, allowing partial fills, limited to the crossing set 0..k
        i = j = 0
        while i <= k and j <= k:
            buy, sell = buys[i], sells[j]
            qty = min(buy.quantity, sell.quantity)

            if qty <= 1e-12:
                if buy.quantity <= 1e-12:
                    i += 1
                if sell.quantity <= 1e-12:
                    j += 1
                continue

            trades.append(Trade(buy.agent_id, sell.agent_id, qty, P_clear))
            self.daily_volume += qty

            # reduce remaining quantities (keep original limit prices)
            buys[i] = Decision(buy.agent_id, buy.side, buy.quantity - qty, buy.price)
            sells[j] = Decision(sell.agent_id, sell.side, sell.quantity - qty, sell.price)

            if buys[i].quantity <= 1e-12:
                i += 1
            if sells[j].quantity <= 1e-12:
                j += 1

        self.last_price = P_clear

        self.price_history.append(self.last_price if self.last_price is not None else 0.0)
        self.volume_history.append(self.daily_volume)
        return trades
