
import streamlit as st
import pandas as pd
import snowflake.connector


# --------------------------------------------------
# 1. Dashboard setup
# --------------------------------------------------
# Keep the layout wide so tables and analytics are easy to explore.
st.set_page_config(
    page_title="Spotify Data Explorer",
    page_icon="🎧",
    layout="wide",
)

st.title("🎧 Spotify Data Explorer")
st.caption(
    "From Spotify API data to an interactive analytics layer — "
    "powered by AWS, Snowflake and Streamlit."
)

st.markdown(
    """
    This dashboard explores the data produced by my Spotify ETL pipeline.
    Transformed song, album and artist records are stored in Snowflake
    and queried here for exploration and analysis.
    """
)


# --------------------------------------------------
# 2. Snowflake connection
# --------------------------------------------------
# OAuth lets me use my existing Snowflake browser login instead of
# storing a password in the application.
@st.cache_resource
def get_snowflake_connection():
    return snowflake.connector.connect(
        account="GO74315.ap-southeast-7.aws",
        user="gauravambasta1999",
        authenticator="OAUTH_AUTHORIZATION_CODE",
        warehouse="SPOTIFY_WH",
        database="SPOTIFY_DB",
        schema="PUBLIC",
        role="SNOWFLAKE_LEARNING_ROLE",
    )


# --------------------------------------------------
# 3. Reusable query helper
# --------------------------------------------------
def fetch_data(sql, params=None):
    """
    Execute a SELECT query and return the result as a DataFrame.

    Parameters are passed separately from the SQL so user input
    can be safely used in filters without string-building SQL.
    """
    connection = get_snowflake_connection()

    with connection.cursor() as cursor:
        cursor.execute(sql, params or ())
        records = cursor.fetchall()

        # Preserve the column names returned by Snowflake.
        columns = [column[0] for column in cursor.description]

    return pd.DataFrame(records, columns=columns)


# --------------------------------------------------
# 4. Load dashboard summary
# --------------------------------------------------
# One query gives us the three headline metrics for the overview.
SUMMARY_SQL = """
    SELECT
        (SELECT COUNT(DISTINCT SONG_ID)
         FROM SPOTIFY_DB.PUBLIC.TBLSONGS) AS TOTAL_SONGS,

        (SELECT COUNT(DISTINCT ALBUM_ID)
         FROM SPOTIFY_DB.PUBLIC.TBLALBUM) AS TOTAL_ALBUMS,

        (SELECT COUNT(DISTINCT ARTIST_ID)
         FROM SPOTIFY_DB.PUBLIC.TBLARTIST) AS TOTAL_ARTISTS
"""


# --------------------------------------------------
# 5. Sidebar navigation
# --------------------------------------------------
page = st.sidebar.radio(
    "Explore your data",
    [
        "Overview",
        "Songs",
        "Albums",
        "Artists",
        "Analytics",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Data source: Snowflake")
st.sidebar.caption("Database: SPOTIFY_DB")
st.sidebar.caption("Schema: PUBLIC")


# --------------------------------------------------
# 6. Dashboard pages
# --------------------------------------------------
try:
    summary = fetch_data(SUMMARY_SQL).iloc[0]

    if page == "Overview":
        st.subheader("Pipeline at a glance")

        metric_1, metric_2, metric_3 = st.columns(3)

        metric_1.metric(
            "🎵 Songs",
            f"{int(summary['TOTAL_SONGS']):,}",
        )
        metric_2.metric(
            "💿 Albums",
            f"{int(summary['TOTAL_ALBUMS']):,}",
        )
        metric_3.metric(
            "🎤 Artists",
            f"{int(summary['TOTAL_ARTISTS']):,}",
        )

        st.divider()
        st.subheader("Recently added songs")

        recent_songs = fetch_data("""
            SELECT
                SONG_NAME,
                SONG_ADDED,
                DURATION_MS,
                ALBUM_ID,
                ARTIST_ID
            FROM SPOTIFY_DB.PUBLIC.TBLSONGS
            ORDER BY SONG_ADDED DESC NULLS LAST
            LIMIT 10
        """)

        # Convert milliseconds into minutes for easier reading.
        if not recent_songs.empty:
            recent_songs["DURATION_MIN"] = (
                recent_songs["DURATION_MS"] / 60000
            ).round(2)

            recent_songs = recent_songs.drop(
                columns=["DURATION_MS"]
            )

        st.dataframe(
            recent_songs,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Counts use distinct IDs. The recent-songs table shows "
            "up to 10 records from the source table."
        )

    elif page == "Songs":
        st.subheader("Song explorer")
        st.write("Search the loaded song records by name.")

        search_text = st.text_input(
            "Song name",
            placeholder="Start typing a song name...",
        )

        # The wildcard search is parameterized rather than inserted
        # directly into the SQL statement.
        if search_text.strip():
            songs = fetch_data("""
                SELECT
                    SONG_ID,
                    SONG_NAME,
                    DURATION_MS,
                    SONG_ADDED,
                    ALBUM_ID,
                    ARTIST_ID,
                    URL
                FROM SPOTIFY_DB.PUBLIC.TBLSONGS
                WHERE SONG_NAME ILIKE %s
                ORDER BY SONG_NAME
                LIMIT 500
            """, (f"%{search_text.strip()}%",))
        else:
            songs = fetch_data("""
                SELECT
                    SONG_ID,
                    SONG_NAME,
                    DURATION_MS,
                    SONG_ADDED,
                    ALBUM_ID,
                    ARTIST_ID,
                    URL
                FROM SPOTIFY_DB.PUBLIC.TBLSONGS
                ORDER BY SONG_NAME
                LIMIT 100
            """)

        if not songs.empty:
            songs["DURATION_MIN"] = (
                songs["DURATION_MS"] / 60000
            ).round(2)
            songs = songs.drop(columns=["DURATION_MS"])

        st.caption(f"{len(songs):,} records displayed")
        st.dataframe(
            songs,
            use_container_width=True,
            hide_index=True,
        )

    elif page == "Albums":
        st.subheader("Album collection")

        albums = fetch_data("""
            SELECT
                ALBUM_ID,
                ALBUM_NAME,
                RELEASE_DATE,
                TOTAL_TRACKS,
                URL
            FROM SPOTIFY_DB.PUBLIC.TBLALBUM
            ORDER BY ALBUM_NAME
            LIMIT 500
        """)

        st.caption(f"{len(albums):,} records displayed")
        st.dataframe(
            albums,
            use_container_width=True,
            hide_index=True,
        )

    elif page == "Artists":
        st.subheader("Artist directory")

        artists = fetch_data("""
            SELECT
                ARTIST_ID,
                ARTIST_NAME,
                EXTERNAL_URL
            FROM SPOTIFY_DB.PUBLIC.TBLARTIST
            ORDER BY ARTIST_NAME
            LIMIT 500
        """)

        st.caption(f"{len(artists):,} records displayed")
        st.dataframe(
            artists,
            use_container_width=True,
            hide_index=True,
        )

    elif page == "Analytics":
        st.subheader("Artist analytics")
        st.write(
            "Compare artists by the number of distinct songs "
            "associated with their IDs."
        )

        # Aggregate in Snowflake so we only transfer the top results
        # to the local dashboard.
        artist_stats = fetch_data("""
            SELECT
                a.ARTIST_NAME,
                COUNT(DISTINCT s.SONG_ID) AS SONG_COUNT
            FROM SPOTIFY_DB.PUBLIC.TBLSONGS s
            INNER JOIN SPOTIFY_DB.PUBLIC.TBLARTIST a
                ON s.ARTIST_ID = a.ARTIST_ID
            GROUP BY a.ARTIST_NAME
            ORDER BY SONG_COUNT DESC, a.ARTIST_NAME
            LIMIT 10
        """)

        if artist_stats.empty:
            st.info(
                "No matching song and artist records were found."
            )
        else:
            chart_data = artist_stats.set_index("ARTIST_NAME")

            st.bar_chart(chart_data["SONG_COUNT"])

            st.subheader("Top 10 artists")
            st.dataframe(
                artist_stats,
                use_container_width=True,
                hide_index=True,
            )

except Exception as error:
    # Keep technical details visible during development so database,
    # permissions and connection problems can be diagnosed.
    st.error("The dashboard could not load data from Snowflake.")
    st.code(str(error))

    st.info(
        "Check your Snowflake login, warehouse status, table names "
        "and role permissions. If the OAuth session has expired, "
        "restart the app and authenticate again if prompted."
    )
