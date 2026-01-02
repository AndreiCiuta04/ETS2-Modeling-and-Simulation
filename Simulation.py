class Simulation:
    """
    Controls the execution of the simulation.

    The Simulation advances time, coordinates agent actions,
    applies shocks, and triggers market clearing.
    """

    def __init__(
        self,
        agents: list,
        market,
        shock_process,
        end_time: int,
        rng_seed: int
    ):
        """
        Initializes the simulation with its components.

        @param agents list of firm agents participating in the simulation
        @param market the market in which agents trade
        @param shock_process source of shocks
        @param end_time final simulation time step
        @param rng_seed random seed for reproducibility
        """
        pass

    """
    Runs the simulation from the initial time until the end time.

    This method repeatedly calls step() until the simulation
    reaches the specified end time.

    @return None
    """
    def run(self) -> None:
        pass

    """
    Executes a single simulation time step.

    A typical step includes:
    - applying exogenous shocks
    - collecting orders from agents
    - submitting orders to the market
    - matching orders and executing trades
    - advancing the simulation time

    @return None
    """
    def step(self) -> None:
        pass
