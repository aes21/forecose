import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from forecose import DexcomForecast

@pytest.fixture
def sample_cgm_data():
    """Sample CGM data for prior 24 hours."""
    return np.random.uniform(4.0, 10.0, size=288)

@pytest.fixture
def mock_timesfm_model():
    """
    Mocks the TimesFM model to return dummy arrays.
    """
    with patch("forecose.forecose.timesfm.TimesFM_2p5_200M_torch.from_pretrained") as mock_model:
        instance = mock_model.return_value
        mock_point = np.array([[5.5] * 12])
        mock_quantiles = np.zeros((1, 12, 10))

        # quantiles
        mock_quantiles[0, :, 0] = 4.0
        mock_quantiles[0, :, 1] = 4.5
        mock_quantiles[0, :, 4] = 5.0
        mock_quantiles[0, :, 7] = 6.5
        mock_quantiles[0, :, 8] = 7.0

        instance.forecast.return_value = (mock_point, mock_quantiles)
        yield instance

def test_forecaster_structure(sample_cgm_data, mock_timesfm_model):
    """Verifies the forecast method returns the correct pd.DataFrame structure."""

    last_time = pd.Timestamp.now(tz="UTC")
    interval = pd.Timedelta(minutes=5)

    forecaster = DexcomForecast(
        cgm_history=sample_cgm_data,
        last_timestamp=last_time,
        sampling_interval=interval,
        context_len=288,
        horizon=12
    )

    df = forecaster.forecast()

    assert len(df) == 12

    assert list(df.columns) == ["timestamp", "predicted_glucose", "q10", "q25", "q50", "q75", "q90"]

    assert df["timestamp"].iloc[0] == last_time + interval
    assert df["timestamp"].iloc[1] == last_time + (2 * interval)

def test_forecaster_empty_history():
    """Verifies the model blocks execution if no data is passed from the Dexcom Share API."""
    forecaster = DexcomForecast(
        cgm_history=np.array([]),
        last_timestamp=pd.Timestamp.now(tz="UTC"),
        sampling_interval=pd.Timedelta(minutes=5)
    )

    with pytest.raises(ValueError, match="No historical data provided"):
        forecaster.forecast()
