"""
Script to download data from a specified list of stations into a pandas dataframe
takes an input file which contains site information (see sites.conf)
"""

from util import get_config
from argparse import ArgumentParser
import ulmo
import numpy as np
import pandas as pd
import pdb

def download_data(stnid, wban, config):
    """
    Function to get data using ulmo and save to directory
    Config file determines which sites to pull and where to store data
    """
    archive_dir = '{}/ncdc/'.format(config['ARCHIVE_DIR'])
    data = ulmo.ncdc.ghcn_daily.get_data(wban, as_dataframe=True)
    print('Got data -- length {}'.format(len(data['TMAX'])))

    # collect and reformat various data types
    tmax = np.round((data['TMAX'].copy().values[:, 0].astype('float')) / 10. * 9. / 5. + 32., 0)
    tmin = np.round((data['TMIN'].copy().values[:, 0].astype('float')) / 10. * 9. / 5. + 32., 0)
    if 'PRCP' in data.keys():
        precip = np.round((data['PRCP'].copy().values[:, 0].astype('float')) / 2.54 / 100., 2)
    else:
        precip = []

    # convert and combine into dataframe
    tmax = pd.Series(tmax, index=data['TMAX'].index.astype('datetime64'))
    tmin = pd.Series(tmin, index=data['TMIN'].index.astype('datetime64'))
    if len(precip) > 0:
        precip = pd.Series(precip, index=data['PRCP'].index.astype('datetime64'))
    else:
        precip = pd.Series()

    df = pd.DataFrame(index=tmax.index, columns=['tmax', 'tmin', 'precip'])
    df['tmax'] = tmax
    df['tmin'] = tmin
    df['precip'] = precip

    # drop where all columns are missing data
    df = df.dropna(thresh=1)
    # save as pickle
    df.to_pickle('{}/{}_ncdc.p'.format(archive_dir, stnid))

    pdb.set_trace()

    print('got data for {}'.format(stnid))

    return
