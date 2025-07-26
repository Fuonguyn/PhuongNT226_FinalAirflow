class SqlQueries:
    songplay_table_insert = ("""
    WITH songplay_data AS (
        SELECT
            md5(CAST(events.sessionid AS TEXT) || CAST(events.start_time AS TEXT)) AS playid,
            events.start_time, 
            events.userid, 
            events.level, 
            songs.song_id,
            songs.artist_id, 
            events.sessionid, 
            events.location, 
            events.useragent
        FROM (
            SELECT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' AS start_time, *
            FROM staging_events
            WHERE page='NextSong'
        ) events
        LEFT JOIN staging_songs songs
            ON events.song = songs.title
            AND events.artist = songs.artist_name
            AND events.length = songs.duration
    )
    INSERT INTO songplays (
        playid, start_time, userid, level,
        songid, artistid, sessionid, location, user_agent
    )
    SELECT * FROM songplay_data
    ON CONFLICT (playid) DO NOTHING;
    """)

    user_table_insert = ("""
    INSERT INTO users (userid, first_name, last_name, gender, level)
    SELECT DISTINCT userid, firstname AS first_name, lastname AS last_name, gender, level
    FROM staging_events
    WHERE page='NextSong'
    ON CONFLICT (userid) DO NOTHING;
""")


    song_table_insert = ("""
    INSERT INTO songs (songid, title, artistid, year, duration)
    SELECT DISTINCT song_id, title, artist_id, year, duration
    FROM staging_songs
    ON CONFLICT (songid) DO NOTHING;
""")


    artist_table_insert = ("""
    INSERT INTO artists (artistid, name, location, latitude, longitude)
    SELECT DISTINCT artist_id, artist_name, artist_location, artist_latitude, artist_longitude
    FROM staging_songs
    ON CONFLICT (artistid) DO NOTHING;
""")


    time_table_insert = ("""
    INSERT INTO time (start_time, hour, day, week, month, year, weekday)
    SELECT 
        start_time, 
        EXTRACT(hour FROM start_time), 
        EXTRACT(day FROM start_time), 
        EXTRACT(week FROM start_time), 
        EXTRACT(month FROM start_time), 
        EXTRACT(year FROM start_time), 
        EXTRACT(dow FROM start_time)
    FROM songplays
    ON CONFLICT (start_time) DO NOTHING                     
""")
