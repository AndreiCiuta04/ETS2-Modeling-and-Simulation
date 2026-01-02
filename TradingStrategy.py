class TradingStrategy:
    """
    Defines a decision rule used by a firm agent to determine
    whether to submit a buy or sell order.
    """

    """
    Determines the trading action of an agent at a given time step.

    The strategy observes the agent's internal state and a summary
    of the current market and decides whether to:
    - submit a buy order
    - submit a sell order
    - take no action

    This method must not modify the agent or the market directly.
    It only returns an Order or None.

    @param agent the firm agent using this strategy
    @param market snapshot of the current market state
    @param t current simulation time step
    @return an Order or None
    """
    def decide(self, agent, market, t: int):
        raise NotImplementedError
