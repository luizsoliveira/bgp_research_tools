import os
import sys
import pandas as pd
import matplotlib.pyplot as plot
from datetime import datetime
from datetime import timezone

src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
src_dir = f"{src_dir}/src"
sys.path.append(src_dir)

from data_download.clients.ioda_client import IODAClient

def convert_datetime(timestamp):
    date_time = datetime.fromtimestamp(timestamp)
    date_time = date_time.replace(tzinfo=timezone.utc) 
    return date_time.strftime("%m/%d/%Y, %H:%M:%S")    

client = IODAClient(debug=True)

region_code = 1226
from_timestamp = 1696259700
to_timestamp = 1700147700

title = f"Region {region_code} from {convert_datetime(from_timestamp)} to {convert_datetime(to_timestamp)}"

# df = client.get_signals_dataframe('region', region_code, from_timestamp, to_timestamp, add_datetime_column=True)
df = client.get_signals_normalized_dataframe('region', region_code, from_timestamp, to_timestamp, add_datetime_column=True)

df.to_csv(f"examples/signals_region_{region_code}.csv")

fig, ax = plot.subplots()
df.plot(x='datetime', figsize=(10,6), title=title, 
        lw=0.5, fontsize=12, ax=ax, grid=False, color={"merit-nt": "orange", "bgp": "green", "ping-slash24": "blue"})

# plot.savefig("examples/")
plot.show(block=True)


