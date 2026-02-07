from mesa import Agent
from DataStructures import Decision
from Risk import Risk
import random


class FirmAgent(Agent):
    """
    Firm agent matching the LaTeX model.

    - deterministic daily emissions: e_{j,t} = X_{j,t} * phi_j
    - forecast position: AP_{j,t} = cum_emissions + (T - t) * e_{j,t}
    - net position: gap = AP_{j,t} - A_{j,t}
    - quantity: Q = |gap| / (T - t)
    - reservation price: PV_{j,t} = (P_j - C_{j,t}) / phi_j  (deterministic)
    - daily profit: π_{j,t} = X(P-C) - q_traded_today * P_clear,t
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
        super().__init__(model)
        self.unique_id = unique_id

        self.P_j = float(product_price)
        self.X_j = float(initial_production)
        self.phi_j = float(carbon_intensity)
        self.C_j = float(cost)
        self.risk = risk
        self.allowances = float(allowances)

        self.cum_emissions = 0.0

        # daily trading result & profit tracking (needed for LaTeX π_{j,t})
        self.q_traded_today = 0.0  # signed: +buy, -sell
        self.daily_profit = 0.0
        self.prev_daily_profit = 0.0

        # cumulative profit (for reporting)
        self.profit = 0.0

        self.decision = None

    def decide(self):
        """
        Determines the firm's trading decision for the day.
        """

        # 1) Daily emissions
        e_jt = self.X_j * self.phi_j
        self.cum_emissions += e_jt

        # 2) Remaining days (T - t) exactly as in LaTeX
        remaining_days = self.model.horizon - self.model.day

        # If remaining_days == 0, LaTeX Q=gap/(T-t) would divide by 0 -> submit no order.
        if remaining_days <= 0:
            self.decision = None
            return

        # 3) Forecast annual position
        AP_jt = self.cum_emissions + remaining_days * e_jt
        gap = AP_jt - self.allowances

        # 4) Dynamic penalty floor S_t = (t/T) * Π
        S_t = (self.model.day / self.model.horizon) * self.model.penalty

        # 5) Reservation price PV_{j,t} (deterministic)
        reservation_price = (self.P_j - self.C_j) / self.phi_j
        reservation_price = max(reservation_price, 0.0)

        # 6) Risk-adjusted price vs last clearing price
        market_price = self.model.market.last_price
        alpha = self.risk.value(self.model.day)
        P_last = market_price if market_price is not None else reservation_price

        if gap > 0:
            # BUY
            side = "buy"
            qty = gap / remaining_days

            P_temp = min(
                reservation_price - alpha * (reservation_price - P_last),
                reservation_price,
            )
            price = max(P_temp, S_t)

        else:
            # SELL
            side = "sell"
            qty = (-gap) / remaining_days

            price = max(
                reservation_price - alpha * (reservation_price - P_last),
                reservation_price,
            )

        self.decision = Decision(
            agent_id=self.unique_id,
            side=side,
            quantity=max(qty, 0.0),
            price=max(price, 0.0),
        )

    def post_trade(self):
        """
        Applies daily profit and production adaptation.

        LaTeX daily profit:
          π_{j,t} = X(P - C) - q_traded_today * P_clear,t
        """
        P_clear = self.model.market.last_price if self.model.market.last_price is not None else 0.0

        self.prev_daily_profit = self.daily_profit
        self.daily_profit = self.X_j * (self.P_j - self.C_j) - (self.q_traded_today * P_clear)

        # accumulate
        self.profit += self.daily_profit

        # Production adaptation based on DAILY profit
        delta = self.model.delta
        dx = abs(random.normalvariate(0, self.model.production_std))

        if self.daily_profit > self.prev_daily_profit * (1 + delta):
            self.X_j *= (1 + dx)
        elif self.daily_profit < self.prev_daily_profit * (1 - delta):
            self.X_j *= (1 - dx)

        # Cost shock for next day
        epsilon = random.normalvariate(0, self.model.cost_shock_std)
        self.C_j *= (1 + epsilon)
