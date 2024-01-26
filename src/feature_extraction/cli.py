import argparse
import os
import sys

src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(src_dir)

from data_download.cli import data_download, convert_datetime
from feature_extraction.bgp_cplusplus_feature_extraction import BGPCPlusPlusFeatureExtraction

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
    
    args = parser.parse_args()

    datetime_start = convert_datetime(args.datetime_start)
    datetime_end = convert_datetime(args.datetime_end)

    file_extract = data_download_and_extract(args.output_file, datetime_start, datetime_end, args.rrc, args.site_collection, args.max_concurrent_requests)
    print(file_extract)