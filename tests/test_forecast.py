import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

from pydexcom import Dexcom
from forecose import DexcomForecast
from forecose.glucose_forecast import GlucoseForecast
from forecose.const import CLIP_HIGH, CLIP_LOW, MMOL_L_CONVERSION_FACTOR

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

    assert df_mmol["predicted_glucose"].iloc[0] < (CLIP_HIGH * MMOL_L_CONVERSION_FACTOR)

    assert not df["predicted_glucose"].equals(df_mmol["predicted_glucose"])

def test_kinetics(mock_dexcom, mock_timesfm_model):
    """Verifies deterministic events shift the forecast in the correct direction and within physical boundaries."""
    forecaster = DexcomForecast()

    df = forecaster.get_forecast(mock_dexcom)

    carbs_df = df.add_event(type="carbs", units=50)
    assert carbs_df["predicted_glucose"].iloc[-1] > df["predicted_glucose"].iloc[-1]

    insulin_df = df.add_event(type="insulin", units=10)
    assert insulin_df["predicted_glucose"].iloc[-1] < df["predicted_glucose"].iloc[-1]

    # verify clipping
    error_df = df.add_event(type="insulin", units=200)
    assert error_df["predicted_glucose"].min() >= CLIP_LOW

    assert df["predicted_glucose"].equals(forecaster.get_forecast(mock_dexcom)["predicted_glucose"])

@patch("forecose.forecose.timesfm.TimesFM_2p5_200M_torch.from_pretrained")
def test_model_lazy_loading(mock_from_pretrained):
    """Verfies the TimesFM model is only loaded on first access, not instatiation of the `DexcomForecast` object."""
    forecaster = DexcomForecast()

    # check that model was not called
    mock_from_pretrained.assert_not_called()

    # trigger model
    mock_model_instance = mock_from_pretrained.return_value
    model = forecaster.model

    mock_from_pretrained.assert_called_once()
    mock_model_instance.compile.assert_called_once()

    # verify that multiple accessions does not recompile the model
    _ = forecaster.model

    assert mock_from_pretrained.call_count == 1

    assert mock_model_instance.compile.call_count == 1

def test_custom_data(mock_timesfm_model):
    """Verifies that the forecast can run without Dexcom connection when custom data is provided."""
    times = pd.date_range(end=pd.Timestamp.now(tz="UTC"), periods=288, freq="5min")
    custom_df = pd.DataFrame({"Time": times, "Glucose": 105.0})

    forecaster = DexcomForecast(cgm_history=custom_df)

    # do not pass a dexcom object
    df = forecaster.get_forecast()

    assert isinstance(df, GlucoseForecast)

    assert len(df) == 12

    assert np.all(forecaster._cgm_history == 105.0)

def test_custom_data_invalid_columns(mock_timesfm_model):
    """Verifies invalid data columns blocks forecast execution."""
    invalid_df = pd.DataFrame({"timestamp": [1, 2], "value": [100, 105]})

    forecaster = DexcomForecast(cgm_history=invalid_df)

    # raise KeyError
    with pytest.raises(KeyError, match="Input data must only contain"):
        forecaster.get_forecast()
