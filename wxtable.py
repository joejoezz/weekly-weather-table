"""
Script to run and update the weekly weather table
"""

import sys
import os
import glob
import warnings
import pandas as pd
import pdb
from argparse import ArgumentParser

from util import get_config
import db
from download import download_ncdc
import normals

def main(args):
    """
    Main running script
    """

    # Get the config file.
    config = get_config(args.config)

    # Get the station metadata
    stn_metadata = pd.read_csv(config['STATION_FILE'])

    # create the dataframe that we will be populating
    df = pd.DataFrame(index=stn_metadata['stnid'].values, columns=config['Database']['COLUMNS'])
    df['region'] = stn_metadata['region'].values
    df['name'] = stn_metadata['name'].values

    # check for NCDC file, download if missing
    ncdc_files = glob.glob('{}ncdc/*_ncdc.p'.format(config['ARCHIVE_DIR']))
    for stnid in df.index.values:
        ncdc_filename = '{}ncdc/{}_ncdc.p'.format(config['ARCHIVE_DIR'], stnid)
        if ncdc_filename not in ncdc_files or args.d_ncdc is True:
            wban = 'USW000{}'.format(stn_metadata[stn_metadata['stnid'] == 'ksea']['wban'].values[0])
            print('no NCDC data for {}, downloading now'.format(stnid))
            download_ncdc.download_data(stnid, wban, config)
        else:
            print('NCDC data found for {}'.format(stnid))

    # check for normals file, create if missing




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