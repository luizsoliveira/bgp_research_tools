import argparse
import os
import sys
from datetime import datetime

src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(src_dir)

from data_download.clients.ripe_client import RIPEClient

def convert_datetime(date_time_input):
    format="%Y%m%dT%H%M%S"
    try:
        return datetime.strptime(date_time_input, format)
    except ValueError:
        sys.exit(f"ABORTING: ERROR. The input \"{date_time_input}\" does not match format {format}.")

def data_download(datetime_start, datetime_end, rrc=4, site_collection='ripe', max_concurrent_requests=32, cacheLocation=False):
    client = RIPEClient(max_concurrent_requests=32, debug=True, cacheLocation=cacheLocation)
    return client.download_updates_interval_files(datetime_start,
                                            datetime_end, int(rrc))
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser('CLI for Download module of BGP Research Software')

    parser.add_argument('--site-collection', dest='site_collection', default='ripe', choices=['ripe'], help='Choose a site collection that can be ripe or route-views (not available yet)')
    parser.add_argument('--from', dest='datetime_start', type=str, required=True, help='Choose a datetime to start download in the format: yyyymmddThhmmss. Example: 20030521T080100 ')
    parser.add_argument('--to', dest='datetime_end', type=str, required=True, help='Choose a datetime to start download in the format: yyyymmddThhmmss. Example: 20030521T080100 ')
    parser.add_argument('--rrc', dest='rrc', type=int, default=4, help='Choose a RRC')
    parser.add_argument('--max-concurrent-requests', dest='max_concurrent_requests', type=int, default=32, help='Choose a number of max concurrent requests')
    parser.add_argument('--mrt-cache-directory', dest='mrt_cache_directory', type=str, default=False, help='Directory location to save and retrieve (cache) the downloaded MRT files.')

    args = parser.parse_args()

    datetime_start = convert_datetime(args.datetime_start)
    datetime_end = convert_datetime(args.datetime_end)

    for file in data_download(datetime_start, datetime_end, rrc=args.rrc, site_collection=args.site_collection, max_concurrent_requests=args.max_concurrent_requests, cacheLocation=args.mrt_cache_directory):
        print(file['file_path'])
    