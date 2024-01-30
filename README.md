# BGP Research Tools

A toolkit to help researchers work with BGP data, providing a CLI, clients, parsers, and other tools.

* CLI;
* RIPE Client;
* Integration with MRT parsers;      

## Instaling

```bash
git clone https://github.com/luizsoliveira/bgp_research_tools
cd bgp_research_tools
apt -y install python3-pip
python3 -m pip install -r src/requirements.txt
```

## Instaling on HPC (CEDAR)

```bash
# Downloading python code
git clone https://github.com/luizsoliveira/bgp_research_tools
cd bgp_research_tools
# Loading modules python3.10 and scipy-stack
module load python/3.10
module load scipy-stack
# Creating a virtual environment on the folder ENV
virtualenv --no-download ENV
# Activating the virtual environment created
source ENV/bin/activate
# Updating pip in the environment
pip install --no-index --upgrade pip
# Installing the required python packages, 
python3.10 -m pip install -r src/requirements.txt --no-index
# The --no-index option tells pip to not install from PyPI, but instead to install only from locally available packages, i.e. CEDAR wheels.
```

## RIPE Client

Client to facilitate downloading MRT files from the RIPE repository.

### Usage

#### Simple usage without cache, logging, and debug

```python
client = RIPEClient()
# Example datetime range
files = client.download_updates_interval_files(datetime(2022, 12, 25, 10, 0), datetime(2022, 12, 25, 11, 37))

# The files are immediately returned as they are being downloaded
for file in files:
    print(file)
```

**Expected output:**

```bash
(...)/ripe/rrc04/2022.12/updates.20221225.1000.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1005.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1010.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1015.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1020.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1025.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1030.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1035.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1040.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1045.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1050.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1055.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1100.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1105.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1110.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1115.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1120.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1125.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1130.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1135.gz
```

#### Passing a cache location

```python
client = RIPEClient(cacheLocation='./cache/ripe')
# Returns a array with the location of the downloaded files respecting the datetime range
files = client.download_updates_interval_files(datetime(2022, 12, 25, 10, 0), datetime(2022, 12, 25, 11, 37))

# The files are immediately returned as they are being downloaded
for file in files:
    print(file)
```

Passing a cache location, the client will check the previous existence of the file before doing the download.
When the file is found in the cache, the client will return the cached file.
When a cache location is not provided, the client will choose a temp directory and will use this for cache purposes.

#### Passing a logging object

```python
#LOGGING configuration
logging.basicConfig(
    filename='ripe.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


client = RIPEClient(logging=logging, cacheLocation='./cache/ripe')
# Returns a array with the location of the downloaded files respecting the datetime range
files = client.download_updates_interval_files(datetime(2022, 12, 25, 10, 0), datetime(2022, 12, 25, 11, 37))

# The files are immediately returned as they are being downloaded
for file in files:
    print(file)
```

In this way, some messages will be written in the log file in according to the log object configuration.

#### Enabling debug messages

```python
client = RIPEClient(debug=True)
# Returns a array with the location of the downloaded files respecting the datetime range
files = client.download_updates_interval_files(datetime(2022, 12, 25, 10, 0), datetime(2022, 12, 25, 11, 37))

# The files are immediately returned as they are being downloaded
for file in files:
    print(file)
```

With debug=True some messages will be printed on the screen during the client downloading proccess. 

## Useful information about BGP anomaly events

### Slammer
* Beginning of the event: 25.01.2003 at 5:31 GMT
* End of the event: 25.01.2003 at 19:59 GMT

### Nimda
* Beginning of the event: 18.09.2001 at 13:19 GMT 
* End of the event: 20.09.2001 at 23:59 GMT 

### Code Red I
* Beginning of the event: 19.07.2001 at 13:20 GMT
* End of the event: 19.07.2001 at 23:19 GMT

### Moscow Blackout:
* Beginning of the event: 25.05.2005 at 04:00 GMT
* End of the event: 25.05.2005 at 07:59 GMT

### Pakistan Power Outage:
* Beginning of the event: 09.01.2005 at 18:40 GMT
* End of the event: 09.01.2005 at 23:59 GMT

### WannaCrypt Ransomware Attack

* Beginning of the event: 
* End of the event: 

### WestRock Ransomware Attack
* Beginning of the event: 23.01.2021 at 1:12 GMT
* End of the event: 29.01 2021 at 23:59 GMT








