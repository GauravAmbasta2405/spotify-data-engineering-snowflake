# 🎧 Spotify Data Explorer

An end-to-end data engineering project that transforms Spotify playlist data into structured datasets and an interactive analytics dashboard using **Python, AWS, Snowflake, and Streamlit**.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Spotify_API-1DB954?style=for-the-badge&logo=spotify&logoColor=white" alt="Spotify API" />
  <img src="https://img.shields.io/badge/Amazon_S3-569A31?style=for-the-badge&logo=amazons3&logoColor=white" alt="Amazon S3" />
  <img src="https://img.shields.io/badge/AWS_Lambda-FF9900?style=for-the-badge&logo=awslambda&logoColor=white" alt="AWS Lambda" />
  <img src="https://img.shields.io/badge/Snowflake-29B5E8?style=for-the-badge&logo=snowflake&logoColor=white" alt="Snowflake" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
</p>

## 📌 Overview

Spotify Data Explorer automates the journey from playlist extraction to data analysis. Spotify API data is collected using Python, stored in Amazon S3, transformed into structured CSV datasets using AWS Lambda, and loaded into Snowflake for querying and visualization.

The Streamlit dashboard provides an interactive interface to explore songs, albums, artists, and artist-level analytics.

## 🖥️ Dashboard

### Overview

Displays distinct song, album, and artist counts alongside recently added song records.

![Dashboard Overview](images/overview.png)

### Songs Explorer

Search song records by name and explore song metadata, timestamps, album and artist references, and Spotify links.

![Songs Explorer](images/songs-explorer.png)

### Album Collection

Explore album names, release dates, track counts, and Spotify URLs.

![Album Collection](images/albums.png)

### Artist Directory

Browse artist records, identifiers, and external Spotify URLs.

![Artist Directory](images/artists.png)

### Artist Analytics

Compare artists by the number of distinct songs associated with their IDs, using a bar chart and a Top 10 table.

![Artist Analytics](images/analytics.png)

## 🏗️ Architecture

```mermaid
flowchart TD
    A["Spotify Web API"] --> B["Python + Spotipy<br/>OAuth Authentication"]
    B --> C[("Amazon S3<br/>Raw JSON")]
    C --> D["AWS Lambda<br/>Transformation"]
    D --> E[("S3: Song CSVs")]
    D --> F[("S3: Album CSVs")]
    D --> G[("S3: Artist CSVs")]
    E --> H["Snowflake Stage"]
    F --> H
    G --> H
    H --> I[("Snowflake Tables<br/>SPOTIFY_DB.PUBLIC")]
    I --> J["Streamlit Dashboard"]

    classDef source fill:#1DB954,stroke:#168A40,color:#fff
    classDef aws fill:#FF9900,stroke:#C77700,color:#111
    classDef warehouse fill:#29B5E8,stroke:#1686B0,color:#071A22
    classDef dashboard fill:#FF4B4B,stroke:#C52F2F,color:#fff

    class A source
    class B,C,D,E,F,G aws
    class H,I warehouse
    class J dashboard
```

## ⚙️ Data Pipeline

1. **Data Extraction:** Python and Spotipy authenticate with Spotify and retrieve playlist items.
2. **Raw Data Storage:** The Spotify API response is stored as JSON in Amazon S3 under `raw_data/to_processed/`.
3. **Event-Driven Processing:** An S3 object-created notification invokes AWS Lambda when a JSON file is uploaded.
4. **Data Transformation:** Lambda uses Python and Pandas to extract song, album, and artist attributes and structure them into separate datasets.
5. **Curated Data Storage:** Transformed CSV files are written to dedicated S3 prefixes for songs, albums, and artists.
6. **Data Loading:** Snowflake stages and CSV file formats support loading the transformed datasets into relational tables. `COPY INTO` and Snowpipe auto-ingestion were tested during development.
7. **Analytics and Visualization:** Streamlit queries Snowflake to display summary metrics, searchable records, and artist analytics.

## ☁️ AWS S3 Data Layout

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

The transformation Lambda processes JSON files from `raw_data/to_processed/`, writes transformed CSV files to the corresponding prefixes, copies processed JSON files to `raw_data/processed/`, and deletes the original raw objects.

## ❄️ Snowflake Data Model

**Database:** `SPOTIFY_DB`  
**Schema:** `PUBLIC`

| Table       | Description     | Key Columns                                                                         |
| ----------- | --------------- | ----------------------------------------------------------------------------------- |
| `TBLSONGS`  | Song-level data | `SONG_ID`, `SONG_NAME`, `DURATION_MS`, `URL`, `SONG_ADDED`, `ALBUM_ID`, `ARTIST_ID` |
| `TBLALBUM`  | Album metadata  | `ALBUM_ID`, `ALBUM_NAME`, `RELEASE_DATE`, `TOTAL_TRACKS`, `URL`                     |
| `TBLARTIST` | Artist metadata | `ARTIST_ID`, `ARTIST_NAME`, `EXTERNAL_URL`                                          |

The dashboard queries these tables to retrieve records, calculate distinct counts, join song and artist data, and aggregate songs by artist.

## 📊 Verified Results

| Metric              | Result |
| ------------------- | -----: |
| Distinct Songs      |     50 |
| Albums              |     47 |
| Artists             |     71 |
| Song Rows Displayed |    100 |

The Overview displays the number of distinct song IDs, while the Songs page displays table rows. These metrics differ because the song table can contain repeated song IDs.

## ✨ Key Features

- Automated Spotify playlist extraction using Python and Spotipy.
- Event-driven serverless transformation with AWS Lambda.
- Raw JSON and curated CSV storage in Amazon S3.
- Snowflake staging, table loading, and SQL-based analytics.
- Interactive song search and album and artist browsing.
- Artist-level aggregation with a bar chart and Top 10 ranking table.
- Browser-based Snowflake OAuth authentication for the local dashboard.

## 🧰 Technology Stack

| Category             | Technologies                                    |
| -------------------- | ----------------------------------------------- |
| Programming          | Python                                          |
| Data Source          | Spotify Web API, Spotipy                        |
| Cloud Storage        | Amazon S3                                       |
| Serverless Computing | AWS Lambda                                      |
| Data Processing      | Pandas                                          |
| Data Warehouse       | Snowflake                                       |
| Data Loading         | Snowflake Stage, `COPY INTO`, Snowpipe (tested) |
| Dashboard            | Streamlit                                       |
| Query Language       | SQL                                             |

## 📁 Repository Structure

```text
.
├── images/
│   ├── overview.png
│   ├── songs-explorer.png
│   ├── albums.png
│   ├── artists.png
│   └── analytics.png
├── app.py
├── data_extraction.py
├── data_transformation_load.py
├── Spotify Data Pipeline.ipynb
└── README.md
```

## 🚀 Run the Dashboard Locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
```

Replace the placeholders with your repository URL and project directory.

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install streamlit pandas snowflake-connector-python
```

For the extraction and transformation scripts, install:

```bash
python -m pip install spotipy boto3
```

### 4. Configure Snowflake authentication

Configure the Snowflake account and browser-based OAuth authentication settings in `app.py` for your environment.

Keep Spotify client secrets, refresh tokens, AWS credentials, and other sensitive values out of source control. Use environment variables and appropriate IAM permissions for AWS components.

### 5. Launch Streamlit

```bash
streamlit run app.py
```

The dashboard will typically be available at `http://localhost:8501`.

---

<p align="center">
  <strong>Spotify Data Explorer</strong><br/>
  Python · AWS · Snowflake · Streamlit
</p>
