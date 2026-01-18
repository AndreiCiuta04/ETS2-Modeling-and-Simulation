import csv


class DataProcessor:
    """
    Responsible for importing empirical ETS data into the simulation.

    The DataProcessor:
    - reads raw CSV input files,
    - validates and cleans emissions data,
    - derives numerical initial conditions.

    It does NOT:
    - create agents,
    - assign risk behavior,
    - interact with Mesa.

    This keeps data handling fully separated from simulation logic.
    """

    def __init__(self):
        """
        Initializes the data processor.
        """
        self.emissions = []
        self.n_agents = 0

    def load_emissions_csv(self, filepath: str) -> None:
        """
        Loads annual firm emissions from a CSV file.

        Expected:
        - a header row containing a column named 'emissions'
          (case- and whitespace-insensitive)

        Each row corresponds to one firm.
        Firms with zero or negative emissions are kept for now
        and handled during validation.
        """
        self.emissions = []

        # utf-8-sig removes Excel BOM if present
        with open(filepath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                raise ValueError("CSV file has no header row.")

            # Normalize headers: lowercase and strip whitespace
            field_map = {
                name.strip().lower(): name
                for name in reader.fieldnames
            }

            if "emissions" not in field_map:
                raise ValueError(
                    f"No 'emissions' column found. Columns are: {reader.fieldnames}"
                )

            emissions_key = field_map["emissions"]

            for row in reader:
                try:
                    value = float(row[emissions_key])
                    self.emissions.append(value)
                except (ValueError, TypeError):
                    # Skip malformed rows explicitly
                    continue

        self.n_agents = len(self.emissions)

    def validate(self) -> None:
        """
        Validates and cleans loaded emissions data.

        Validation rules:
        - At least one firm must be present
        - Firms with zero or negative emissions are excluded,
          as they do not meaningfully participate in allowance trading
        """
        if not self.emissions:
            raise ValueError("No emissions data loaded.")

        # Filter out non-positive emitters
        filtered = [e for e in self.emissions if e > 0.0]

        if not filtered:
            raise ValueError("All firms have zero or negative emissions.")

        self.emissions = filtered
        self.n_agents = len(self.emissions)

    def derive_initial_conditions(self, allowance_factor: float = 0.9):
        """
        Derives numerical initial conditions for the model.

        :param allowance_factor: fraction of annual emissions
                                 allocated as initial allowances
        :return: list of dictionaries with firm fundamentals
        """
        return [
            {
                "annual_emissions": e,
                "initial_allowances": allowance_factor * e,
            }
            for e in self.emissions
        ]
