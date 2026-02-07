import csv
import pandas as pd


class DataProcessor:
    """
    Handles empirical data ingestion for the ETS model.

    Responsibilities:
    - load annual emissions (for forecasting & penalties)
    - load firm-level economic parameters
    - keep raw data untouched
    - perform only explicit, documented transformations
    """

    def __init__(self):
        self.emissions = []
        self.initial_conditions = []
        self.firm_params = []

    # Annual emissions (Emission Data.csv)
    def load_emissions_csv(self, filepath: str):
        self.emissions = []

        with open(filepath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                raise ValueError("Emission Data.csv has no header row.")

            field_map = {
                name.strip().lower(): name
                for name in reader.fieldnames
            }

            if "emissions" not in field_map:
                raise ValueError(
                    f"No 'emissions' column found. Columns: {reader.fieldnames}"
                )

            key = field_map["emissions"]

            for row in reader:
                try:
                    e = float(row[key])
                    if e > 0.0:
                        self.emissions.append(e)
                except (ValueError, TypeError):
                    continue

        if not self.emissions:
            raise ValueError("No valid emissions data loaded.")

    def derive_initial_conditions(self):
        self.initial_conditions = [
            {"annual_emissions": e}
            for e in self.emissions
        ]
        return self.initial_conditions

    # Firm parameters (EU ETS 2 real data.csv)
    def load_firm_parameters(self, filepath: str):
        # Read raw file without header
        df_raw = pd.read_csv(
            filepath,
            sep=";",
            encoding="latin1",
            header=None
        )

        # Detect header row
        header_row = None
        for i in range(min(20, len(df_raw))):
            row = df_raw.iloc[i].astype(str).str.lower()
            if row.str.contains("carbon").any():
                header_row = i
                break

        if header_row is None:
            raise ValueError("Could not find header row in EU ETS 2 real data.csv")

        # Re-read with header
        df = pd.read_csv(
            filepath,
            sep=";",
            encoding="latin1",
            header=header_row
        )

        cols = {c.strip().lower(): c for c in df.columns}

        def find_col(prefixes):
            for p in prefixes:
                for c in cols:
                    if c.startswith(p):
                        return cols[c]
            raise ValueError(f"Missing column starting with {prefixes}")

        def to_float(x):
            if x is None:
                return None

            s = str(x).strip()

            # Excel error literals or empty
            if s in {"", "#DIV/0!", "#VALUE!", "#N/A", "nan"}:
                return None

            # European formatting: thousands '.' and decimal ','
            s = s.replace(".", "").replace(",", ".")

            try:
                return float(s)
            except ValueError:
                return None

        tco2_col = find_col(["tco2", "emission"])
        output_col = find_col(["daily output", "output"])
        phi_col = find_col(["carbon intensity", "carbon"])
        price_col = find_col(["price"])
        cost_col = find_col(["marginal cost", "cost"])

        self.firm_params = []

        for _, row in df.iterrows():
            allowances = to_float(row[tco2_col])
            production = to_float(row[output_col])
            phi_raw = to_float(row[phi_col])
            price = to_float(row[price_col])
            cost = to_float(row[cost_col])

            # Skip firms with invalid fundamentals
            if (
                    None in (allowances, production, phi_raw, price, cost)
                    or phi_raw <= 1
            ):
                continue

            self.firm_params.append(
                {
                    "initial_allowances": allowances,
                    "initial_production": production,
                    "phi_j": phi_raw / 1000.0,  # kg → tons
                    "price": price,
                    "cost": cost,
                }
            )

        if not self.firm_params:
            raise ValueError("No valid firm parameters loaded.")

        return self.firm_params
