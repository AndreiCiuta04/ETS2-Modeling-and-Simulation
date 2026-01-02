class Trade:
    """
    Represents an executed transaction between two agents.

    A Trade is created by the market when a buy order and a sell
    order are successfully matched.
    """

    """
    Initializes a trade record.

    @param price execution price of the trade
    @param quantity number of allowances exchanged
    @param buyer_id identifier of the buying agent
    @param seller_id identifier of the selling agent
    @param time simulation time at which the trade occurred
    """
    def __init__(
        self,
        price: float,
        quantity: float,
        buyer_id: int,
        seller_id: int,
        time: int
    ):
        pass
