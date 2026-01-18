from mesa import Model
from Market import Market
from FirmAgent import FirmAgent


class ETSModel(Model):
    """
    Mesa model orchestrating the ETS simulation.
    """

    def __init__(
        self,
        initial_conditions,
        risk_objects,
        penalty,
        horizon,
        base_value_price=65.0,
        trade_fraction=1.0,
        value_shock_std=0.05,
        anchor_shock_std=0.03,
        initial_market_price=None,
        product_price=55.0,
        cost=25.0,
    ):
        super().__init__()

        self.horizon = int(horizon)
        self.day = 0
        self.penalty = float(penalty)

        self.base_value_price = base_value_price
        self.trade_fraction = trade_fraction
        self.value_shock_std = value_shock_std
        self.anchor_shock_std = anchor_shock_std

        self.market = Market(initial_market_price)
        self.firms = {}

        for i, (ic, risk) in enumerate(zip(initial_conditions, risk_objects)):
            daily_emissions = ic["annual_emissions"] / self.horizon

            self.firms[i] = FirmAgent(
                unique_id=i,
                model=self,
                daily_emissions=daily_emissions,
                product_price=product_price,
                cost=cost,
                risk=risk,
                allowances=ic["initial_allowances"],
            )

    def step(self):
        """
        Executes one trading day.
        """
        self.day += 1

        for firm in self.firms.values():
            firm.decide()

        trades = self.market.clear([f.decision for f in self.firms.values()])
        self._apply_trades(trades)

        for firm in self.firms.values():
            firm.post_trade()

        if self.day >= self.horizon:
            self._apply_terminal_penalty()

    def _apply_trades(self, trades):
        """
        Transfers allowances and money between firms.
        """
        for t in trades:
            self.firms[t.buyer_id].allowances += t.quantity
            self.firms[t.seller_id].allowances -= t.quantity

            cash = t.quantity * t.price
            self.firms[t.buyer_id].profit -= cash
            self.firms[t.seller_id].profit += cash

    def _apply_terminal_penalty(self):
        """
        Applies end-of-year compliance penalties.
        """
        for firm in self.firms.values():
            shortfall = max(firm.cum_emissions - firm.allowances, 0.0)
            firm.profit -= shortfall * self.penalty
