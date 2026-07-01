from __future__ import annotations

import pandas as pd

import numpy as np

from .const import FORECAST_DESCRIPTIONS, MMOL_L_CONVERSION_FACTOR, CLIP_HIGH, CLIP_LOW

from .kinetics import _TYPES, calculate_event_curve

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
    
    def add_event(self, type: _TYPES, units: float, minutes_ago: int = 0, tau: float | None = None, sensitivity: float | None = None):
        """Applies an overly to account for insulin (downward) or carb (upward) events."""
        forecast = self.copy()

        # generate time vector with offset
        intervals = len(forecast)
        t_future = np.arange(5, (intervals * 5) + 5, 5) + minutes_ago

        # calculate impact array
        impact_curve = calculate_event_curve(t_array=t_future, type=type, units=units, tau=tau, sensitivity=sensitivity)

        for col in FORECAST_DESCRIPTIONS:
            if col in forecast.columns:
                if type == "insulin":
                    vals_curved = forecast[col] - impact_curve
                else:
                    vals_curved = forecast[col] + impact_curve

                forecast[col] = np.round(np.clip(vals_curved, CLIP_LOW, CLIP_HIGH), 0)

        return forecast