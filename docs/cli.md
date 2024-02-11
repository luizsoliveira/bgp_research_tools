The Command Line Interface (CLI) provided in this repository offers the following modules:

[Dataset creation](#dataset-creation)
* [Data Download](#data-downloading)
* [Feature Extraction](#feature-extraction)
* Data merging
* Data labeling

Exploratory data analysis and Feature selection
* Exploratory data analysis
* Feature selection
  
Model Training
* Data normalization
* Data partition
* Batch model training
* Performance evaluation

# Dataset creation

## Data downloading

#### Choosing site collection, RRC, and time interval
```console
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20230102T235959 
```
* Download MRT BGP files from RIPE RIS RRC04 from 2023-01-01T00:00:00 to 2024-01-28T23:59:59.
* A list with the path of the downloaded files will be printed at stdout.
* The files will be downloaded in a temporary folder provided by the operational system.

#### Choosing a cache location
```console
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20230102T235959 \
--mrt-cache-directory ~/cache
```
* Uses the path `~/cache` to store the downloaded files.
* The same directory is also used as a cache source that allows avoid downloading repeated files. 

#### Choosing the max number of concurrent requests

```console
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20230102T235959 \
--mrt-cache-directory ~/cache
--max-concurrent-requests 32
```
* Specify that the connection pool will use a maximum number of 32 concurrent HTTP requests at the same time.

### Data downloading using distributed processing
This CLI offers valuable resources when distributing the data download into several nodes. In this way, it is possible to specify that each node will download a chunk of the total period requested. This chunk corresponds to some interval of hours. The default value is 24 hours.

#### Specifying a chunk number
```console
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20240128T235959 \
--mrt-cache-directory ~/cache \
--chunk 1
```
* In the example above, the data download will execute only chunk number 1 of a total of 393 chunks.
* Passing `--chunk 1` returns: "The datetime_start and datetime_end were adjusted to 2023-01-01 00:00:00 and 2023-01-01 23:59:59, respectively. Considering chunk_number=1 and chunk_duration_hours=24."
* Passing `--chunk 2` returns: "The datetime_start and datetime_end were adjusted to 2023-01-02 00:00:00 and 2023-01-02 23:59:59, respectively. Considering chunk_number=2 and chunk_duration_hours=24."
* A useful resource is to pass `--chunk 0` to force the CLI to return an error message that displays the range of chunk numbers that is valid: "ABORTING: For the datetime interval provided the chunk_number must be between 1 and 393. Instead, 0 was provided."

#### Specifying the chunk duration

```console
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20240128T235959 \
--mrt-cache-directory ~/cache \
--chunk 1 \
--chunk-duration-hours 4
```
* Passing `--chunk 1` returns: "The datetime_start and datetime_end were adjusted to 2023-01-01 00:00:00 and 2023-01-01 03:59:59, respectively. Considering chunk_number=1 and chunk_duration_hours=4."
* Passing `--chunk 0` returns: "ABORTING: For the datetime interval provided the chunk_number must be between 1 and 2358. Instead, 0 was provided."

Additional information is available through --help switch.
```console
python src/data_download/cli.py --help                                                
```

## Feature extraction

Feature extraction is a step done after data downloading or during the download when using pipelining.

To make it easy to use this CLI, the data download step was totally integrated with the feature extraction step. This means that the users can execute commands for feature extraction, and the CLI will automatically and transparently take care of the data downloading.

This CLI runs the MRTprocessor in the background, which has to be installed to perform feature extraction.

#### Extracting features from a specific site collection, RRC, and time interval
```console
python src/feature_extraction/cli.py --rrc 0 \
--from 20230101T000000 --to 20230102T235959 \
--mrt-cache-directory ~/cache \
--output ~/datasets/dataset.csv
```
* In the example above, the feature extraction will be performed by downloading MRT files or getting them from the cache when available.
* The MRTprocessor will be called passing parameter a list of files according to the parameters `--rrc`, `--from`, and `--to`.
* The matrix having the 37 features and one line for each 1-minute interval will be saved at `~/datasets/dataset.csv`.

### Feature extraction using distributed processing

#### Specifying a chunk number
```console
python src/feature_extraction/cli.py --rrc 4 \
--from 20230101T000000 --to 20240128T235959 \
--mrt-cache-directory ~/cache \
--chunk 1 \
--output ~/datasets/dataset.csv
```

#### Specifying the chunk duration
```console
python src/feature_extraction/cli.py --rrc 4 \
--from 20230101T000000 --to 20240128T235959 \
--mrt-cache-directory ~/cache \
--chunk 1 \
--chunk-duration-hour 4 \
--output ~/datasets/dataset.csv
```

Additional information available through --help switch.
```console
python src/feature_extraction/cli.py --help                                                
```