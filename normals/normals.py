"""
compete weekly normals and seasonal normals
these functions all take dataframes with the following column names:
'tmax' = high temp
'tmin' = low temp
'precip' = daily precipitation
"""

import numpy as np
import pandas as pd
import util
from datetime import datetime, timedelta

def compute_avg_t(stn_data, year_range, start_date, end_date):
    # computes average temperature from highs and lows between specified dates
    stn_data = extract_date_range(stn_data, year_range, start_date, end_date)
    tmax = np.nanmean(stn_data['tmax'])
    tmin = np.nanmean(stn_data['tmin'])
    tavg = np.around(np.nanmean([tmax+tmin]) * 0.5, 0).astype('int')
    return tavg


def compute_avg_dd(stn_data, year_range, end_date):
    # computes average growing degree days
    start_date = end_date.replace(month=1, day=1)
    stn_data = extract_date_range(stn_data, year_range, start_date, end_date)
    dd_yearly = []
    current_year = year_range[0]
    while current_year <= year_range[1]:
        good_data = stn_data[stn_data.index.year == current_year]
        tmean = (good_data['tmax'] + good_data['tmin']) * 0.5
        dd_daily = tmean - 50
        dd_daily[dd_daily < 0] = 0
        nulls = util.count_nulls([tmean])
        if nulls == 0:
            dd_yearly.append(np.sum(dd_daily))
        current_year += 1
    dd_avg = np.round(np.mean(dd_yearly), 0).astype('int')
    return dd_avg


def compute_wy_avg_precip(stn_data, year_range, wy_start, end_date):
    # compute accumulated precip in water year
    precip_yearly = []
    year_range[0] = year_range[0] - 1
    current_year = year_range[0]
    stn_data = extract_date_range(stn_data, year_range, wy_start, end_date)
    while current_year <= year_range[1] - 1:
        start_tmp = wy_start.replace(year=current_year)
        end_tmp = end_date.replace(year=current_year + 1)
        good_loc = np.where((stn_data.index.to_series() >= start_tmp) & (stn_data.index <= end_tmp))[0]
        good_data = stn_data.loc[stn_data.index[good_loc]]
        nulls = util.count_nulls([good_data['precip']])
        # allow up to 2 nulls for WY precip
        if nulls < 3:
            precip_yearly.append(np.sum(good_data['precip']))
        current_year += 1
    precip_avg = np.round(np.mean(precip_yearly), 2)
    return precip_avg


def compute_avg_precip(stn_data, year_range, start_date, end_date):
    # computes average accumulated precip
    # water year can overlap two years, have to be careful with year selection
    # water year also begins the year before (i.e WY 2020 is Oct 2019-Sep 2020)
    precip_yearly = []
    current_year = year_range[0]
    if start_date.year == end_date.year:
        stn_data = extract_date_range(stn_data, year_range, start_date, end_date)
        while current_year <= year_range[1]:
            good_data = stn_data[stn_data.index.year == current_year]
            nulls = util.count_nulls([good_data['precip']])
            if nulls == 0:
                precip_yearly.append(np.sum(good_data['precip']))
            current_year += 1
    else:
        # if year overlaps, push back year_range of start_year
        year_range[0] -= 1
        stn_data = extract_date_range(stn_data, year_range, start_date, end_date)
        while current_year <= year_range[1]-1:
            start_tmp = start_date.replace(year=current_year)
            end_tmp = end_date.replace(year=current_year+1)
            good_loc = np.where((stn_data.index.to_series() >= start_tmp) & (stn_data.index <= end_tmp))[0]
            good_data = stn_data.loc[stn_data.index[good_loc]]
            nulls = util.count_nulls([good_data['precip']])
            if nulls == 0:
                precip_yearly.append(np.sum(good_data['precip']))
            current_year += 1
    precip_avg = np.round(np.mean(precip_yearly), 2)
    return precip_avg


def extract_date_range(stn_data, year_range, start_date, end_date):
    """
    extract a portion of a stn_data array between start date and end date to compute normals
    there is probably a more elegant way to do this but current version works
    """
    # truncate to the normal period defined by year range
    stn_data = stn_data[(stn_data.index.year >= year_range[0]) & (stn_data.index.year <= year_range[1])]

    # create a new column of month-day strings
    months = np.char.zfill(stn_data.index.month.values.astype('str'),2 )
    days = np.char.zfill(stn_data.index.day.values.astype('str'), 2)
    mmdd = np.core.defchararray.add(months, days)
    stn_data['mmdd'] = pd.Series(mmdd, index=stn_data.index)

    # get the approved list of mmdd
    good_mmdd = []
    while start_date <= end_date:
        good_mmdd.append(str(start_date.month).zfill(2)+str(start_date.day).zfill(2))
        start_date += timedelta(days=1)

    # truncate stn_data to the desired dates
    stn_data = stn_data[stn_data['mmdd'].isin(good_mmdd)]
    stn_data = stn_data.drop(columns='mmdd')
    return stn_data


