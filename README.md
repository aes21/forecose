A time-series forecasting extension for [pydexcom](https://github.com/gagebenne/pydexcom) using Google's [TimesFM](https://github.com/google-research/timesfm). Used to predict immediate, short term blood glucose readings.

## Quick Start
1. Ensure that you have installed the pydexcom package and [enabled the Share service](https://provider.dexcom.com/education-research/cgm-education-use/videos/setting-dexcom-share-and-follow) within your [Dexcom G7 / G6 / G5 / G4](https://www.dexcom.com/apps).

`pip install pydexcom`

2. Initialise `pydexcom` with your Dexcom credentials (below shows the simplist route, refere to pydexcom for further instruction).

```python
>>> from pydexcom import Dexcom
>>> dexcom = Dexcom(username="username", password="password")
```

3. Generate a prediction.

```python
>>> from forecose import DexcomForecast
>>> forecaster = DexcomForecast.from_dexcom( 
        dexcom=dexcom,      # pull recent readings from your active 'Dexcom' session
        context_len=288,    # uses prior day's readings as context
        horizon=12          # predicts the next hour
    )
>>> predictions = forecaster.forecast()
>>> print(predictions.head())
```