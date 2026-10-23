# Spotify Data Explorer

An end-to-end Spotify data engineering project that extracts playlist data from the Spotify API, stores raw data in Amazon S3, transforms it with AWS Lambda, loads curated song, album, and artist records into Snowflake, and provides a local Streamlit dashboard for exploration.

## Dashboard Preview

The dashboard keeps Streamlit's dark appearance and focuses on browsing the data produced by the pipeline.

### Overview
![Spotify Data Explorer overview](docs/images/overview.png)

The overview displays distinct song, album, and artist counts, followed by recently added song records.

### Songs Explorer
![Songs Explorer](docs/images/songs-explorer.png)

Search song records by name and inspect their IDs, timestamps, album and artist references, and Spotify URLs.

### Albums
![Album collection](docs/images/albums.png)

Browse album metadata, including release date, track count, and Spotify URL.

### Artists
![Artist directory](docs/images/artists.png)

Browse artist IDs, names, and external Spotify API URLs.

### Analytics
![Artist analytics](docs/images/analytics.png)

A Snowflake aggregation identifies the top artists by distinct song count and displays the results as a bar chart and table.

## Architecture

```text
Spotify Web API
      |
      v
Python + Spotipy
(Spotify OAuth / playlist items)
      |
      v
Amazon S3 — raw_data/to_processed/
      |
      v
AWS Lambda — transformation
      |
      +------------------+------------------+
      |                  |                  |
      v                  v                  v
song_data/*.csv     album_data/*.csv   artist_data/*.csv
      \                  |                  /
       \                 |                 /
        +------ Amazon S3 transformed_data/+
                           |
                           v
                  Snowflake stage and tables
                  SPOTIFY_DB.PUBLIC
                           |
                           v
                 Streamlit Data Explorer
```

**Snowpipe note:** Snowpipe auto-ingestion was configured and tested during development. The pipe was later dropped during cleanup, so this README does not describe Snowpipe as currently active. The existing S3-to-Lambda notification was preserved.

## AWS and Snowflake components

- **Spotify API / Spotipy** — retrieves playlist item data.
- **Amazon S3** — stores raw JSON and transformed CSV outputs.
- **AWS Lambda** — extracts song, album, and artist fields and writes CSV files to S3.
- **Amazon S3 event notification** — triggers the transformation Lambda when a JSON object is created under `raw_data/to_processed/`.
- **Snowflake** — stores and queries the transformed data.
- **Streamlit** — provides the local dashboard.
- **Pandas** — structures transformed records and prepares dashboard tables.

## S3 layout

```text
spotify-etl-project-gaurav-ambasta/
├── raw_data/
│   ├── to_processed/
│   └── processed/
└── transformed_data/
    ├── song_data/
    ├── album_data/
    └── artist_data/
```

The extraction function writes the Spotify response as JSON to `raw_data/to_processed/`. The transformation function reads JSON files from that prefix, creates CSV outputs for songs, albums, and artists, copies processed JSON files to `raw_data/processed/`, and removes the originals from `raw_data/to_processed/`.

## Transformation logic

The Lambda transformation code builds three datasets:

- **Songs:** song ID, name, duration in milliseconds, Spotify URL, added timestamp, album ID, and the first artist ID.
- **Albums:** album ID, name, release date, total tracks, and Spotify URL.
- **Artists:** artist ID, name, and external URL.

Pandas DataFrames are used to create CSV outputs in the `transformed_data/` prefixes. Duplicate album IDs and artist IDs are dropped within each processed dataset. Song records are not deduplicated by the transformation function.

The extraction code requests up to 50 playlist items with `limit=50` and `offset=0`; it currently retrieves a single page rather than paginating through the whole playlist.

## Snowflake data model

The dashboard queries these tables in `SPOTIFY_DB.PUBLIC`:

| Table | Purpose | Main fields used |
|---|---|---|
| `TBLSONGS` | Song records | `SONG_ID`, `SONG_NAME`, `DURATION_MS`, `URL`, `SONG_ADDED`, `ALBUM_ID`, `ARTIST_ID` |
| `TBLALBUM` | Album metadata | `ALBUM_ID`, `ALBUM_NAME`, `RELEASE_DATE`, `TOTAL_TRACKS`, `URL` |
| `TBLARTIST` | Artist metadata | `ARTIST_ID`, `ARTIST_NAME`, `EXTERNAL_URL` |

The S3 stage and CSV file format were configured in Snowflake to read the transformed files. During development, `COPY INTO` loaded album and artist records, and Snowpipe was tested for automatic song ingestion.

## Verified results

The dashboard screenshot captured during verification displayed:

| Metric | Value |
|---|---:|
| Distinct songs | 50 |
| Albums | 47 |
| Artists | 71 |
| Song rows shown on the Songs page | 100 |

The song metric uses `COUNT(DISTINCT SONG_ID)`, while the Songs page displays table rows. Therefore, the row count can be higher than the distinct song count when duplicate song IDs exist.

## Dashboard features

- **Overview** — distinct song, album, and artist metrics plus the 10 most recently added song records.
- **Songs** — search by song name and inspect song metadata.
- **Albums** — browse album details.
- **Artists** — browse artist records.
- **Analytics** — join songs to artists, count distinct songs per artist, and display the top 10 results.

The dashboard uses the existing Streamlit layout and theme. Snowflake queries perform filtering and aggregation, and Pandas formats the returned records for display.

## Run locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
```

Replace the placeholders with your repository URL and project directory.

### 2. Create and activate a virtual environment

On macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install streamlit pandas snowflake-connector-python
```

The extraction and transformation code also use `spotipy` and `boto3`; install those in the environment used to run those components:

```bash
python -m pip install spotipy boto3
```

### 4. Configure access

The local dashboard uses Snowflake's browser-based OAuth authorization-code flow. Update the connection settings in `app.py` to match your Snowflake account and user if you are adapting the project to another account.

Do not commit AWS access keys, Spotify client secrets, refresh tokens, OAuth tokens, or other credentials. For AWS Lambda, configure the Spotify values as Lambda environment variables and use an IAM execution role with only the S3 permissions required by the function.

### 5. Start the dashboard

```bash
streamlit run app.py
```

Streamlit normally opens the local dashboard at `http://localhost:8501`.

## Cost and cleanup

This project was built using AWS and Snowflake learning/free-trial resources. Service usage can incur charges depending on account terms and usage. The dashboard is designed to run locally and does not require hosting on AWS.

Suspend the Snowflake warehouse when not using it, and review S3 objects, Lambda activity, notifications, and Snowflake resources before leaving the project idle. The Snowflake warehouse used during development was `SPOTIFY_WH`.

## Limitations and possible improvements

- The extraction currently requests only the first 50 playlist items; pagination could be added.
- Song duplicates can appear when the same data is loaded more than once. A future improvement would add a deduplication or merge strategy keyed by `SONG_ID`.
- Snowpipe was tested but dropped during cleanup; it can be recreated if ongoing automatic ingestion is needed.
- The dashboard currently runs locally and uses simple top-artist analytics.

## Skills demonstrated

`Python` · `SQL` · `AWS Lambda` · `Amazon S3` · `Boto3` · `Spotipy` · `Pandas` · `Snowflake` · `ETL` · `Streamlit` · `Data Modeling` · `Data Visualization`

---

**Project:** Spotify Data Explorer  
**Dashboard:** Streamlit  
**Warehouse:** Snowflake
