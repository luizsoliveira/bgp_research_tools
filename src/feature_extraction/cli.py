import argparse
import os
import sys
import datetime

src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(src_dir)

from data_download.cli import data_download, convert_datetime
from feature_extraction.bgp_cplusplus_feature_extraction import BGPCPlusPlusFeatureExtraction

def append_suffix_on_filename(filename, suffix):
    name, ext = os.path.splitext(filename)
    return f"{name}_{suffix}{ext}"

def split_interval_per_day(datetime_start, datetime_end, day_number):

    if (datetime_end <= datetime_start):
        sys.exit(f"ABORTING: The datetime_end must be greater than datetime_start. Instead, a bigger datetime_start was provided.")

    difference_days = (datetime_end.date() - datetime_start.date()).days + 1
    
    if (day_number < 1 or day_number > difference_days):
        sys.exit(f"ABORTING: For the datetime interval provided the day_number must be between 1 and {difference_days}. Instead, {day_number} was provided.")

    # First second of the desired day
    new_datetime_start = datetime_start.replace(hour=0, minute=0, second=0) + datetime.timedelta(days=(day_number - 1))
    # In case of the first day, use the time provided by the parameter datetime_start
    new_datetime_start = max(new_datetime_start, datetime_start)

    # Last second of the desired day
    new_datetime_end = datetime_start.replace(hour=23, minute=59, second=59) + datetime.timedelta(days=(day_number - 1))
    # In case of the first day, use the time provided by the parameter datetime_end
    new_datetime_end = min(new_datetime_end, datetime_end)

    return new_datetime_start, new_datetime_end


def data_download_and_extract(output_file, datetime_start, datetime_end, rrc=4, site_collection='ripe', max_concurrent_requests=32):
    
    extractor = BGPCPlusPlusFeatureExtraction()
    downloaded_files = []
    
    for file in data_download(datetime_start, datetime_end, rrc, site_collection, max_concurrent_requests):
        print(f"File downloaded: {file['file_path']}")
        downloaded_files.append(file)

    file_extract = extractor.extract_features_from_files(downloaded_files, output_file) #, filter_asn, filter_ipv4, filter_ipv6
    if file_extract:
        return file_extract
    else:
        os.exit(f"Error during extracting file: {output_file} ")

if __name__ == "__main__":

    parser = argparse.ArgumentParser('CLI for Feature Extraction module of BGP Research Tool')

    #Download arguments
    parser.add_argument('--site-collection', dest='site_collection', default='ripe', choices=['ripe'], help='Choose a site collection that can be ripe or route-views (not available yet)')
    parser.add_argument('--from', dest='datetime_start', type=str, required=True, help='Choose a datetime to start download in the format: yyyymmddThhmmss. Example: 20030521T080100 ')
    parser.add_argument('--to', dest='datetime_end', type=str, required=True, help='Choose a datetime to start download in the format: yyyymmddThhmmss. Example: 20030521T080100 ')
    parser.add_argument('--rrc', dest='rrc', type=int, default=4, help='Choose a RRC')
    parser.add_argument('--max-concurrent-requests', dest='max_concurrent_requests', type=int, default=32, help='Choose a number of max concurrent requests')

    #Extraction arguments
    parser.add_argument('--output', dest='output_file', type=str, required=True, help='Choose a number of max concurrent requests')
    parser.add_argument('--day', dest='day_number', type=int, required=False, default=False, help='In case of distributed processing, choose the day number of the slice that will be processed.')
    
    args = parser.parse_args()

    datetime_start = convert_datetime(args.datetime_start)
    datetime_end = convert_datetime(args.datetime_end)

    output_file = args.output_file

    if (args.day_number):
        datetime_start, datetime_end = split_interval_per_day(datetime_start, datetime_end, args.day_number)
        print(f"The datetime_start and datetime_end were adjusted to {datetime_start} and {datetime_end}, respectively.")
        
        output_file = append_suffix_on_filename(output_file, args.day_number)
        print(f"The output_file name was adjusted to \"{output_file}\".")

    # print(datetime_start, datetime_end)
    file_extract = data_download_and_extract(args.output_file, datetime_start, datetime_end, args.rrc, args.site_collection, args.max_concurrent_requests)
    print(file_extract)