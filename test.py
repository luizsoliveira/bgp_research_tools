from ripe_client import RIPEClient


client = RIPEClient(cacheLocation='./cache/ripe')

#client.download_update_file(2023, 9, 14, 10,50)

client.download_updates_interval_files(2023, 9, 14, 10,51, 2023, 9, 14, 11,16)
