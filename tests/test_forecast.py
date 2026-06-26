import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

from pydexcom import Dexcom
from forecose import DexcomForecast
from forecose.glucose_forecast import GlucoseForecast
from forecose.const import CLIP_HIGH, CLIP_LOW

@pytest.fixture
def mock_timesfm_model():
    """
    Mocks the TimesFM model to return dummy arrays.
    """
    with patch("forecose.forecose.timesfm.TimesFM_2p5_200M_torch.from_pretrained") as mock_model:
        instance = mock_model.return_value
        mock_point = np.array([[100] * 12])

        # quantiles
        mock_quantiles = np.zeros((1, 12, 10))
        mock_quantiles[0, :, 0] = 80.0
        mock_quantiles[0, :, 1] = 90.0
        mock_quantiles[0, :, 4] = 100.0
        mock_quantiles[0, :, 7] = 110.0
        mock_quantiles[0, :, 8] = 120.0

        instance.forecast.return_value = (mock_point, mock_quantiles)
        yield instance

@pytest.fixture
def mock_dexcom():
    """Simulates an active pydexcom Dexcom session."""
    dexcom = MagicMock(spec=Dexcom)

    readings = []
    base_time = pd.Timestamp.now(tz="UTC") - pd.Timedelta(hours=24)

    for i in range(288):
        mock_reading = MagicMock()
        mock_reading.datetime = base_time - pd.Timedelta(minutes=5*i)
        mock_reading.value = 105
        readings.append(mock_reading)

    dexcom.get_glucose_readings.return_value = readings[::-1]
    return dexcom

@pytest.fixture
def mock_dexcom_empty():
    """Simulates a failed API called or empty session data."""
    dexcom = MagicMock(spec=Dexcom)
    dexcom.get_glucose_readings.return_value = []

    return dexcom


def test_forecast_structure(mock_dexcom, mock_timesfm_model):
    """Verifies the forecast method returns the correct subclass structure."""
    forecaster = DexcomForecast()
    df = forecaster.get_forecast(mock_dexcom)

    assert isinstance(df, GlucoseForecast)

    assert len(df) == 12

    assert list(df.columns) == ["timestamp", "predicted_glucose", "q10", "q25", "q50", "q75", "q90"]

def test_forecaster_empty_history(mock_dexcom_empty, mock_timesfm_model):
    """Verifies the model blocks execution if no data is passed from the Dexcom Share API."""
    forecaster = DexcomForecast()

    with pytest.raises(RuntimeError, match="No readings returned from Dexcom Share API."):
        forecaster.get_forecast(mock_dexcom_empty)

def test_mmol_l_conversion(mock_dexcom, mock_timesfm_model):
    """Verifies glucose value conversion on the subcluss structure output."""
    forecaster = DexcomForecast()

    df = forecaster.get_forecast(mock_dexcom)
    df_mmol = df.mmol_l

    assert isinstance(df_mmol, GlucoseForecast)

    assert df_mmol["predicted_glucose"].iloc[0] < 22.0

    assert not df["predicted_glucose"].equals(df_mmol["predicted_glucose"])