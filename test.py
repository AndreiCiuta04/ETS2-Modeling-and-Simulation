import os
import random
import matplotlib.pyplot as plt
import numpy as np

from DataProcessor import DataProcessor
from ETSModel import ETSModel
from Risk import Risk
from RiskPattern import RiskPattern

def main():
    # -----------------------------
    # Simulation parameters
    # -----------------------------
    horizon = 365
    penalty = 100
    n_runs = 10

    all_price_paths = []
    all_volume_paths = []
    final_prices = []

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # -----------------------------
    # Load data
    # -----------------------------
    dp = DataProcessor()

    dp.load_emissions_csv(os.path.join(base_dir, "Emission Data.csv"))
    initial_conditions = dp.derive_initial_conditions()

    firm_params = dp.load_firm_parameters(
        os.path.join(base_dir, "EU ETS 2 real data.csv")
    )

    # ------------------------------------
    # Align datasets after cleaning
    # ------------------------------------
    n_agents = min(len(initial_conditions), len(firm_params))

    initial_conditions = initial_conditions[:n_agents]
    firm_params = firm_params[:n_agents]

    print(f"Using {n_agents} firms after data alignment.")

    # -----------------------------
    # Risk patterns
    # -----------------------------
    available_patterns = [
        RiskPattern.CONSTANT,
        RiskPattern.LINEAR_DECREASING,
        RiskPattern.CONCAVE_DECREASING,
        RiskPattern.CONVEX_DECREASING,
        RiskPattern.STEPWISE_DECREASING,
        RiskPattern.RANDOM_STEPWISE,
    ]

    # -----------------------------
    # Monte Carlo runs
    # -----------------------------
    for run in range(n_runs):

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
                    seed=1000 + i + run * 10_000,
                    n_steps=random.randint(3, 7),
                )
            )

        model = ETSModel(
            initial_conditions=initial_conditions,
            firm_params=firm_params,
            risk_objects=risk_objects,
            penalty=penalty,
            horizon=horizon,
            initial_market_price=40,
            reservation_price_std=0.05,
            production_std=0.03,
            cost_shock_std=0.005,   # 0.2%
            delta=0.02,
        )

        for _ in range(horizon):
            model.step()

        all_price_paths.append(model.market.price_history)
        all_volume_paths.append(model.market.volume_history)
        final_prices.append(model.market.last_price)

    # -----------------------------
    # Aggregate statistics
    # -----------------------------
    mean_price = np.mean(all_price_paths, axis=0)
    std_price = np.std(all_price_paths, axis=0)
    mean_volume = np.mean(all_volume_paths, axis=0)

    # -----------------------------
    # Plot price paths
    # -----------------------------
    plt.figure(figsize=(10, 5))
    plt.plot(mean_price, label="Average price")
    plt.fill_between(
        range(horizon),
        mean_price - std_price,
        mean_price + std_price,
        alpha=0.3,
        label="±1 std",
    )
    plt.xlabel("Day")
    plt.ylabel("Price")
    plt.title("Monte Carlo Average Allowance Price")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -----------------------------
    # Plot volume
    # -----------------------------
    plt.figure(figsize=(10, 5))
    plt.plot(mean_volume, label="Average daily volume")
    plt.xlabel("Day")
    plt.ylabel("Volume")
    plt.title("Average ETS Trading Volume")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -----------------------------
    # Final stats
    # -----------------------------
    print("\nMonte Carlo results:")
    print("Average final price:", np.mean(final_prices))
    print("Std of final price:", np.std(final_prices))
    print("Min final price:", np.min(final_prices))
    print("Max final price:", np.max(final_prices))

    # -----------------------------
    # Final agent snapshot (last run)
    # -----------------------------
    print("\n=== FINAL AGENT RESULTS ===")
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
