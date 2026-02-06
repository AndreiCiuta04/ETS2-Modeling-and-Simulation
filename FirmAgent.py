from mesa import Agent
from DataStructures import Decision
from Risk import Risk
import random


class FirmAgent(Agent):
    """
    Represents a regulated firm participating in the ETS.

    Each firm:
    - emits CO2 at a fixed daily rate,
    - forecasts compliance needs over the remaining year,
    - submits one buy or sell order per day,
    - follows a time-dependent risk pattern that governs
      pricing aggressiveness.
    """

    def __init__(
        self,
        unique_id,
        model,
        daily_emissions,
        product_price,
        cost,
        risk: Risk,
        allowances,
    ):
        """
        Initializes a firm agent.

        :param unique_id: unique firm identifier (managed explicitly)
        :param model: reference to the ETSModel
        :param daily_emissions: fixed daily CO2 emissions
        :param product_price: output price (proxy for value creation)
        :param cost: marginal production cost
        :param risk: Risk object defining aggressiveness over time
        :param allowances: initial allowance holdings
        """
        # Mesa 3.x-compatible initialization
        super().__init__(model)
        self.unique_id = unique_id

        self.daily_emissions = float(daily_emissions)
        self.product_price = float(product_price)
        self.cost = float(cost)
        self.risk = risk
        self.allowances = float(allowances)

        self.cum_emissions = 0.0
        self.profit = 0.0
        self.decision = None

    def decide(self):
        """
        Determines the firm's trading decision for the day.

        Economic interpretation:
        - emissions are realized deterministically,
        - total emissions are forecast over the remaining year,
        - the firm compares forecasted emissions to allowances,
        - a buy or sell decision is formed,
        - the limit price is adjusted according to risk.
        """

        # 1. Emit CO2
        self.cum_emissions += self.daily_emissions

        # 2. Forecast end-of-year emissions
        remaining_days = max(self.model.horizon - self.model.day, 1)
        forecast = self.cum_emissions + remaining_days * self.daily_emissions
        gap = forecast - self.allowances

        # 3. Risk-dependent aggressiveness
        alpha = self.risk.value(self.model.day)

        # 4. Noisy economic valuation
        valuation = (
            self.model.base_value_price
            * (1 + random.normalvariate(0, self.model.value_shock_std))
        )

        # 5. Regulatory penalty anchor
        penalty_anchor = (
            (self.model.day / self.model.horizon)
            * self.model.penalty
            * (1 + random.normalvariate(0, self.model.anchor_shock_std))
        )

        reservation_price = valuation
        market_price = self.model.market.last_price
        # 6. Trading decision
        if gap > 0:
            # Needs allowances → buy NEW!
            if gap > 0:
                # Needs allowances → buy
                side = "buy"
                qty = (gap / remaining_days) * self.model.trade_fraction

                if market_price is not None and market_price < reservation_price:
                    price = reservation_price - alpha * abs(reservation_price - market_price)
                else:
                    price = reservation_price



            price = max(price, penalty_anchor)


        else:
            # Excess allowances → sell
            side = "sell"
            qty = (-gap / remaining_days) * self.model.trade_fraction

            if market_price is not None and market_price > reservation_price:
                price = reservation_price + alpha * abs(reservation_price - market_price)
            else:
                price = reservation_price




        '''
            # 6. Trading decision
            if gap > 0:
                # Needs allowances → buy
                side = "buy"
                qty = (gap / remaining_days) * self.model.trade_fraction
    
                price = max(
                    penalty_anchor + alpha * (valuation - penalty_anchor),
                    penalty_anchor,
                )
    
            else:
                # Excess allowances → sell
                side = "sell"
                qty = (-gap / remaining_days) * self.model.trade_fraction
    
                anchor = self.model.market.last_price or valuation
                price = anchor + alpha * (valuation - anchor)
            '''


        self.decision = Decision(
            agent_id=self.unique_id,
            side=side,
            quantity=max(qty, 0.0),
            price=max(price, 0.0),
            )

    def post_trade(self):
        """
        Applies operating profit after trading.

        This represents non-ETS profit flows and keeps
        trading profits and production profits separated.
        """
        self.profit += self.product_price - self.cost
