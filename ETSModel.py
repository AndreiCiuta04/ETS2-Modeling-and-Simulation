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
        firm_params,
        risk_objects,
        penalty,
        horizon,
        initial_market_price=None,
        reservation_price_std=0.05,  # kept for compatibility (unused now)
        production_std=0.03,
        cost_shock_std=0.02,
        delta=0.02,
    ):
        super().__init__()

        # Global parameters
        self.horizon = int(horizon)
        self.day = 0
        self.penalty = float(penalty)

        # Parameters used by FirmAgent
        self.reservation_price_std = reservation_price_std
        self.production_std = production_std
        self.cost_shock_std = cost_shock_std
        self.delta = delta

        # Market
        self.market = Market(initial_market_price)

        # Firms
        self.firms = {}
        for i, (ic, params, risk) in enumerate(zip(initial_conditions, firm_params, risk_objects)):
            self.firms[i] = FirmAgent(
                unique_id=i,
                model=self,
                product_price=params["price"],
                initial_production=params["initial_production"],
                carbon_intensity=params["phi_j"],
                cost=params["cost"],
                allowances=params["initial_allowances"],
                risk=risk,
            )

            # NOTE: `ic` is still unused (same as your original code).
            # If your LaTeX claims firms are initialized using this real-data series,
            # tell me what `ic` represents (baseline emissions? production?) and I’ll wire it in.

    def step(self):
        """
        Executes one trading day.
        """
        self.day += 1

        # reset daily trade accounting needed for π_{j,t}
        for firm in self.firms.values():
            firm.q_traded_today = 0.0

        # decisions
        for firm in self.firms.values():
            firm.decide()

        # market clearing
        trades = self.market.clear([f.decision for f in self.firms.values()])
        self._apply_trades(trades)

        # post-trade updates (profit + production + cost shock)
        for firm in self.firms.values():
            firm.post_trade()

        # end-of-year penalty
        if self.day >= self.horizon:
            self._apply_terminal_penalty()

    def _apply_trades(self, trades):
        """
        Transfers allowances and records traded quantity.
        Profit is computed in FirmAgent.post_trade() via π_{j,t}.
        """
        for t in trades:
            buyer = self.firms[t.buyer_id]
            seller = self.firms[t.seller_id]

            buyer.allowances += t.quantity
            seller.allowances -= t.quantity

            # Signed traded quantity for π_{j,t}
            buyer.q_traded_today += t.quantity
            seller.q_traded_today -= t.quantity

    def _apply_terminal_penalty(self):
        """
        Applies end-of-year compliance penalties.
        """
        for firm in self.firms.values():
            shortfall = max(firm.cum_emissions - firm.allowances, 0.0)
            firm.profit -= shortfall * self.penalty
