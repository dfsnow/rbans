#!/bin/bash

source config.sh

createdb "$db_name" -O "$db_user"

psql -d "$db_name" -U "$db_user" << EOD

    SET CLIENT_ENCODING TO UTF8;
    SET STANDARD_CONFORMING_STRINGS TO ON;
    BEGIN;
    DROP TABLE IF EXISTS "public"."comments";
    CREATE TABLE "public"."comments" (
        gid serial,
        "author" varchar(20),
        "subreddit" varchar(200),
        "parent_id" varchar(20),
        "id" varchar(20),
        "score" int,
        "body" varchar(50000),
        "date" date,
        PRIMARY KEY (id, date)
        ) PARTITION BY RANGE(date);
    COMMIT;

EOD
for year in $(seq 2004 2018); do
    for month in $(seq 1 12); do
        month_next=$(($month + 1))
        combined=$(date -d "0000-12-01 $year year $month months" +%Y-%m-%d)
        combined_next=$(date -d "0000-12-01 $year year $month_next months" +%Y-%m-%d)
        combined_name=$(echo $combined | tr '-' '_' | awk '{print substr($0,1,7)}')
        psql -d "$db_name" -U "$db_user" << EOD
            CREATE TABLE comments_$combined_name PARTITION OF comments
            FOR VALUES FROM ('$combined') TO ('$combined_next');
EOD
    done;
done

psql -d "$db_name" -U "$db_user" << EOD

    CREATE UNIQUE INDEX comments_id_idx ON comments (date, id);
    CREATE INDEX comments_date_subreddit_idx ON comments (date, subreddit);
    CREATE INDEX comments_subreddit ON comments (subreddit);
    CREATE INDEX comments_author_idx ON comments (author);

EOD
