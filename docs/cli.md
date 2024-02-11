The Command Line Interface (CLI) provided in this repository offer the following modules:

Dataset creation
* Data Download
* Feature Extraction
* Data merging
* Data labeling

Exploratory data analysis and Feature selecting
* Exploratory data analysis
* Feature selection
  
Model Trainning
* Data normalization
* Data partition
* Batch model training
* Performance evaluation

# Dataset creation

## Data downloading

#### Choosing site collection, RRC and time interval
  
```bash
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20230102T235959 
```
* Download MRT BGP files from RIPE RIS RRC04 from 2023-01-01T00:00:00 to 2024-01-28T23:59:59.
* A list with the path of the downloaded files will be printed at stdout.
* The files will be download in a temporary folder provided by the operational system.

#### Choosing a cache location

```bash
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20230102T235959 \
--mrt-cache-directory ~/cache
```
* Uses the path `~/cache` to store the downloaded files.
* The same directory is also used as a cache source that allows avoid to download repeated files. 

#### Choosing the max number of concurrent requests

```bash
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20230102T235959 \
--mrt-cache-directory ~/cache
--max-concurrent-requests 32
```
* Specify that the connection pool will use a maximum number of 32 concurrent HTTP requests at the same time.

### Data downloading using distributed processing
This CLI offer resources valuable when distributing the data download into several nodes. In this way is possible to specify that each node will do the download a chunk of the total period requested.

#### Specifying a chunk number
```bash
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20240128T235959 \
--mrt-cache-directory ~/cache \
--chunk 1
```
* In the example above, the data download will execute only the chunk number 1 of a total of 393 chunks.
* Passing `--chunk 1` returns: "The datetime_start and datetime_end were adjusted to 2023-01-01 00:00:00 and 2023-01-01 23:59:59, respectively. Considering chunk_number=1 and chunk_duration_hours=24."
* Passing `--chunk 2` returns: "The datetime_start and datetime_end were adjusted to 2023-01-02 00:00:00 and 2023-01-02 23:59:59, respectively. Considering chunk_number=2 and chunk_duration_hours=24."
* An useful resource is to pass `--chunk 0` just to force the CLI return a error message that display the range of chunk numbers that is valid: "ABORTING: For the datetime interval provided the chunk_number must be between 1 and 393. Instead, 0 was provided."

#### Specifying the chunk duration

```bash
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20240128T235959 \
--mrt-cache-directory ~/cache \
--chunk 1 \
--chunk-duration-hours 4
```
* Passing `--chunk 1` returns: "The datetime_start and datetime_end were adjusted to 2023-01-01 00:00:00 and 2023-01-01 03:59:59, respectively. Considering chunk_number=1 and chunk_duration_hours=4."
* Passing `--chunk 0` returns: "ABORTING: For the datetime interval provided the chunk_number must be between 1 and 2358. Instead, 0 was provided."

Additional information available through --help switch.
```bash
python src/data_download/cli.py --help                                                
```

## Feature extraction

Feature extraction is a step done after data downloading or during the download when using pipelining.

To turn easy the use of this CLI, the data download step was totally integrated with the feature extraction step. This means that the users can execute command for feature extraction and the CLI will automatically and transparently take care about the data downloading.

This CLI run the MRTprocessor in background, which have to be installed to perform feature extraction.

#### Extracting features from a specific site collection, RRC and time interval
```bash
python src/feature_extraction/cli.py --rrc 0 \
--from 20230101T000000 --to 20230102T235959 \
--mrt-cache-directory ~/cache \
--output ~/datasets/dataset.csv
```
* In the example above the feature extraction will be performed downloading MRT files, or getting them from cache when available.
* The MRTprocessor will be called passing parameter a list of files according with the parameters `--rrc`, `--from` and `--to`.
* The matrix having the 37 features and one line for each 1-minute interval will be saved at ``


### Feature extraction using distributed processing

#### Specifying a chunk number
```bash
python src/feature_extraction/cli.py --rrc 4 \
--from 20230101T000000 --to 20240128T235959 \
--mrt-cache-directory ~/cache \
--chunk 1 \
--output ~/datasets/dataset.csv
```

#### Specifying the chunk duration
```bash
python src/feature_extraction/cli.py --rrc 4 \
--from 20230101T000000 --to 20240128T235959 \
--mrt-cache-directory ~/cache \
--chunk 1 \
--chunk-duration-hour 4 \
--output ~/datasets/dataset.csv
```

Additional information available through --help switch.
```bash
python src/feature_extraction/cli.py --help                                                
```