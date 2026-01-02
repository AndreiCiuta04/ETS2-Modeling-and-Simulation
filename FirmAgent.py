class FirmAgent:
    """
    Represents a single firm participating in the emissions allowance market.

    A FirmAgent holds allowances, produces emissions, observes the market,
    and decides whether to buy, sell, or hold allowances based on its strategy
    and risk preferences.
    """

    def __init__(
        self,
        agent_id: int,
        allowances: float,
        cash: float,
        emissions_remaining: float,
        risk_aversion: float,
        strategy
    ):
        """
        Initializes a firm agent with its initial state.

        @param agent_id unique identifier of the agent
        @param allowances initial number of allowances owned
        @param cash initial cash balance
        @param emissions_remaining expected future emissions until compliance
        @param risk_aversion parameter controlling tolerance to uncertainty
        @param strategy trading strategy used by the agent
        """
        pass

    """
    Determines the agent's trading action for the current time step.

    The agent observes the current market state and, based on its internal
    state and trading strategy, decides whether to:
    - submit a buy order
    - submit a sell order
    - take no action

    @param market a snapshot of the current market state
    @param t current simulation time step
    @return an Order object if the agent trades, or None otherwise
    """
    def decide(self, market, t: int):
        pass

    """
    Updates the agent's internal state after a trade has been executed.

    This includes:
    - adjusting allowance holdings
    - adjusting cash balance

    This method is called only when the agent participated in the trade.

    @param trade the executed trade involving this agent
    @return None
    """
    def apply_trade(self, trade) -> None:
        pass

    """
    Updates the agent's expected remaining emissions.

    This method may be called once per time step to account for
    realized emissions or updated forecasts.

    @param amount emissions realized during the current time step
    @return None
    """
    def update_emissions(self, amount: float) -> None:
        pass

    """
    Computes the agent's current compliance gap.

    The compliance gap is defined as:
    expected remaining emissions minus current allowance holdings.

    A positive value indicates a need to buy allowances.
    A negative value indicates excess allowances available for sale.

    @return the current compliance gap
    """
    def compliance_gap(self) -> float:
        pass
