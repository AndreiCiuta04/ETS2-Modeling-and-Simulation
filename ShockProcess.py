class ShockProcess:
    """
    Generates exogenous shocks affecting the market and agents.

    The ShockProcess models random external events such as
    policy changes, weather effects, or macroeconomic disturbances.
    """

    def __init__(
        self,
        volatility: float,
        jump_probability: float
    ):
        """
        Initializes the shock process.

        @param volatility controls the magnitude of continuous shocks
        @param jump_probability probability of a discrete jump shock
        """
        self.volatility = volatility
        self.jump_probability = jump_probability

    """
    Generates a shock realization for the given time step.

    This method samples a random disturbance and returns a Shock
    object describing its impact.

    The shock is not applied here; it is applied by the Simulation
    during the execution of a time step.

    @param t current simulation time step
    @return a Shock instance
    """
    def step(self, t: int):
        pass
