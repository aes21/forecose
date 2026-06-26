from __future__ import annotations

import pandas as pd

from .const import FORECAST_DESCRIPTIONS, MMOL_L_CONVERSION_FACTOR

class GlucoseForecast(pd.DataFrame):
    """Subclass for parsing and manipulation of forecast glucose data frame."""

    @property
    def _constructor(self):
        return GlucoseForecast
    
    @property
    def mmol_l(self) -> GlucoseForecast:
        """Forecast blood glucose values in mmol/L."""
        forecast = self.copy()

        for col in FORECAST_DESCRIPTIONS:
            if col in forecast.columns:
                forecast[col] = (forecast[col] * MMOL_L_CONVERSION_FACTOR).round(1)

        return forecast