from typing import Literal, Optional

import numpy as np

_TYPES = Literal["insulin", "carbs"]

def _erlang_cdf(t_array: np.ndarray, magnitude: float, sensitivity: float, tau: float) -> np.ndarray:
    """
    Calculate the cumlative event impact using second-order delay (Erlang CDF).
    """
    impact = magnitude * sensitivity * (1 - (1 + t_array / tau) * np.exp(-t_array / tau))

    return np.clip(impact, a_min=0, a_max=None)

def calculate_event_curve(t_array: np.ndarray, type: _TYPES, units: float, tau: Optional[float] = None, sensitivity: Optional[float] = None) -> np.ndarray:
    """
    Calculates event impact via Erlang CDF.
    """

    if type == "insulin":
        # default 55 minute peak
        t_peak = tau if tau is not None else 55.0

        # sets a 40 mg/dL drop per unit
        factor = sensitivity if sensitivity is not None else 40.0
    else:
        # default 40 minute peak
        t_peak = tau if tau is not None else 40.0

        # sets a 4 mg/dL rise per carb unit (g)
        factor = sensitivity if sensitivity is not None else 4.0

    return _erlang_cdf(t_array, magnitude=units, sensitivity=factor, tau=t_peak)