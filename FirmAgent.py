from mesa import Agent
from DataStructures import Decision
from Risk import Risk
import random
import math


class FirmAgent(Agent):
    """
    Firm agent implementing the decision logic from the LaTeX model.

    - emits proportionally to production: e_{j,t} = X_{j,t} * phi_j
    - forecasts end-of-year position and trades to close the expected gap
    - chooses a risk-adjusted limit price around a reservation price
    - tracks daily profit and adapts production based on profit changes
    """

    def __init__(
        self,
        unique_id,
        model,
        product_price,
        initial_production,
        carbon_intensity,
        cost,
        risk: Risk,
        allowances,
    ):
        """
        Creates a firm with fixed product parameters and an exogenous risk profile.

        @param unique_id: Integer firm identifier used across the simulation.
        @param model: Reference to the ETSModel instance.
        @param product_price: Output price P_j.
        @param initial_production: Initial production level X_j.
        @param carbon_intensity: Carbon intensity phi_j (tons CO2 per unit output).
        @param cost: Initial marginal cost C_j.
        @param risk: Risk object controlling how aggressively the firm prices orders over time.
        @param allowances: Initial allowance endowment A_{j,0}.
        """
        super().__init__(model)
        self.unique_id = unique_id

        # Firm parameters (kept close to the LaTeX documentation notation for readability)
        self.P_j = float(product_price)
        self.X_j = float(initial_production)
        self.phi_j = float(carbon_intensity)
        self.C_j = float(cost)
        self.risk = risk
        self.allowances = float(allowances)

        # Emissions accumulated
        self.cum_emissions = 0.0

        # Daily trading result & profit tracking
        self.q_traded_today = 0.0  # signed: +buy, -sell
        self.daily_profit = 0.0
        self.prev_daily_profit = 0.0

        # Cumulative profit
        self.profit = 0.0

        # Most recent order submitted to the market (Decision or None)
        self.decision = None

    def decide(self):
        """
        Computes and stores the firm's limit order for the current day.

        The method updates emissions, forecasts the end-of-year allowance gap,
        and submits either a buy or sell Decision with a risk-adjusted limit price.

        @return: None (stores Decision in self.decision)
        """
        # Daily emissions (production and carbon intensity)
        e_jt = self.X_j * self.phi_j
        self.cum_emissions += e_jt

        # Remaining days in the compliance year (T - t)
        remaining_days = self.model.horizon - self.model.day

        # Avoid division by zero quantity formula Q = |gap|/(T-t).
        if remaining_days <= 0:
            self.decision = None
            return

        # Forecast annual position and compute expected shortfall/excess.
        AP_jt = self.cum_emissions + remaining_days * e_jt
        gap = AP_jt - self.allowances  # >0 -> expected shortage -> buy

        # Penalty / floor price term used in pricing logic.
        S_t = math.exp(4.6 * (self.model.day / self.model.horizon))
        # S_t = 100 * math.exp((self.model.day - self.model.horizon)) maybe?

        # Reservation price
        reservation_price = (self.P_j - self.C_j) / self.phi_j
        reservation_price = max(reservation_price, 0.0)

        # Risk-adjusted pricing relative to last clearing price
        market_price = self.model.market.last_price
        alpha = self.risk.value(self.model.day)
        P_last = market_price if market_price is not None else reservation_price

        if gap > 0:
            # BUY: firm expects a shortfall, submits a buy order.
            side = "buy"
            qty = gap / remaining_days

            # Move price toward last price based on risk.
            P_temp = min(
                reservation_price - alpha * (reservation_price - P_last),
                reservation_price,
            )

            # Enforce a lower bound
            price = max(P_temp, S_t)
        else:
            # SELL: firm expects an excess, submits a sell order.
            side = "sell"
            qty = (-gap) / remaining_days

            price = max(
                reservation_price - alpha * (reservation_price - P_last),
                reservation_price,
            )

        # Store the order for the market to read during clearing.
        self.decision = Decision(
            agent_id=self.unique_id,
            side=side,
            quantity=max(qty, 0.0),
            price=max(price, 0.0),
        )

    def post_trade(self):
        """
        Updates profit and adapts production and costs after market clearing.

        - Profit is accumulated into self.profit
        - Production adapts depending on whether profit increased/decreased beyond a threshold.
        - Costs receive an exogenous random shock for the next day.
        """
        P_clear = (
            self.model.market.last_price
            if self.model.market.last_price is not None
            else 0.0
        )

        # Compute daily profit using signed traded quantity (buy positive, sell negative).
        self.prev_daily_profit = self.daily_profit
        self.daily_profit = self.X_j * (self.P_j - self.C_j) - (self.q_traded_today * P_clear)

        # Accumulate
        self.profit += self.daily_profit

        # Production adaptation based on daily profit changes
        delta = self.model.delta
        dx = abs(random.normalvariate(0, self.model.production_std))

        if self.daily_profit > self.prev_daily_profit * (1 + delta):
            self.X_j *= (1 + dx)
        elif self.daily_profit < self.prev_daily_profit * (1 - delta):
            self.X_j *= (1 - dx)

        # Cost shock for next day
        epsilon = random.normalvariate(0, self.model.cost_shock_std)
        self.C_j *= (1 + epsilon)
