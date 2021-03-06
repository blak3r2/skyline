"""
Skyline functions

These are shared functions that are required in multiple modules.
"""
import logging
import traceback
from time import time
import socket

from os.path import dirname, join, abspath, isfile
from os import path
import json
import requests
try:
    import urlparse
except ImportError:
    import urllib.parse
try:
    import urllib2
except ImportError:
    import urllib.request
    import urllib.error
import datetime

import settings

try:
    from settings import GRAPHITE_HOST
except:
    GRAPHITE_HOST = ''
try:
    from settings import CARBON_PORT
except:
    CARBON_PORT = ''

config = {'user': settings.PANORAMA_DBUSER,
          'password': settings.PANORAMA_DBUSERPASS,
          'host': settings.PANORAMA_DBHOST,
          'port': settings.PANORAMA_DBPORT,
          'database': settings.PANORAMA_DATABASE,
          'raise_on_warnings': True}


def send_graphite_metric(current_skyline_app, metric, value):
    """
    Sends the skyline_app metrics to the `GRAPHITE_HOST` if a graphite
    host is defined.

    :param current_skyline_app: the skyline app using this function
    :param metric: the metric namespace
    :param value: the metric value
    :return: ``True`` or ``False``
    :rtype: boolean

    """
    if GRAPHITE_HOST != '':

        sock = socket.socket()
        sock.settimeout(10)

        # Handle connection error to Graphite #116 @etsy
        # Fixed as per https://github.com/etsy/skyline/pull/116 and
        # mlowicki:etsy_handle_connection_error_to_graphite
        # Handle connection error to Graphite #7 @ earthgecko
        # merged 1 commit into earthgecko:master from
        # mlowicki:handle_connection_error_to_graphite on 16 Mar 2015
        try:
            sock.connect((GRAPHITE_HOST, CARBON_PORT))
            sock.settimeout(None)
        except socket.error:
            sock.settimeout(None)
            endpoint = '%s:%d' % (GRAPHITE_HOST, CARBON_PORT)
            current_skyline_app_logger = current_skyline_app + 'Log'
            current_logger = logging.getLogger(current_skyline_app_logger)
            current_logger.error(
                'error :: cannot connect to Graphite at %s' % endpoint)
            return False

        # For the same reason as above
        # sock.sendall('%s %s %i\n' % (name, value, time()))
        try:
            sock.sendall('%s %s %i\n' % (metric, value, time()))
            sock.close()
            return True
        except:
            endpoint = '%s:%d' % (GRAPHITE_HOST, CARBON_PORT)
            current_skyline_app_logger = current_skyline_app + 'Log'
            current_logger = logging.getLogger(current_skyline_app_logger)
            current_logger.error(
                'error :: could not send data to Graphite at %s' % endpoint)
            return False

    return False


def mkdir_p(path):
    """
    Create nested directories.

    :param path: directory path to create

    :return: returns True

    """
    try:
        os.getpid()
    except:
        import os
    try:
        python_version
    except:
        from sys import version_info
        python_version = int(version_info[0])
    try:
        if python_version == 2:
            mode_arg = int('0755')
        if python_version == 3:
            mode_arg = mode=0o755
        os.makedirs(path, mode_arg)
        return True
    # Python >2.5
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def load_metric_vars(current_skyline_app, metric_vars_file):
    """
    Import the metric variables for a check from a metric check variables file

    :param metric_vars_file: the path and filename to the metric variables files

    :return: returns True

    """
    try:
        os.getpid()
    except:
        import os

    try:
        imp
    except:
        import imp

    if os.path.isfile(metric_vars_file):
        current_skyline_app_logger = current_skyline_app + 'Log'
        current_logger = logging.getLogger(current_skyline_app_logger)
        current_logger.info(
            'loading metric variables from import - metric_check_file - %s' % (
                str(metric_vars_file)))
        # Bug #1460: panorama check file fails
        # global metric_vars
        # current_logger.info('set global metric_vars')
        with open(metric_vars_file) as f:
            try:
                metric_vars = imp.load_source('metric_vars', '', f)
                if settings.ENABLE_DEBUG:
                    current_logger.info(
                        'metric_vars determined - metric variable - metric - %s' % str(metric_vars.metric))
            except:
                current_logger.info(traceback.format_exc())
                msg = 'failed to import metric variables - metric_check_file'
                current_logger.error(
                    'error :: %s - %s' % (msg, str(metric_vars_file)))
                metric_vars = False

    return metric_vars


def write_data_to_file(current_skyline_app, write_to_file, mode, data):
    """
    Write date to a file

    :param current_skyline_app: the skyline app using this function
    :param file: the path and filename to write the data into
    :param mode: ``w`` to overwrite, ``a`` to append
    :param data: the data to write to the file

    :return: returns True

    """
    try:
        os.getpid()
    except:
        import os

    try:
        python_version
    except:
        from sys import version_info
        python_version = int(version_info[0])

    file_dir = os.path.dirname(write_to_file)
    if not os.path.exists(file_dir):
        try:
            if python_version == 2:
                mode_arg = int('0755')
            if python_version == 3:
                mode_arg = mode=0o755
            os.makedirs(file_dir, mode_arg)
        # Python >2.5
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    if not os.path.exists(file_dir):
        current_skyline_app_logger = current_skyline_app + 'Log'
        current_logger = logging.getLogger(current_skyline_app_logger)
        current_logger.error(
            'error :: could not create directory - %s' % (str(file_dir)))

    try:
        with open(write_to_file, mode) as fh:
            fh.write(data)
        if python_version == 2:
            mode_arg = int('0644')
        if python_version == 3:
            mode_arg = '0o644'
        os.chmod(write_to_file, mode_arg)

        return True
    except:
        return False

    return False


def fail_check(current_skyline_app, failed_check_dir, check_file_to_fail):
    """
    Move a failed check file.

    :param current_skyline_app: the skyline app using this function
    :param failed_check_dir: the directory where failed checks are moved to
    :param check_file_to_fail: failed check file to move

    :return: ``True``, ``False`` ``pass``

    """
    try:
        os.getpid()
    except:
        import os

    try:
        shutil
    except:
        import shutil

    try:
        python_version
    except:
        from sys import version_info
        python_version = int(version_info[0])

    current_skyline_app_logger = current_skyline_app + 'Log'
    current_logger = logging.getLogger(current_skyline_app_logger)

    if not os.path.exists(failed_check_dir):
        try:
            mkdir_p(failed_check_dir)
            if settings.ENABLE_PANORAMA_DEBUG or settings.ENABLE_CRUCIBLE_DEBUG:
                current_logger.info(
                    'created failed_check_dir - %s' % str(failed_check_dir))
        except:
            current_logger.error(
                'error :: failed to create failed_check_dir - %s' %
                str(failed_check_dir))
            current_logger.info(traceback.format_exc())
            return False

    check_file_name = os.path.basename(str(check_file_to_fail))
    failed_check_file = '%s/%s' % (failed_check_dir, check_file_name)

    try:
        shutil.move(check_file_to_fail, failed_check_file)
        if python_version == 2:
            mode_arg = int('0644')
        if python_version == 3:
            mode_arg = '0o644'
        os.chmod(failed_check_file, mode_arg)

        current_logger.info('moved check file to - %s' % failed_check_file)
        return True
    except OSError:
        msg = 'failed to move check file to -%s' % failed_check_file
        current_logger.error('error :: %s' % msg)
        current_logger.info(traceback.format_exc())
        pass

    return False


def alert_expiry_check(current_skyline_app, metric, metric_timestamp, added_by):
    """
    Only check if the metric does not a EXPIRATION_TIME key set, panorama
    uses the alert EXPIRATION_TIME for the relevant alert setting contexts
    whether that be analyzer, mirage, boundary, etc and sets its own
    cache_keys in redis.  This prevents large amounts of data being added
    in terms of duplicate anomaly records in Panorama and timeseries json and
    image files in crucible samples so that anomalies are recorded at the same
    EXPIRATION_TIME as alerts.

    :param current_skyline_app: the skyline app using this function
    :param metric: metric name
    :param added_by: which app requested the alert_expiry_check

    :return: ``True``, ``False`` ``pass``

    - If in alert expiry period returns ```True```
    - If not in alert expiry period or unknown returns ```False```
    """

    try:
        re
    except:
        import re

    current_skyline_app_logger = current_skyline_app + 'Log'
    current_logger = logging.getLogger(current_skyline_app_logger)

    cache_key = 'last_alert.%s.%s.%s' % (current_skyline_app, added_by, metric)
    try:
        last_alert = self.redis_conn.get(cache_key)
    except:
        current_logger.info(traceback.format_exc())
        current_logger.error(
            'error :: failed to query redis cache key - %s' % cache_key)
        return False

    if added_by == 'analyzer' or added_by == 'mirage':
        if settings.ENABLE_DEBUG:
            current_logger.info('Will check %s ALERTS' % added_by)
        if settings.ENABLE_ALERTS:
            if settings.ENABLE_DEBUG:
                current_logger.info('Checking %s ALERTS' % added_by)

            for alert in settings.ALERTS:
                ALERT_MATCH_PATTERN = alert[0]
                METRIC_PATTERN = metric
                alert_match_pattern = re.compile(ALERT_MATCH_PATTERN)
                pattern_match = alert_match_pattern.match(METRIC_PATTERN)
                if pattern_match:
                    expiration_timeout = alert[2]
                    if settings.ENABLE_DEBUG:
                        msg = 'matched - %s - %s - EXPIRATION_TIME is %s' % (
                            added_by, metric, str(expiration_timeout))
                        current_logger.info('%s' % msg)
                    check_age = int(check_time) - int(metric_timestamp)
                    if int(check_age) > int(expiration_timeout):
                        check_expired = True
                        if settings.ENABLE_DEBUG:
                            msg = 'the check is older than EXPIRATION_TIME for the metric - not checking - check_expired'
                            current_logger.info('%s' % msg)

    if added_by == 'boundary':
        if settings.BOUNDARY_ENABLE_ALERTS:
            for alert in settings.BOUNDARY_METRICS:
                ALERT_MATCH_PATTERN = alert[0]
                METRIC_PATTERN = metric
                alert_match_pattern = re.compile(ALERT_MATCH_PATTERN)
                pattern_match = alert_match_pattern.match(METRIC_PATTERN)
                if pattern_match:
                    source_app = 'boundary'
                    expiration_timeout = alert[2]
                    if settings.ENABLE_DEBUG:
                        msg = 'matched - %s - %s - EXPIRATION_TIME is %s' % (
                            source_app, metric, str(expiration_timeout))
                        current_logger.info('%s' % msg)
                    check_age = int(check_time) - int(metric_timestamp)
                    if int(check_age) > int(expiration_timeout):
                        check_expired = True
                        if settings.ENABLE_DEBUG:
                            msg = 'the check is older than EXPIRATION_TIME for the metric - not checking - check_expired'
                            current_logger.info('%s' % msg)

    cache_key = '%s.last_check.%s.%s' % (current_skyline_app, added_by, metric)
    if settings.ENABLE_DEBUG:
        current_logger.info(
            'debug :: cache_key - %s.last_check.%s.%s' % (
                current_skyline_app, added_by, metric))

    # Only use the cache_key EXPIRATION_TIME if this is not a request to
    # run_crucible_tests on a timeseries
    if settings.ENABLE_DEBUG:
        current_logger.info('debug :: checking if cache_key exists')
    try:
        last_check = self.redis_conn.get(cache_key)
    except Exception as e:
        current_logger.error(
            'error :: could not query cache_key for %s - %s - %s' % (
                alerter, metric, str(e)))

    if not last_check:
        try:
            self.redis_conn.setex(cache_key, expiration_timeout, packb(value))
            current_logger.info(
                'set cache_key for %s - %s with timeout of %s' % (
                    source_app, metric, str(expiration_timeout)))
        except Exception as e:
            current_logger.error(
                'error :: could not query cache_key for %s - %s - %s' % (
                    alerter, metric, str(e)))
            current_logger.info('all anomaly files will be removed')
            remove_all_anomaly_files = True
    else:
        if check_expired:
            current_logger.info(
                'check_expired - all anomaly files will be removed')
            remove_all_anomaly_files = True
        else:
            current_logger.info(
                'cache_key is set and not expired for %s - %s - all anomaly files will be removed' % (
                    source_app, metric))
            remove_all_anomaly_files = True


def get_graphite_metric(
    current_skyline_app, metric, from_timestamp, until_timestamp, data_type,
        output_object):
    """
    Fetch data from graphite and return it as object or save it as file

    :param current_skyline_app: the skyline app using this function
    :param metric: metric name
    :param from_timestamp: unix timestamp
    :param until_timestamp: unix timestamp
    :param data_type: image or json
    :param output_object: object or path and filename to save data as, if set to
                          object, the object is returned
    """
    try:
        os.getpid()
    except:
        import os

    current_skyline_app_logger = current_skyline_app + 'Log'
    current_logger = logging.getLogger(current_skyline_app_logger)

#    if settings.ENABLE_DEBUG:
    current_logger.info('graphite_metric - %s' % (metric))

    # Graphite timeouts
    connect_timeout = int(settings.GRAPHITE_CONNECT_TIMEOUT)
    if settings.ENABLE_DEBUG:
        current_logger.info('connect_timeout - %s' % str(connect_timeout))

    current_logger.info('connect_timeout - %s' % str(connect_timeout))

    read_timeout = int(settings.GRAPHITE_READ_TIMEOUT)
    if settings.ENABLE_DEBUG:
        current_logger.info('read_timeout - %s' % str(read_timeout))

    current_logger.info('read_timeout - %s' % str(read_timeout))

    graphite_until = datetime.datetime.fromtimestamp(int(until_timestamp)).strftime('%H:%M_%Y%m%d')
    current_logger.info('graphite_until - %s' % str(graphite_until))

    graphite_from = datetime.datetime.fromtimestamp(int(from_timestamp)).strftime('%H:%M_%Y%m%d')
    output_format = data_type

    # graphite URL
    if settings.GRAPHITE_PORT != '':
        image_url = settings.GRAPHITE_PROTOCOL + '://' + settings.GRAPHITE_HOST + ':' + settings.GRAPHITE_PORT + '/render/?from=' + graphite_from + '&until=' + graphite_until + '&target=' + metric
        url = image_url + '&format=' + output_format
    else:
        image_url = settings.GRAPHITE_PROTOCOL + '://' + settings.GRAPHITE_HOST + '/render/?from=' + graphite_from + '&until=' + graphite_until + '&target=' + metric
        url = image_url + '&format=' + output_format
    if settings.ENABLE_DEBUG:
        current_logger.info('graphite url - %s' % (url))

    current_logger.info('graphite url - %s' % (url))

    get_image = False
    if data_type == 'image' and output_object != 'object':
        if not os.path.isfile(output_object):
            get_image = True
        else:
            if settings.ENABLE_DEBUG:
                current_logger.info('graph file exists - %s' % str(output_object))

    if get_image:
        current_logger.info(
            'retrieving png - surfacing %s graph from graphite from %s to %s' % (
                metric, str(graphite_from), str(graphite_until)))

        graphite_image_file = output_object
        if 'width' not in image_url:
            image_url += '&width=586'
        if 'height' not in image_url:
            image_url += '&height=308'
        if settings.ENABLE_DEBUG:
            current_logger.info('graphite image url - %s' % (str(image_url)))
        image_url_timeout = int(connect_timeout)

        image_data = None

        try:
            image_data = urllib2.urlopen(image_url, timeout=image_url_timeout).read()
            current_logger.info('url OK - %s' % (image_url))
        except urllib2.URLError:
            image_data = None
            current_logger.error('error :: url bad - %s' % (image_url))

        if image_data is not None:
            with open(graphite_image_file, 'w') as f:
                f.write(image_data)
            current_logger.info('retrieved - %s' % (graphite_image_file))
            if python_version == 2:
                mode_arg = int('0644')
            if python_version == 3:
                mode_arg = '0o644'
            os.chmod(graphite_image_file, mode_arg)
        else:
            current_logger.error(
                'error :: failed to retrieved - %s' % (graphite_image_file))

        if not os.path.isfile(graphite_image_file):
            msg = 'retrieve failed to surface %s graph from Graphite' % (metric)
            current_logger.error('error :: %s' % msg)

    if data_type == 'json':

        if output_object != 'object':
            if os.path.isfile(output_object):
                return True

        msg = 'surfacing timeseries data for %s from graphite from %s to %s' % (
            metric, graphite_from, graphite_until)
        current_logger.info('%s' % msg)
        if requests.__version__ >= '2.4.0':
            use_timeout = (int(connect_timeout), int(read_timeout))
        else:
            use_timeout = int(connect_timeout)
        if settings.ENABLE_DEBUG:
            current_logger.info('use_timeout - %s' % (str(use_timeout)))

        try:
            r = requests.get(url, timeout=use_timeout)
            js = r.json()
            datapoints = js[0]['datapoints']
            if settings.ENABLE_DEBUG:
                current_logger.info('data retrieved OK')
        except:
            datapoints = [[None, int(graphite_until)]]
            current_logger.error('error :: data retrieval failed')

        converted = []
        for datapoint in datapoints:
            try:
                new_datapoint = [float(datapoint[1]), float(datapoint[0])]
                converted.append(new_datapoint)
            except:
                continue

        if output_object != 'object':
            with open(output_object, 'w') as f:
                f.write(json.dumps(converted))
            if python_version == 2:
                mode_arg = int('0644')
            if python_version == 3:
                mode_arg = '0o644'
            os.chmod(output_object, mode_arg)
            if settings.ENABLE_DEBUG:
                current_logger.info('json file - %s' % output_object)
        else:
            timeseries_json = json.dumps(converted)
            return timeseries_json

        if not os.path.isfile(output_object):
            current_logger.error(
                'error :: failed to surface %s json from graphite' % (metric))
            return False
        else:
            return True

################################################################################


def mysql_select(current_skyline_app, select):
    """
    Select data from mysql database

    :param current_skyline_app: the Skyline app that is calling the function
    :param select: the select string
    :type select: str
    :return: tuple
    :rtype: tuple, boolean

    - **Example usage**::

        from skyline_functions import mysql_select
        query = 'select id, metric from anomalies'
        result = mysql_select(query)

    - **Example of the 0 indexed results tuple, which can hold multiple results**::

        >> print('results: %s' % str(results))
        results: [(1, u'test1'), (2, u'test2')]

        >> print('results[0]: %s' % str(results[0]))
        results[0]: (1, u'test1')

    .. note::
        - If the MySQL query fails a boolean will be returned not a tuple
            * ``False``
            * ``None``

    """
    ENABLE_DEBUG = False
    try:
        if settings.ENABLE_PANORAMA_DEBUG:
            ENABLE_DEBUG = True
    except:
        nothing_to_do = True
    try:
        if settings.ENABLE_WEBAPP_DEBUG:
            ENABLE_DEBUG = True
    except:
        nothing_to_do = True

    current_skyline_app_logger = current_skyline_app + 'Log'
    current_logger = logging.getLogger(current_skyline_app_logger)
    current_logger.info('debug :: entering mysql_select')

    try:
        mysql.connector
    except:
        import mysql.connector
    try:
        conversion
    except:
        from mysql.connector import conversion
    try:
        re
    except:
        import re

    try:
        cnx = mysql.connector.connect(**config)
        if ENABLE_DEBUG:
            current_logger.info('debug :: connected to mysql')
    except mysql.connector.Error as err:
        current_logger.error('error :: mysql error - %s' % str(err))
        current_logger.error('error :: failed to connect to mysql')
        return False

    if cnx:
        try:
            if ENABLE_DEBUG:
                current_logger.info('debug :: %s' % (str(select)))

            # NOTE: when a LIKE SELECT is made the query string is not run
            # through the conversion.MySQLConverter().escape method as it
            # it would not work and kept on returning mysql error - 1064 with
            # multiple single quotes e.g. use near '\'carbon%\'' at line 1
            # Various patterns were attempted to no avail, it seems to be
            # related to % character. pseudo basic HTTP auth has been added to
            # the webapp just in someone does not secure it properly, a little
            # defence in depth, so added WEBAPP_ALLOWED_IPS too.
            pattern_match = None
            try:
                pattern_match = re.search(' LIKE ', str(select))
            except:
                current_logger.error('error :: pattern_match - %s' % traceback_format_exc())
            if not pattern_match:
                try:
                    pattern_match = re.search(' like ', str(select))
                except:
                    current_logger.error('error :: pattern_match - %s' % traceback_format_exc())

            # TBD - not sure how to get it escaping safely
            pattern_match = True
            if pattern_match:
                query = str(select)
                current_logger.info('debug :: unescaped query - %s' % (str(query)))
                cursor = cnx.cursor()
                cursor.execute(query)
            else:
                query = conversion.MySQLConverter().escape(select)
                current_logger.info('debug :: escaped query - %s' % (str(query)))
                cursor = cnx.cursor()
                cursor.execute(query.format(query))

            # cursor = cnx.cursor()
            # cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            cnx.close()
            return result
        except mysql.connector.Error as err:
            current_logger.error('error :: mysql error - %s' % str(err))
            current_logger.error(
                'error :: failed to query database - %s' % (str(select)))
            try:
                cnx.close()
                return False
            except:
                return False
    else:
        if ENABLE_DEBUG:
            current_logger.error('error - failed to connect to mysql')

    # Close the test mysql connection
    try:
        cnx.close()
        return False
    except:
        return False

    return False
