A time-series forecasting extension for [pydexcom](https://github.com/gagebenne/pydexcom) using Google's [TimesFM](https://github.com/google-research/timesfm). Used to predict immediate, short term blood glucose readings.

> All modelling and forecasting is performed locally on your device. The only external connections made are with:
> - Dexcom Share API: fetching CGM readings following the `pydexcom` approach.
> - HuggingFace: one-time download of the forecasting model weights on the first run.

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
                         timestamp  predicted_glucose       q10       q25       q50       q75       q90
0 2026-06-25 11:01:19.199000+01:00           8.243370  8.244899  8.125346  8.214749  8.266071  8.309934
1 2026-06-25 11:06:19.199000+01:00           8.050682  8.073329  7.738788  8.018662  8.208736  8.303193
2 2026-06-25 11:11:19.199000+01:00           7.897943  7.879324  7.332723  7.783697  8.082028  8.256586
3 2026-06-25 11:16:19.199000+01:00           7.767045  7.738261  6.965607  7.621467  8.026337  8.236394
4 2026-06-25 11:21:19.199000+01:00           7.615633  7.667328  6.668064  7.442780  7.972524  8.216294
```