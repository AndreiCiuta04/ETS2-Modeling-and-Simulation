from mesa import Model
from Market import Market
from FirmAgent import FirmAgent


class ETSModel(Model):
    """
    Mesa model orchestrating the ETS simulation.

    The model owns:
    - global simulation parameters (horizon, penalty, etc.)
    - the market mechanism
    - the set of firm agents and the daily stepping logic
    """

    def __init__(
        self,
        initial_conditions,
        firm_params,
        risk_objects,
        penalty,
        horizon,
        initial_market_price=None,
        reservation_price_std=0.05, #cant remove it
        production_std=0.03,
        cost_shock_std=0.02,
        delta=0.02,
    ):
        """
        Initializes the ETS model, creates the market, and instantiates all firm agents.

        @param initial_conditions: Per-firm initial condition dicts (currently unused in core logic).
        @param firm_params: Per-firm economic parameters (price, production, phi_j, cost, allowances).
        @param risk_objects: Per-firm Risk objects controlling penalty expectation / risk schedule.
        @param penalty: End-of-year penalty price per unit of emissions shortfall.
        @param horizon: Number of trading days in the simulated year.
        @param initial_market_price: Optional initial price used by the market before any trades.
        @param reservation_price_std: Std for reservation price shocks (currently unused).
        @param production_std: Std for production shocks applied inside the agent.
        @param cost_shock_std: Std for cost shocks applied inside the agent.
        @param delta: Discount/adjustment parameter used in agent decision logic (agent-side meaning).
        """
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

        # Firms (indexed by agent id)
        self.firms = {}
        for i, (ic, params, risk) in enumerate(
            zip(initial_conditions, firm_params, risk_objects)
        ):
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


    def step(self):
        """
        Executes one trading day:
        - firms compute their decisions (orders)
        - market clears and produces trades
        - trades are applied (allowances + traded quantity accounting)
        - firms update internal state (profit, production, etc.)
        - if this is the terminal day, apply compliance penalties
        """
        self.day += 1

        # Reset daily traded quantity
        for firm in self.firms.values():
            firm.q_traded_today = 0.0

        # Firms decide what orders to submit (Decision objects or None).
        for firm in self.firms.values():
            firm.decide()

        # Market clearing based on all submitted decisions.
        trades = self.market.clear([f.decision for f in self.firms.values()])
        self._apply_trades(trades)

        # Post-trade state updates inside each firm (profit, production shocks, etc.).
        for firm in self.firms.values():
            firm.post_trade()

        # End-of-year compliance check.
        if self.day >= self.horizon:
            self._apply_terminal_penalty()

    def _apply_trades(self, trades):
        """
        Applies executed trades:
        - transfers allowances between buyer and seller
        - records signed traded quantity for each firm (used later in profit accounting)

        @param trades: List of Trade objects returned by the market clearing mechanism.
        @return None
        """
        for t in trades:
            buyer = self.firms[t.buyer_id]
            seller = self.firms[t.seller_id]

            buyer.allowances += t.quantity
            seller.allowances -= t.quantity

            buyer.q_traded_today += t.quantity
            seller.q_traded_today -= t.quantity

    def _apply_terminal_penalty(self):
        """
        Applies end-of-year compliance penalties based on emissions shortfall.

        If cum_emissions > allowances, the difference is penalized at `self.penalty`.
        """
        for firm in self.firms.values():
            shortfall = max(firm.cum_emissions - firm.allowances, 0.0)
            firm.profit -= shortfall * self.penalty
