"""
Script to run and update the weekly weather table
"""

import sys
import os
import glob
import warnings
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pdb
from argparse import ArgumentParser

import util
import db
from download import ncdc
from normals import normals
from stats import stats

def main(args):
    """
    Main running script
    """

    # Get the config file.
    config = util.get_config(args.config)

    # Get the station metadata
    stn_metadata = pd.read_csv(config['STATION_FILE'])

    # create the dataframe that we will be populating
    df = pd.DataFrame(index=stn_metadata['stnid'].values, columns=config['Database']['COLUMNS'])
    df['region'] = stn_metadata['region'].values
    df['name'] = stn_metadata['name'].values

    # check for NCDC file, download if missing
    print('Checking for NCDC files')
    ncdc_files = glob.glob('{}ncdc/*_ncdc.p'.format(config['ARCHIVE_DIR']))
    for stnid in df.index.values:
        ncdc_filename = '{}ncdc/{}_ncdc.p'.format(config['ARCHIVE_DIR'], stnid)
        if ncdc_filename not in ncdc_files or args.d_ncdc is True:
            wban = 'USW000{}'.format(stn_metadata[stn_metadata['stnid'] == 'ksea']['wban'].values[0])
            print('no NCDC data for {}, downloading now'.format(stnid))
            ncdc.download_data(stnid, wban, config)
        else:
            print('NCDC data found for {}'.format(stnid))

    # find dates for start and end of week and water year
    dt_today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start, week_end = util.get_week(dt_today)
    wy_start = util.get_water_year(dt_today)

    # compute normals: average weekly temp, growing degree days (starts 1-Jan
    print('Computing normals and obs')
    df_normals = pd.DataFrame(index=df.index, columns=['t_avg_week', 'dd', 'precip_week', 'precip_wy'])
    year_range = [int(config['Normals']['start_year']), int(config['Normals']['end_year'])]
    for stnid in df.index.values:
        stn_data = pd.read_pickle('{}ncdc/{}_ncdc.p'.format(config['ARCHIVE_DIR'], stnid))
        # due to rounding issues we add a slight increase to the even F temperatures
        stn_data['tmax'] += 0.0001
        stn_data['tmin'] += 0.0001
        # normals
        df_normals.loc[stnid]['t_avg_week'] = normals.compute_avg_t(stn_data, year_range, week_start, week_end)
        df_normals.loc[stnid]['dd'] = normals.compute_avg_dd(stn_data, year_range, week_end)
        df_normals.loc[stnid]['precip_week'] = normals.compute_avg_precip(stn_data, year_range, week_start, week_end)
        df_normals.loc[stnid]['precip_wy'] = normals.compute_wy_avg_precip(stn_data, year_range, wy_start, week_end)

        # stats (obs)
        df.loc[stnid]['hi'], df.loc[stnid]['lo'], df.loc[stnid]['avg'] = \
            stats.compute_temp_stats(stn_data, week_start, week_end)
        df.loc[stnid]['dd_total'] = stats.compute_dd(stn_data, datetime(week_start.year, 1, 1), week_end)
        df.loc[stnid]['precip_week'], df.loc[stnid]['precip_week_days'] = \
            stats.compute_precip(stn_data, week_start, week_end)
        df.loc[stnid]['precip_wy'], df.loc[stnid]['precip_wy_days'] = \
            stats.compute_precip(stn_data, wy_start, week_end)

        # departures from normals / filling in everything else
        df.loc[stnid]['dfn'] = df.loc[stnid]['avg'] - df_normals.loc[stnid]['t_avg_week']
        df.loc[stnid]['dd_dfn'] = df.loc[stnid]['dd_total'] - df_normals.loc[stnid]['dd']
        df.loc[stnid]['precip_week_dfn'] = df.loc[stnid]['precip_week'] - df_normals.loc[stnid]['precip_week']
        df.loc[stnid]['precip_wy_dfn'] = df.loc[stnid]['precip_wy'] - df_normals.loc[stnid]['precip_wy']
        df.loc[stnid]['precip_wy_pctnormal'] = \
            np.around((df.loc[stnid]['precip_wy'] / df_normals.loc[stnid]['precip_wy'])*100., 0).astype('int')

    # save normals file
    start_str = week_start.strftime('%Y%m%d')
    end_str = week_end.strftime('%Y%m%d')
    out_filename = '{}weekly_data/weekly_{}to{}.p'.format(config['ARCHIVE_DIR'], start_str, end_str)
    pd.to_pickle(df, out_filename)

    pdb.set_trace()



    # save the final file



    pdb.set_trace()
    """
    # Step 1: check the database initialization
    print('fcst_engine.engine: running database initialization checks')
    add_sites = fcst_engine.db.init(config)

    # Check for backfill-historical sites
    if args.b_stid is not None:
        print('fcst_engine.engine: running backfill of historical data')
        if len(args.b_stid) == 0:
            print('fcst_engine.engine: all sites selected')
            sites = config['Stations'].keys()
        else:
            sites = args.b_stid
        for stid in sites:
            historical(config, stid)
        sys.exit(0)

    # Check for database resets
    if args.r_stid is not None:
        print('fcst_engine.engine: performing database reset')
        if len(args.r_stid) == 0:
            print('fcst_engine.engine: error: no sites selected!')
            sys.exit(1)
        for stid in args.r_stid:
            fcst_engine.db.remove(config, stid)
        sys.exit(0)

    # Step 2: for each site in add_sites above, run historical data
    for stid in add_sites:
        historical(config, stid)

    # Steps 3-6: run services!
    for service_group in config['Engine']['Services'].keys():
        # Make sure we have defined a group to do what this asks
        if service_group not in service_groups:
            print('fcst_engine.engine warning: doing nothing for services in %s' % service_group)
            continue
        for service in config['Engine']['Services'][service_group]:
            # Execute the service
            try:
                get_object(service).main(config)
            except BaseException as e:
                print('fcst_engine.engine warning: failed to run service %s' % service)
                print("*** Reason: '%s'" % str(e))
                if config['traceback']:
                    raise
    """