# forecose

[![PyPI](https://img.shields.io/pypi/v/forecose?style=flat-square)](https://pypi.org/project/forecose/)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest.svg?style=flat-square)](https://pypi.org/project/forecose/)
[![Tests](https://img.shields.io/github/actions/workflow/status/aes21/forecose/test.yaml?style=flat-square&label=tests)](https://github.com/aes21/forecose/actions/workflows/test.yaml)

A time-series forecasting extension for [pydexcom](https://github.com/gagebenne/pydexcom) using Google's [TimesFM](https://github.com/google-research/timesfm). Readings from the previous 24 hours are captured from the Dexcom Share API service and fed into the model to create a forecast of blood glucose values for the next hour.

> All modelling and forecasting is performed locally on your device. The only external connections made are with:
> - Dexcom Share API: fetching CGM readings following the `pydexcom` approach.
> - HuggingFace: one-time download of the forecasting model weights on the first run.

## Quick Start
1. Ensure that you have also installed the `pydexcom` package and [enabled the Share service](https://provider.dexcom.com/education-research/cgm-education-use/videos/setting-dexcom-share-and-follow) within your [Dexcom G7 / G6 / G5 / G4](https://www.dexcom.com/apps) mobile app.

`pip install pydexcom forecose`

2. Initialise `pydexcom` with your Dexcom credentials (below shows the simplist route, refer to [pydexcom](https://github.com/gagebenne/pydexcom) for further instruction).

```python
>>> from pydexcom import Dexcom
>>> dexcom = Dexcom(username="username", password="password")
```

3. Generate a prediction. By default, the `DexcomForecast` class predicts the upcoming hour (the next 12 readings) to prevent overextending the forecast. Set custom prediction lengths by adjusting the `horizon` argument.

```python
>>> from forecose import DexcomForecast
>>> predictions = DexcomForecast(horizon=12).get_forecast(dexcom)
>>> print(predictions)
                          timestamp  predicted_glucose    q10    q20    q30    q40    q50    q60    q70    q80    q90
0  2026-10-01 09:07:45.945000+01:00              161.0  158.0  160.0  160.0  160.0  161.0  162.0  163.0  166.0  171.0
1  2026-10-01 09:12:45.894000+01:00              163.0  154.0  158.0  159.0  161.0  163.0  165.0  168.0  171.0  178.0
2  2026-10-01 09:17:45.843000+01:00              164.0  151.0  156.0  159.0  161.0  164.0  167.0  170.0  175.0  184.0
3  2026-10-01 09:22:45.792000+01:00              165.0  148.0  155.0  159.0  162.0  165.0  169.0  173.0  179.0  190.0
4  2026-10-01 09:27:45.741000+01:00              167.0  146.0  153.0  158.0  162.0  167.0  171.0  176.0  183.0  194.0
5  2026-10-01 09:32:45.690000+01:00              167.0  143.0  152.0  158.0  162.0  167.0  172.0  177.0  185.0  199.0
6  2026-10-01 09:37:45.639000+01:00              167.0  140.0  149.0  155.0  161.0  167.0  172.0  179.0  187.0  201.0
7  2026-10-01 09:42:45.588000+01:00              167.0  138.0  148.0  155.0  161.0  167.0  172.0  179.0  189.0  204.0
8  2026-10-01 09:47:45.537000+01:00              167.0  136.0  147.0  154.0  160.0  167.0  173.0  181.0  190.0  207.0
9  2026-10-01 09:52:45.486000+01:00              167.0  133.0  146.0  152.0  160.0  167.0  174.0  182.0  191.0  209.0
10 2026-10-01 09:57:45.435000+01:00              167.0  132.0  145.0  152.0  160.0  167.0  175.0  184.0  193.0  212.0
11 2026-10-01 10:02:45.384000+01:00              166.0  129.0  143.0  150.0  158.0  166.0  175.0  184.0  194.0  214.0

>>> print(predictions.mmol_l)
                          timestamp  predicted_glucose  q10  q20  q30  q40  q50  q60   q70   q80   q90
0  2026-10-01 09:07:45.945000+01:00                8.9  8.8  8.9  8.9  8.9  8.9  9.0   9.0   9.2   9.5
1  2026-10-01 09:12:45.894000+01:00                9.0  8.5  8.8  8.8  8.9  9.0  9.2   9.3   9.5   9.9
2  2026-10-01 09:17:45.843000+01:00                9.1  8.4  8.7  8.8  8.9  9.1  9.3   9.4   9.7  10.2
3  2026-10-01 09:22:45.792000+01:00                9.2  8.2  8.6  8.8  9.0  9.2  9.4   9.6   9.9  10.5
4  2026-10-01 09:27:45.741000+01:00                9.3  8.1  8.5  8.8  9.0  9.3  9.5   9.8  10.2  10.8
5  2026-10-01 09:32:45.690000+01:00                9.3  7.9  8.4  8.8  9.0  9.3  9.5   9.8  10.3  11.0
6  2026-10-01 09:37:45.639000+01:00                9.3  7.8  8.3  8.6  8.9  9.3  9.5   9.9  10.4  11.2
7  2026-10-01 09:42:45.588000+01:00                9.3  7.7  8.2  8.6  8.9  9.3  9.5   9.9  10.5  11.3
8  2026-10-01 09:47:45.537000+01:00                9.3  7.5  8.2  8.5  8.9  9.3  9.6  10.0  10.5  11.5
9  2026-10-01 09:52:45.486000+01:00                9.3  7.4  8.1  8.4  8.9  9.3  9.7  10.1  10.6  11.6
10 2026-10-01 09:57:45.435000+01:00                9.3  7.3  8.0  8.4  8.9  9.3  9.7  10.2  10.7  11.8
11 2026-10-01 10:02:45.384000+01:00                9.2  7.2  7.9  8.3  8.8  9.2  9.7  10.2  10.8  11.9
```

### What do these predictions mean?
- `predicted-glucose`: The average trajectory of your blood sugar forecast (smoothed, centred baseline of the confidence bands).
- `q10` to `q90`: The range of confidence bands provide a realistic upper and lower estimate boundaries, showing the full probability distribution of predicted glucose values.

## Event Modelling
To account for key events (e.g., insulin administration or carbohydrate (carbs) intake) that act on blood glucose values without distorting the underlying TimesFM probability distribution, you can apply a deterministic overlay to your baseline forecast.

Drawing on mathematical frameworks utilised in closed-loop Artifical Pancreas systems and the Hovorka/Bergman meal submodels, event impacts are computed as a second-order linear delay process. Here, event unit rates (e.g., the absorption of insulin or carbs) are translated into a physiological curve that begins slowly, reaches a peak, and then gradually decays over time.

By default, `forecose` updates the forecast predictions using standard clinical baselines (a 55-minute peak for insulin, and a 40-minute peak for carbs):

```python
>>> carb_predictions = predictions.add_event(type="carbs", units=30, minutes_ago=0)
>>> print(carb_predictions.mmol_l)
                          timestamp  predicted_glucose   q10   q20   q30   q40   q50   q60   q70   q80   q90
0  2026-10-01 09:07:45.945000+01:00                9.0   8.8   8.9   8.9   8.9   9.0   9.0   9.1   9.3   9.5
1  2026-10-01 09:12:45.894000+01:00                9.2   8.7   8.9   9.0   9.1   9.2   9.3   9.5   9.7  10.0
2  2026-10-01 09:17:45.843000+01:00                9.5   8.8   9.0   9.2   9.3   9.5   9.7   9.8  10.1  10.6
3  2026-10-01 09:22:45.792000+01:00                9.8   8.8   9.2   9.4   9.6   9.8  10.0  10.2  10.5  11.2
4  2026-10-01 09:27:45.741000+01:00               10.2   9.0   9.4   9.7   9.9  10.2  10.4  10.7  11.0  11.7
5  2026-10-01 09:32:45.690000+01:00               10.4   9.1   9.6   9.9  10.2  10.4  10.7  11.0  11.4  12.2
6  2026-10-01 09:37:45.639000+01:00               10.7   9.2   9.7  10.0  10.4  10.7  11.0  11.4  11.8  12.6
7  2026-10-01 09:42:45.588000+01:00               11.0   9.4  10.0  10.4  10.7  11.0  11.3  11.7  12.3  13.1
8  2026-10-01 09:47:45.537000+01:00               11.3   9.6  10.2  10.6  10.9  11.3  11.7  12.1  12.6  13.5
9  2026-10-01 09:52:45.486000+01:00               11.7   9.8  10.5  10.8  11.3  11.7  12.0  12.5  13.0  14.0
10 2026-10-01 09:57:45.435000+01:00               11.9  10.0  10.7  11.1  11.5  11.9  12.4  12.9  13.4  14.4
11 2026-10-01 10:02:45.384000+01:00               12.2  10.1  10.9  11.3  11.7  12.2  12.7  13.2  13.7  14.8

>>> insulin_predictions = predictions.add_event(type="insulin", units=5, minutes_ago=0)
>>> print(insulin_predictions.mmol_l)
                          timestamp  predicted_glucose  q10  q20  q30  q40  q50  q60  q70  q80   q90
0  2026-10-01 09:07:45.945000+01:00                8.9  8.7  8.8  8.8  8.8  8.9  8.9  9.0  9.2   9.4
1  2026-10-01 09:12:45.894000+01:00                8.9  8.4  8.6  8.7  8.8  8.9  9.0  9.2  9.3   9.7
2  2026-10-01 09:17:45.843000+01:00                8.8  8.0  8.3  8.5  8.6  8.8  8.9  9.1  9.4   9.9
3  2026-10-01 09:22:45.792000+01:00                8.6  7.7  8.0  8.3  8.4  8.6  8.8  9.0  9.4  10.0
4  2026-10-01 09:27:45.741000+01:00                8.4  7.3  7.7  7.9  8.2  8.4  8.7  8.9  9.3   9.9
5  2026-10-01 09:32:45.690000+01:00                8.1  6.8  7.3  7.6  7.8  8.1  8.4  8.7  9.1   9.9
6  2026-10-01 09:37:45.639000+01:00                7.8  6.3  6.8  7.1  7.4  7.8  8.0  8.4  8.9   9.7
7  2026-10-01 09:42:45.588000+01:00                7.4  5.8  6.4  6.8  7.1  7.4  7.7  8.1  8.7   9.5
8  2026-10-01 09:47:45.537000+01:00                7.0  5.3  5.9  6.3  6.7  7.0  7.4  7.8  8.3   9.3
9  2026-10-01 09:52:45.486000+01:00                6.7  4.8  5.6  5.9  6.3  6.7  7.1  7.5  8.0   9.0
10 2026-10-01 09:57:45.435000+01:00                6.3  4.4  5.1  5.5  5.9  6.3  6.8  7.3  7.8   8.8
11 2026-10-01 10:02:45.384000+01:00                5.9  3.8  4.6  5.0  5.4  5.9  6.4  6.9  7.4   8.5
```

Sensitivity to insulin (ISF) and carbohydrates (CSF) is set at 40 mg/dL per 1U and 4 mg/dL per gram, respectively. These values are placeholders meant to represent reasonable values and should be adjusted through the `add_event` method using the `tau` and `sensitivity` parameters. In future, I hope to develop a method for calculating estimate values from historic data.

```python
>>> insensitive_insulin_predictions = predictions.add_event(type="insulin", units=5, minutes_ago=0, sensitivity=20.0)
>>> print(insensitive_insulin_predictions.mmol_l)
                          timestamp  predicted_glucose  q10  q20  q30  q40  q50  q60  q70  q80   q90
0  2026-10-01 09:07:45.945000+01:00                8.9  8.8  8.9  8.9  8.9  8.9  9.0  9.0  9.2   9.5
1  2026-10-01 09:12:45.894000+01:00                9.0  8.5  8.7  8.8  8.9  9.0  9.1  9.3  9.4   9.8
2  2026-10-01 09:17:45.843000+01:00                8.9  8.2  8.5  8.7  8.8  8.9  9.1  9.3  9.5  10.0
3  2026-10-01 09:22:45.792000+01:00                8.9  7.9  8.3  8.5  8.7  8.9  9.1  9.3  9.7  10.3
4  2026-10-01 09:27:45.741000+01:00                8.8  7.7  8.0  8.3  8.5  8.8  9.0  9.3  9.7  10.3
5  2026-10-01 09:32:45.690000+01:00                8.7  7.4  7.9  8.2  8.4  8.7  9.0  9.3  9.7  10.5
6  2026-10-01 09:37:45.639000+01:00                8.5  7.0  7.5  7.9  8.2  8.5  8.8  9.2  9.7  10.4
7  2026-10-01 09:42:45.588000+01:00                8.3  6.7  7.3  7.7  8.0  8.3  8.6  9.0  9.5  10.4
8  2026-10-01 09:47:45.537000+01:00                8.2  6.4  7.0  7.4  7.8  8.2  8.5  8.9  9.4  10.4
9  2026-10-01 09:52:45.486000+01:00                8.0  6.1  6.8  7.2  7.6  8.0  8.4  8.8  9.3  10.3
10 2026-10-01 09:57:45.435000+01:00                7.8  5.9  6.6  7.0  7.4  7.8  8.3  8.8  9.3  10.3
11 2026-10-01 10:02:45.384000+01:00                7.5  5.5  6.3  6.7  7.1  7.5  8.0  8.5  9.1  10.2
```

## Custom Data Forecasting

Forecast historical CGM data without the need to connect to the Dexcom Share API service. The input data must contain only `Time` and `Glucose` columns to successfully generate a forecast prediction.

```python
>>> import pandas as pd
>>> custom_data = pd.read_csv("historical_cgm_data.csv")
>>> print(custom_data)
                     Time  Glucose
0     2026-08-27T00:01:57      6.7
1     2026-08-27T00:06:57      6.4
2     2026-08-27T00:11:57      6.2
3     2026-08-27T00:16:57      5.9
4     2026-08-27T00:21:58      5.8
...                   ...      ...
1714  2026-09-01T23:37:11      8.5
1715  2026-09-01T23:42:11      8.3
1716  2026-09-01T23:47:11      7.8
1717  2026-09-01T23:52:11      7.5
1718  2026-09-01T23:57:11      7.1
```

Pass the input data when initialising the `DexcomForecast` class via `cgm_history` to bypass the requirement to connect to the Dexcom Share API service.

```python
>>> custom_predictions = DexcomForecast(cgm_history=custom_data).get_forecast()
```