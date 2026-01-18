import os
import random
import matplotlib.pyplot as plt

from DataProcessor import DataProcessor
from ETSModel import ETSModel
from Risk import Risk
from RiskPattern import RiskPattern
from run import run_model


def build_initial_conditions_with_fixed_cap(emissions, cap_fraction=0.9, weight_sigma=0.6):
    """
    Builds initial_conditions while keeping emissions unchanged.

    - Total allowances = cap_fraction * total_emissions
    - Allocation is heterogeneous using random weights so that
      some firms receive more than their emissions (sellers) and
      some receive less (buyers).

    :param emissions: list of annual emissions (empirical)
    :param cap_fraction: total allowances fraction of total emissions
    :param weight_sigma: dispersion of allocation weights (higher => more heterogeneity)
    :return: list of dicts: {"annual_emissions": e, "initial_allowances": a}
    """
    total_emissions = sum(emissions)
    total_allowances = cap_fraction * total_emissions

    weights = [random.lognormvariate(0, weight_sigma) for _ in emissions]
    w_sum = sum(weights)

    initial_conditions = []
    for e, w in zip(emissions, weights):
        a = total_allowances * (w / w_sum)
        initial_conditions.append({"annual_emissions": e, "initial_allowances": a})

    return initial_conditions


def main():
    # -----------------------------
    # Simulation parameters
    # -----------------------------
    horizon = 365
    penalty = 100.0

    # -----------------------------
    # Load emissions data (empirical)
    # -----------------------------
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "Emission Data.csv")

    processor = DataProcessor()
    processor.load_emissions_csv(csv_path)
    processor.validate()

    emissions = processor.emissions
    n_agents = len(emissions)

    print(f"Loaded {n_agents} agents from data.")

    # -----------------------------
    # Build initial allowances:
    # emissions unchanged, cap fixed, allocation heterogeneous
    # -----------------------------
    initial_conditions = build_initial_conditions_with_fixed_cap(
        emissions=emissions,
        cap_fraction=0.9,
        weight_sigma=0.6,  # increase for more heterogeneity/volatility
    )

    # -----------------------------
    # Random risk assignment
    # -----------------------------
    available_patterns = [
        RiskPattern.CONSTANT,
        RiskPattern.LINEAR_DECREASING,
        RiskPattern.CONCAVE_DECREASING,
        RiskPattern.CONVEX_DECREASING,
        RiskPattern.STEPWISE_DECREASING,
        RiskPattern.RANDOM_STEPWISE,
    ]

    risk_objects = []
    for i in range(n_agents):
        pattern = random.choice(available_patterns)
        start_risk = random.uniform(0.6, 0.9)
        end_risk = random.uniform(0.1, start_risk)

        risk_objects.append(
            Risk(
                pattern=pattern,
                start_risk=start_risk,
                end_risk=end_risk,
                horizon=horizon,
                seed=1000 + i,
                n_steps=random.randint(3, 7),
            )
        )

    # -----------------------------
    # Create and run model
    # -----------------------------
    model = ETSModel(
        initial_conditions=initial_conditions,
        risk_objects=risk_objects,
        penalty=penalty,
        horizon=horizon,
        base_value_price=65.0,
        trade_fraction=1.0,
        value_shock_std=0.05,
        anchor_shock_std=0.03,
        initial_market_price=65.0,
        product_price=55.0,
        cost=25.0,
    )

    run_model(model, horizon)

    # -----------------------------
    # Plot price path
    # -----------------------------
    plt.figure(figsize=(10, 5))
    plt.plot(model.market.price_history, label="Allowance price")
    plt.xlabel("Day")
    plt.ylabel("Price")
    plt.title("ETS Allowance Price Over Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -----------------------------
    # Print final results + risk strategies
    # -----------------------------
    print("\n=== FINAL AGENT RESULTS (WITH RISK) ===")
    for agent_id, firm in model.firms.items():
        r = firm.risk
        print(
            f"Agent {agent_id:3d} | "
            f"Pattern={r.pattern.name:18s} | "
            f"start={r.start_risk:.2f} end={r.end_risk:.2f} | "
            f"Profit={firm.profit:12.2f} | "
            f"Allowances={firm.allowances:12.2f} | "
            f"Emissions={firm.cum_emissions:12.2f}"
        )

    print("\nFinal market price:", model.market.last_price)
    print("Final daily volume:", model.market.daily_volume)


if __name__ == "__main__":
    main()
