"""Constants used in `forecose`."""

from pydexcom.const import MAX_MAX_COUNT, MAX_MINUTES, MMOL_L_CONVERSION_FACTOR

class _config:
    """Set insulin/carb sensitivity baselines."""

    def __init__(self):
        self.insulin_tau: float = 55.0
        self.insulin_isf: float = 40.0
        self.carb_tau: float = 40.0
        self.carb_csf: float = 4.0

    def __repr__(self) -> str:
        return (
            f"Insulin peak effect time: {self.insulin_tau} mins\n"
            f"Insulin sensitivity: {self.insulin_isf} mg/dL per unit\n"
            f"Carb peak effect time: {self.carb_tau} mins\n"
            f"Carb sensitivity: {self.carb_csf} mg/dL per gram\n"
        )
    
options = _config()

CLIP_LOW = 40
"""Lowest glucose value reading in mg/dL."""

CLIP_HIGH = 400
"""Highest glucose value reading in mg/dL."""

FORECAST_QUANTILES: dict[str, int] = {
    "q10": 0,
    "q25": 1,
    "q50": 4,
    "q75": 7,
    "q90": 8
}
"""Forecast quantiles."""

FORECAST_DESCRIPTIONS: list[str] = [
    "predicted_glucose",
    *FORECAST_QUANTILES.keys()
]
"""Forecast column names."""

HORIZON: int = 12
"""Prediction count to use when predicting glucose values (1 reading per 5 minutes)."""