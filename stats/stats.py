"""
compete statistics 
these functions all take dataframes with the following column names:
'tmax' = high temp
'tmin' = low temp
'precip' = daily precipitation
"""

import pdb
import numpy as np
import util

def compute_temp_stats(stn_data, start_date, end_date):
    # computes average temperature from highs and lows between specified dates
    tmax = stn_data[start_date:end_date]['tmax']
    tmin = stn_data[start_date:end_date]['tmin']
    nulls = util.count_nulls([tmax, tmin])
    if nulls > 0:
        return np.nan, np.nan, np.nan
    else:
        tmax = np.around(np.max(tmax)).astype('int')
        tmin = np.around(np.min(tmin)).astype('int')
        tmean = np.around(np.mean((np.mean(tmax) + np.mean(tmin))*0.5)).astype('int')
        return tmax, tmin, tmean


def compute_dd(stn_data, start_date, end_date):
    # computes growing degree days
    if start_date.month != 1 and start_date.year != 1:
        raise ValueError('normals.compute_dd error: Growing degree days must have a Jan 1 start date')
    tmax = stn_data[start_date:end_date]['tmax']
    tmin = stn_data[start_date:end_date]['tmin']
    tmean = np.around((tmax + tmin) * 0.5)
    dd_daily = tmean - 50
    dd_daily[dd_daily < 0] = 0
    nulls = util.count_nulls([tmax, tmin])
    if nulls > 0:
        return np.nan
    else:
        return np.sum(dd_daily).astype('int')


def compute_precip(stn_data, start_date, end_date):
    # computes accumulated precip and precip days (for any set of start/end dates)
    precip = stn_data[start_date:end_date]['precip']
    nulls = util.count_nulls([precip])
    if nulls > 0:
        return np.nan, np.nan
    else:
        precip_sum = np.around(np.sum(precip), 2)
        precip_days = len(np.where((precip > 0))[0])
        return precip_sum, precip_days

