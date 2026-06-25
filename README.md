A time-series forecasting extension for pydexcom using Google's TimesFM. Used to predictor short term blood glucose readings.

## Quick Start
1. Ensure that you have installed the pydexcom package and enabled the Share service within your Dexcom G7/G7/G5/G4 mobile app.

`pip install pydexcom`

2. Initialise [] with your Dexcom credentials (below shows the simplist route, refere to pydexcom for further instruction).

```python
>>> from pydexcom import Dexcom
>>> dexcom = Dexcom(username="username", password="password")
```

3. Generate a prediction.

```python
>>> from forecose import DexcomForecast
>>> predictor = DexcomForecast.from_dexcom(dexcom) # pull recent readings from your active 'Dexcom' session
>>> predictor.forecast()
output
```