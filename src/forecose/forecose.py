"""Dexcom prediction class."""

import numpy as np

import pandas as pd

import timesfm

from pydexcom import Dexcom

from .const import CLIP_HIGH, CLIP_LOW, FORECAST_QUANTILES, HORIZON, MAX_MAX_COUNT, MAX_MINUTES

from .glucose_forecast import GlucoseForecast

class DexcomForecast:
    """Class for a time-series forecasting model construction of CGM data."""

    def __init__(
            self,
            context_len: int = MAX_MAX_COUNT,
            horizon: int = HORIZON
    ) -> None:
        """
        Compiles the TimesFM model.
        """
        self.context_len = context_len
        self.horizon = horizon

        self._cgm_history = None
        self._last_timestamp = None
        self._sampling_interval = None

        # initalise and compile the TimesFM model
        self.model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
            "google/timesfm-2.5-200m-pytorch"
        )
        self.model.compile(
            timesfm.ForecastConfig(
                max_context=self.context_len,
                max_horizon=self.horizon,
                normalize_inputs=True,
                use_continuous_quantile_head=True,
                infer_is_positive=True,
                fix_quantile_crossing=True,
            )
        )

    def _fetch_readings(self, dexcom: Dexcom) -> None:
        """Fetch the most recent readings from the active pydexcom session."""
        if not isinstance(dexcom, Dexcom):
            raise TypeError("Expected an object of type pydexcom.Dexcom.")
        
        # extract data
        readings = dexcom.get_glucose_readings(
            minutes=MAX_MINUTES, max_count=self.context_len
        )
        if not readings:
            raise RuntimeError("No readings returned from Dexcom Share API.")
        
        # process data structures
        df = pd.DataFrame(
            [{"Time": r.datetime, "Glucose": r.value} for r in reversed(readings)]
        )
        df["Time"] = pd.to_datetime(df["Time"], utc=True).dt.tz_convert("Europe/London")
        df = df.sort_values("Time").reset_index(drop=True)

        self._cgm_history = df["Glucose"].to_numpy(dtype=float)[-self.context_len:]
        self._last_timestamp = df["Time"].iloc[-1]
        self._sampling_interval = pd.Timedelta(df["Time"].diff().median())

    def get_forecast(self, dexcom: Dexcom) -> GlucoseForecast:
        """Returns point and quantile forecasts of time series data."""
        self._fetch_readings(dexcom)

        if self._cgm_history is None or self._last_timestamp is None:
            raise RuntimeError("CGM history unavailable; call _fetch_readings first.")

        # run inference
        point_forecast, quantile_forecast = self.model.forecast(
            horizon=self.horizon,
            inputs=[self._cgm_history],
        )

        point_vals = point_forecast[0]
        quant_vals = quantile_forecast[0]

        future_timestamps = pd.date_range(
            start=self._last_timestamp + self._sampling_interval,
            periods=self.horizon,
            freq=self._sampling_interval,
        )

        glucose_forecast = {"timestamp": future_timestamps,
                            "predicted_glucose": np.round(np.clip(point_vals, CLIP_LOW, CLIP_HIGH), 0)}
        
        for col, idx in FORECAST_QUANTILES.items():
            glucose_forecast[col] = np.round(np.clip(quant_vals[:, idx], CLIP_LOW, CLIP_HIGH), 0)

        return GlucoseForecast(glucose_forecast)