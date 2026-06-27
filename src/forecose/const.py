from pydexcom.const import MAX_MAX_COUNT, MAX_MINUTES, MMOL_L_CONVERSION_FACTOR

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