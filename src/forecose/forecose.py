"""Dexcom prediction class."""

import numpy as np

import pandas as pd

import timesfm

from pydexcom import Dexcom

class DexcomForecast:
    """Class for a time-series forecasting model construction of CGM data."""

    def __init__(
            self,
            cgm_history: np.ndarray,
            last_timestamp: pd.Timestamp,
            sampling_interval: pd.Timedelta,
            context_len: int = 288,
            horizon: int = 12
    ) -> None:
        """
        Compiles the TimesFM model.
        """
        self.context_len = context_len
        self.horizon = horizon

        self.cgm_history = cgm_history[-self.context_len:]
        self.last_timestamp = last_timestamp
        self.sampling_interval = sampling_interval

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

    @classmethod
    def from_dexcom(
        cls,
        dexcom: Dexcom,
        context_len: int = 288,
        horizon: int = 12
    ):
        """Pull data from an active pydexcom session."""
        if not isinstance(dexcom, Dexcom):
            raise TypeError("Expected an object of type pydexcom.Dexcom.")
        
        # extract data
        readings = dexcom.get_glucose_readings(
            minutes=1440, max_count=context_len
        )
        if not readings:
            raise RuntimeError("No readings returned from Dexcom Share API.")
        
        # process data structures
        df = pd.DataFrame(
            [{"Time": r.datetime, "Glucose": r.mmol_l} for r in reversed(readings)]
        )
        df["Time"] = pd.to_datetime(df["Time"], utc=True).dt.tz_convert("Europe/London")
        df = df.sort_values("Time").reset_index(drop=True)

        cgm_history = df["Glucose"].to_numpy(dtype=float)
        last_timestamp = df["Time"].iloc[-1]
        sampling_interval = pd.Timedelta(df["Time"].diff().median())

        # return instance
        return cls(
            cgm_history=cgm_history,
            last_timestamp=last_timestamp,
            sampling_interval=sampling_interval,
            context_len=context_len,
            horizon=horizon
        )
    
    def forecast(self) -> pd.DataFrame:
        """Returns point and quantile forecasts of time series data."""
        if len(self.cgm_history) == 0:
            raise ValueError("No historical data provided for forecasting.")
        
        # run inference
        point_forecast, quantile_forecast = self.model.forecast(
            horizon=self.horizon,
            inputs=[self.cgm_history],
        )

        point_vals = point_forecast[0]
        quant_vals = quantile_forecast[0]

        future_timestamps = pd.date_range(
            start=self.last_timestamp + self.sampling_interval,
            periods=self.horizon,
            freq=self.sampling_interval,
        )

        # compile
        forecast_df = pd.DataFrame({
            "timestamp": future_timestamps,
            "predicted_glucose": np.clip(point_vals, *(2.2, 22.2)),
            "q10": np.clip(quant_vals[:, 0], *(2.2, 22.2)),
            "q25": np.clip(quant_vals[:, 1], *(2.2, 22.2)),
            "q50": np.clip(quant_vals[:, 4], *(2.2, 22.2)),
            "q75": np.clip(quant_vals[:, 7], *(2.2, 22.2)),
            "q90": np.clip(quant_vals[:, 8], *(2.2, 22.2)),
        })

        return forecast_df