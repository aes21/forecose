# forecose

[![PyPI](https://img.shields.io/pypi/v/pydexcom?style=flat-square)](https://pypi.org/project/forecose/)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest.svg?style=flat-square)](https://pypi.org/project/forecose/)
[![Tests](https://img.shields.io/github/actions/workflow/status/aes21/forecose/test.yaml?style=flat-square&label=tests)](https://github.com/aes21/forecose/actions/workflows/test.yaml)

A time-series forecasting extension for [pydexcom](https://github.com/gagebenne/pydexcom) using Google's [TimesFM](https://github.com/google-research/timesfm). Readings from the previous 24 hours are captured from the Dexcom Share API service are fed into the model to forecast blood glucose values over the next hour.

> All modelling and forecasting is performed locally on your device. The only external connections made are with:
> - Dexcom Share API: fetching CGM readings following the `pydexcom` approach.
> - HuggingFace: one-time download of the forecasting model weights on the first run.

## Quick Start
1. Ensure that you have installed the `pydexcom` package and [enabled the Share service](https://provider.dexcom.com/education-research/cgm-education-use/videos/setting-dexcom-share-and-follow) within your [Dexcom G7 / G6 / G5 / G4](https://www.dexcom.com/apps).

`pip install pydexcom`

2. Initialise `pydexcom` with your Dexcom credentials (below shows the simplist route, refer to pydexcom for further instruction).

```python
>>> from pydexcom import Dexcom
>>> dexcom = Dexcom(username="username", password="password")
```

3. Generate a prediction.

```python
>>> from forecose import DexcomForecast
>>> predictions = DexcomForecast().get_forecast(dexcom)
>>> print(predictions)
                          timestamp  predicted_glucose  q10  q25  q50  q75  q90
0  2026-06-26 11:41:22.163000+01:00                123  122  114  121  126  130
1  2026-06-26 11:46:22.163000+01:00                117  119  103  114  124  130
2  2026-06-26 11:51:22.163000+01:00                112  114   93  108  122  130
3  2026-06-26 11:56:22.163000+01:00                108  111   85  103  120  129
4  2026-06-26 12:01:22.163000+01:00                105  110   77   98  119  129
5  2026-06-26 12:06:22.163000+01:00                102  108   71   94  118  130
6  2026-06-26 12:11:22.163000+01:00                100  106   66   92  119  132
7  2026-06-26 12:16:22.163000+01:00                100  107   64   91  119  135
8  2026-06-26 12:21:22.163000+01:00                100  109   61   91  122  138
9  2026-06-26 12:26:22.163000+01:00                100  108   59   90  124  140
10 2026-06-26 12:31:22.163000+01:00                100  111   57   89  125  143
11 2026-06-26 12:36:22.163000+01:00                101  112   58   89  128  146

>>> print(predictions.mmol_l)
                          timestamp  predicted_glucose  q10  q25  q50  q75  q90
0  2026-06-26 11:41:22.163000+01:00                6.8  6.8  6.3  6.7  7.0  7.3
1  2026-06-26 11:46:22.163000+01:00                6.5  6.6  5.7  6.4  6.9  7.2
2  2026-06-26 11:51:22.163000+01:00                6.3  6.3  5.2  6.0  6.8  7.2
3  2026-06-26 11:56:22.163000+01:00                6.0  6.2  4.7  5.7  6.7  7.2
4  2026-06-26 12:01:22.163000+01:00                5.8  6.1  4.3  5.5  6.6  7.2
5  2026-06-26 12:06:22.163000+01:00                5.7  6.0  3.9  5.3  6.6  7.3
6  2026-06-26 12:11:22.163000+01:00                5.6  5.9  3.7  5.1  6.6  7.3
7  2026-06-26 12:16:22.163000+01:00                5.6  5.9  3.6  5.1  6.7  7.5
8  2026-06-26 12:21:22.163000+01:00                5.6  6.1  3.4  5.1  6.8  7.7
9  2026-06-26 12:26:22.163000+01:00                5.6  6.0  3.3  5.0  6.9  7.8
10 2026-06-26 12:31:22.163000+01:00                5.6  6.2  3.2  5.0  7.0  8.0
11 2026-06-26 12:36:22.163000+01:00                5.7  6.2  3.2  5.0  7.1  8.1
```

## What do these predictions mean?
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
0  2026-06-29 16:11:30.622000+01:00                9.2   9.3  8.4   9.0   9.3   9.5
1  2026-06-29 16:16:30.628000+01:00                9.3   9.3  8.3   9.2   9.8  10.0
2  2026-06-29 16:21:30.634000+01:00                9.6   9.7  8.1   9.3  10.2  10.6
3  2026-06-29 16:26:30.640000+01:00                9.9   9.9  8.1   9.6  10.6  11.1
4  2026-06-29 16:31:30.646000+01:00               10.2  10.3  8.2   9.8  11.1  11.6
5  2026-06-29 16:36:30.652000+01:00               10.6  10.6  8.2  10.2  11.5  12.2
6  2026-06-29 16:41:30.658000+01:00               10.9  10.9  8.3  10.4  12.0  12.7
7  2026-06-29 16:46:30.664000+01:00               11.3  11.4  8.4  10.8  12.5  13.3
8  2026-06-29 16:51:30.670000+01:00               11.6  11.5  8.5  11.0  12.8  13.6
9  2026-06-29 16:56:30.676000+01:00               11.9  11.8  8.6  11.3  13.3  14.0
10 2026-06-29 17:01:30.682000+01:00               12.2  12.2  8.7  11.5  13.6  14.4
11 2026-06-29 17:06:30.688000+01:00               12.4  12.4  8.8  11.7  13.9  14.7

>>> insulin_predictions = predictions.add_event(type="insulin", units=5, minutes_ago=0)
>>> print(insulin_predictions.mmol_l)
                          timestamp  predicted_glucose  q10  q25  q50  q75  q90
0  2026-06-29 16:11:30.622000+01:00                8.5  8.7  7.8  8.4  8.7  8.9
1  2026-06-29 16:16:30.628000+01:00                8.3  8.3  7.3  8.2  8.8  9.0
2  2026-06-29 16:21:30.634000+01:00                8.0  8.2  6.5  7.8  8.6  9.0
3  2026-06-29 16:26:30.640000+01:00                7.8  7.8  6.0  7.5  8.5  9.0
4  2026-06-29 16:31:30.646000+01:00                7.5  7.6  5.4  7.1  8.4  8.9
5  2026-06-29 16:36:30.652000+01:00                7.2  7.2  4.8  6.8  8.1  8.8
6  2026-06-29 16:41:30.658000+01:00                6.9  6.9  4.3  6.4  8.0  8.7
7  2026-06-29 16:46:30.664000+01:00                6.6  6.7  3.7  6.1  7.8  8.5
8  2026-06-29 16:51:30.670000+01:00                6.2  6.2  3.1  5.6  7.4  8.2
9  2026-06-29 16:56:30.676000+01:00                5.9  5.8  2.6  5.3  7.2  8.0
10 2026-06-29 17:01:30.682000+01:00                5.4  5.5  2.2  4.8  6.9  7.7
11 2026-06-29 17:06:30.688000+01:00                5.1  5.1  2.2  4.3  6.5  7.3
```