import csv
import pandas as pd


class DataProcessor:
    """
    Loads empirical inputs for the ETS simulation.

    NOTE (research / future work):
    The emissions pipeline (Emission Data.csv) is currently not used by the core simulation logic.
    It is kept to preserve the research workflow and to enable later extensions.
    """

    def __init__(self):
        """Initializes containers for ingested datasets."""
        self.emissions = []
        self.initial_conditions = []
        self.firm_params = []

    # Annual emissions (Emission Data.csv)
    def load_emissions_csv(self, filepath: str):
        """
        Loads annual emissions from a CSV with an 'emissions' column (case-insensitive).

        @param filepath: Path to 'Emission Data.csv'
        @return: None (populates self.emissions)
        @raises ValueError: If the CSV has no header, no emissions column, or no valid values
        """
        self.emissions = []

        # utf-8-sig handles BOMs that sometimes appear in exported CSV files.
        with open(filepath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                raise ValueError("Emission Data.csv has no header row.")

            # Map normalized header names -> original header names.
            field_map = {name.strip().lower(): name for name in reader.fieldnames}

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
        """
        Converts loaded emissions into a simple per-agent initialization list.

        NOTE:
        These initial conditions are currently only used for dataset alignment and are not yet
        consumed by agent behavior in the core model.

        @return: List[dict] of the form {'annual_emissions': float}
        """
        self.initial_conditions = [{"annual_emissions": e} for e in self.emissions]
        return self.initial_conditions

    # Firm parameters (EU ETS 2 real data.csv)
    def load_firm_parameters(self, filepath: str):
        """
        Loads firm parameters from 'EU ETS 2 real data.csv'.

        The file may contain metadata rows before the actual header, so we detect the header row
        by scanning for a row containing 'carbon'. Numeric values may use European formatting.

        @param filepath: Path to 'EU ETS 2 real data.csv'
        @return: List[dict] firm parameters
        @raises ValueError: If the header row/required columns cannot be found or no valid rows load
        """
        # Read without header to detect where the header starts.
        df_raw = pd.read_csv(filepath, sep=";", encoding="latin1", header=None)

        header_row = None
        for i in range(min(20, len(df_raw))):
            row = df_raw.iloc[i].astype(str).str.lower()
            if row.str.contains("carbon").any():
                header_row = i
                break

        if header_row is None:
            raise ValueError("Could not find header row in EU ETS 2 real data.csv")

        df = pd.read_csv(filepath, sep=";", encoding="latin1", header=header_row)
        cols = {c.strip().lower(): c for c in df.columns}

        def find_col(prefixes):
            """Returns the first column name whose normalized name starts with one of prefixes."""
            for p in prefixes:
                for c in cols:
                    if c.startswith(p):
                        return cols[c]
            raise ValueError(f"Missing column starting with {prefixes}")

        def to_float(x):
            """Parses numbers with EU formatting and ignores common Excel error literals."""
            if x is None:
                return None
            s = str(x).strip()
            if s in {"", "#DIV/0!", "#VALUE!", "#N/A", "nan"}:
                return None
            s = s.replace(".", "").replace(",", ".")  # thousands '.' and decimal ','
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

            # Skip rows that do not contain the required economic values.
            if None in (allowances, production, price, cost):
                continue

            # Ensure carbon intensity is non-trivial; fallback prevents divide-by-zero-like behavior.
            if phi_raw is None or phi_raw < 1:
                phi_raw = 1.0

            self.firm_params.append(
                {
                    "initial_allowances": allowances,
                    "initial_production": production,
                    "phi_j": phi_raw / 1000.0,  # convert kg → tons
                    "price": price,
                    "cost": cost,
                }
            )

        if not self.firm_params:
            raise ValueError("No valid firm parameters loaded.")

        return self.firm_params
