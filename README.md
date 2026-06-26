# forecose

[![PyPI](https://img.shields.io/pypi/v/pydexcom?style=flat-square)](https://pypi.org/project/forecose/)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest.svg?style=flat-square)](https://pypi.org/project/forecose/)

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
>>> predictions = DexcomForecast().get_forecast(dexcom)
>>> print(predictions)
                          timestamp  predicted_glucose         q10         q25         q50         q75         q90
0  2026-06-26 11:41:22.163000+01:00         123.036758  122.259880  114.010910  121.040176  126.698639  130.737625
1  2026-06-26 11:46:22.163000+01:00         117.917084  119.255325  103.586609  114.847458  124.962013  130.337677
2  2026-06-26 11:51:22.163000+01:00         112.936745  114.285713   93.414429  108.460175  122.032082  130.147263
3  2026-06-26 11:56:22.163000+01:00         108.864471  111.334473   85.159195  103.118362  120.449158  129.664490
4  2026-06-26 12:01:22.163000+01:00         105.268646  110.067360   77.075996   98.538086  119.166481  129.867401
5  2026-06-26 12:06:22.163000+01:00         102.510818  108.663223   71.013176   94.973129  118.314079  130.784134
6  2026-06-26 12:11:22.163000+01:00         100.653397  106.934074   66.480339   92.466553  119.067230  132.150269
7  2026-06-26 12:16:22.163000+01:00         100.558281  107.133316   64.823494   91.983261  119.827232  135.091919
8  2026-06-26 12:21:22.163000+01:00         100.579796  109.257736   61.783752   91.251221  122.283157  138.308975
9  2026-06-26 12:26:22.163000+01:00         100.584198  108.955002   59.392654   90.392227  124.204987  140.372147
10 2026-06-26 12:31:22.163000+01:00         100.988571  111.358139   57.296143   89.819542  125.757668  143.972672
11 2026-06-26 12:36:22.163000+01:00         101.895081  112.446609   58.076065   89.992996  128.253937  146.511047

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
`forecose` applies the TimesFM PyTorch model to blood glucose values retrieved from the `pydexcom` Python API interface for Dexcom. The `predicted_glucose` details a point prediction from the resulting probabilistic distribution over the next hour (12x 5 minute interval readings).

The probability quantiles (from `q10` to `q90`) highlights the prediction confidence band and boundaries for the immediate upcoming glucose readings.