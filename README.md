# forecose

[![PyPI](https://img.shields.io/pypi/v/forecose?style=flat-square)](https://pypi.org/project/forecose/)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest.svg?style=flat-square)](https://pypi.org/project/forecose/)
[![Tests](https://img.shields.io/github/actions/workflow/status/aes21/forecose/test.yaml?style=flat-square&label=tests)](https://github.com/aes21/forecose/actions/workflows/test.yaml)

A time-series forecasting extension for [pydexcom](https://github.com/gagebenne/pydexcom) using Google's [TimesFM](https://github.com/google-research/timesfm). Readings from the previous 24 hours are captured from the Dexcom Share API service are fed into the model to forecast blood glucose values over the next hour.

> All modelling and forecasting is performed locally on your device. The only external connections made are with:
> - Dexcom Share API: fetching CGM readings following the `pydexcom` approach.
> - HuggingFace: one-time download of the forecasting model weights on the first run.

## Quick Start
1. Ensure that you also the `pydexcom` package and [enabled the Share service](https://provider.dexcom.com/education-research/cgm-education-use/videos/setting-dexcom-share-and-follow) within your [Dexcom G7 / G6 / G5 / G4](https://www.dexcom.com/apps).

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
                          timestamp  predicted_glucose    q10    q25    q50    q75    q90
0  2026-06-30 11:56:43.332500+01:00              156.0  156.0  147.0  155.0  159.0  162.0
1  2026-06-30 12:01:43.332000+01:00              159.0  159.0  142.0  156.0  165.0  169.0
2  2026-06-30 12:06:43.331500+01:00              160.0  159.0  137.0  156.0  169.0  176.0
3  2026-06-30 12:11:43.331000+01:00              160.0  161.0  132.0  155.0  172.0  180.0
4  2026-06-30 12:16:43.330500+01:00              162.0  161.0  128.0  156.0  176.0  185.0
5  2026-06-30 12:21:43.330000+01:00              162.0  162.0  125.0  155.0  177.0  188.0
6  2026-06-30 12:26:43.329500+01:00              163.0  164.0  120.0  155.0  180.0  192.0
7  2026-06-30 12:31:43.329000+01:00              162.0  162.0  116.0  153.0  181.0  194.0
8  2026-06-30 12:36:43.328500+01:00              162.0  162.0  113.0  152.0  183.0  197.0
9  2026-06-30 12:41:43.328000+01:00              161.0  161.0  109.0  151.0  183.0  197.0
10 2026-06-30 12:46:43.327500+01:00              162.0  162.0  107.0  151.0  186.0  201.0
11 2026-06-30 12:51:43.327000+01:00              161.0  160.0  104.0  149.0  186.0  201.0

>>> print(predictions.mmol_l)
                          timestamp  predicted_glucose  q10  q25  q50   q75   q90
0  2026-06-30 11:56:43.332500+01:00                8.7  8.7  8.2  8.6   8.8   9.0
1  2026-06-30 12:01:43.332000+01:00                8.8  8.8  7.9  8.7   9.2   9.4
2  2026-06-30 12:06:43.331500+01:00                8.9  8.8  7.6  8.7   9.4   9.8
3  2026-06-30 12:11:43.331000+01:00                8.9  8.9  7.3  8.6   9.5  10.0
4  2026-06-30 12:16:43.330500+01:00                9.0  8.9  7.1  8.7   9.8  10.3
5  2026-06-30 12:21:43.330000+01:00                9.0  9.0  6.9  8.6   9.8  10.4
6  2026-06-30 12:26:43.329500+01:00                9.0  9.1  6.7  8.6  10.0  10.7
7  2026-06-30 12:31:43.329000+01:00                9.0  9.0  6.4  8.5  10.0  10.8
8  2026-06-30 12:36:43.328500+01:00                9.0  9.0  6.3  8.4  10.2  10.9
9  2026-06-30 12:41:43.328000+01:00                8.9  8.9  6.0  8.4  10.2  10.9
10 2026-06-30 12:46:43.327500+01:00                9.0  9.0  5.9  8.4  10.3  11.2
11 2026-06-30 12:51:43.327000+01:00                8.9  8.9  5.8  8.3  10.3  11.2
```

### What do these predictions mean?
- `predicted-glucose`: The most likely trajectory your blood sugar will take (centred baseline of the confidence bands).
- `q10` to `q90`: The range of confidence bands provide a realistic upper and lower estimate boundaries, showing the full probability distribution of predicted glucose values.

## Event Modelling
To account for the key exogenous events (e.g., insulin administration or carbohydrate (carbs) intake) that act on blood glucose values without distorting the underlying TimesFM probability distribution, you can apply a deterministic overlay to your baseline forecast.

Drawing on mathematical frameworks utilised in closed-loop Artifical Pancreas systems and the Hovorka/Bergman meal submodels, event impacts are computed as a second-order linear delay process. Here, event unit rates (e.g., the absorption of insulin or carbs) are translated into a physiological curve that begins slowly, reaches a peak, and then gradually decays over time.

By default, `forecose` updates the forecast predictions using the standard clinical baselines (a 55-minute peak for insulin, and a 40-minute peak for carbs):

```python
>>> carb_predictions = predictions.add_event(type="carbs", units=30, minutes_ago=0)
>>> print(carb_predictions.mmol_l)
                          timestamp  predicted_glucose   q10  q25   q50   q75   q90
0  2026-06-30 11:56:43.332500+01:00                8.7   8.7  8.2   8.7   8.9   9.0
1  2026-06-30 12:01:43.332000+01:00                9.0   9.0  8.0   8.8   9.3   9.5
2  2026-06-30 12:06:43.331500+01:00                9.3   9.2  8.0   9.0   9.8  10.2
3  2026-06-30 12:11:43.331000+01:00                9.5   9.5  7.9   9.2  10.2  10.6
4  2026-06-30 12:16:43.330500+01:00                9.9   9.8  8.0   9.5  10.7  11.2
5  2026-06-30 12:21:43.330000+01:00               10.2  10.2  8.1   9.8  11.0  11.6
6  2026-06-30 12:26:43.329500+01:00               10.5  10.5  8.1  10.0  11.4  12.1
7  2026-06-30 12:31:43.329000+01:00               10.8  10.8  8.2  10.3  11.8  12.5
8  2026-06-30 12:36:43.328500+01:00               11.0  11.0  8.3  10.5  12.2  13.0
9  2026-06-30 12:41:43.328000+01:00               11.3  11.3  8.4  10.8  12.5  13.3
10 2026-06-30 12:46:43.327500+01:00               11.7  11.7  8.6  11.0  13.0  13.8
11 2026-06-30 12:51:43.327000+01:00               11.9  11.8  8.7  11.2  13.3  14.1

>>> insulin_predictions = predictions.add_event(type="insulin", units=5, minutes_ago=0)
>>> print(insulin_predictions.mmol_l)
                          timestamp  predicted_glucose  q10  q25  q50  q75  q90
0  2026-06-30 11:56:43.332500+01:00                8.6  8.6  8.1  8.5  8.8  8.9
1  2026-06-30 12:01:43.332000+01:00                8.7  8.7  7.7  8.5  9.0  9.2
2  2026-06-30 12:06:43.331500+01:00                8.5  8.5  7.3  8.3  9.0  9.4
3  2026-06-30 12:11:43.331000+01:00                8.3  8.4  6.8  8.0  9.0  9.4
4  2026-06-30 12:16:43.330500+01:00                8.2  8.1  6.3  7.8  8.9  9.4
5  2026-06-30 12:21:43.330000+01:00                7.8  7.8  5.8  7.4  8.7  9.3
6  2026-06-30 12:26:43.329500+01:00                7.5  7.6  5.2  7.1  8.5  9.2
7  2026-06-30 12:31:43.329000+01:00                7.2  7.2  4.6  6.7  8.2  8.9
8  2026-06-30 12:36:43.328500+01:00                6.8  6.8  4.1  6.2  7.9  8.7
9  2026-06-30 12:41:43.328000+01:00                6.4  6.4  3.5  5.8  7.6  8.4
10 2026-06-30 12:46:43.327500+01:00                6.0  6.0  3.0  5.4  7.4  8.2
11 2026-06-30 12:51:43.327000+01:00                5.6  5.6  2.4  4.9  7.0  7.8
```

By default, sensitivity to insulin (ISF) and carbohydrates (CSF) is set at 40 mg/dL per 1U and 4 mg/dL per gram, respectively. These values are placeholders meant to represent reasonable values and should be adjusted through the `add_event` method using the `tau` and `sensitivity` parameters. In future, I hope to develop a method for calculating estimate values from historic data.

```python
>>> insensitive_insulin_predictions = predictions.add_event(type="insulin", units=5, minutes_ago=0, sensitivity=20.0)
>>> print(insensitive_insulin_predictions.mmol_l)
                          timestamp  predicted_glucose  q10  q25  q50  q75  q90
0  2026-06-30 11:56:43.332500+01:00                8.7  8.7  8.2  8.6  8.8  9.0
1  2026-06-30 12:01:43.332000+01:00                8.8  8.8  7.8  8.6  9.1  9.3
2  2026-06-30 12:06:43.331500+01:00                8.7  8.7  7.4  8.5  9.2  9.6
3  2026-06-30 12:11:43.331000+01:00                8.6  8.7  7.0  8.3  9.3  9.7
4  2026-06-30 12:16:43.330500+01:00                8.5  8.5  6.7  8.2  9.3  9.8
5  2026-06-30 12:21:43.330000+01:00                8.4  8.4  6.4  8.0  9.3  9.9
6  2026-06-30 12:26:43.329500+01:00                8.3  8.4  5.9  7.9  9.3  9.9
7  2026-06-30 12:31:43.329000+01:00                8.0  8.0  5.5  7.5  9.1  9.8
8  2026-06-30 12:36:43.328500+01:00                7.9  7.9  5.2  7.3  9.0  9.8
9  2026-06-30 12:41:43.328000+01:00                7.7  7.7  4.8  7.1  8.9  9.7
10 2026-06-30 12:46:43.327500+01:00                7.5  7.5  4.5  6.9  8.9  9.7
11 2026-06-30 12:51:43.327000+01:00                7.3  7.2  4.1  6.6  8.7  9.5
```