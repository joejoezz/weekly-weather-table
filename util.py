"""
utility functions
"""

from datetime import datetime, timedelta

def get_config(config_path):
    """
    Retrieve the config dictionary from config_path.
    Written by Jonathan Weyn jweyn@uw.edu
    Modified by Joe Zagrodnik joe.zagrodnik@wsu.edu
    """
    import configobj
    try:
        config_dict = configobj.ConfigObj(config_path, file_error=True)
    except IOError:
        print('Error: unable to open configuration file %s' % config_path)
        raise
    except configobj.ConfigObjError as e:
        print('Error while parsing configuration file %s' % config_path)
        print("*** Reason: '%s'" % e)
        raise

    return config_dict


def get_week(dt_today):
    # find dates of last week (monday - sunday)
    sunday_offset = (dt_today.weekday() - 6) % 7
    week_end = dt_today - timedelta(sunday_offset)
    week_start = dt_today - timedelta(sunday_offset + 6)
    return week_start, week_end


def get_water_year(dt_today):
    # find start date of current water year
    if dt_today.month < 10:
        wy_start = datetime(dt_today.year-1, 10, 1)
    else:
        wy_start = datetime(dt_today.year, 10, 1)
    return wy_start


