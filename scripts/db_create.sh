#!/bin/bash

source config.sh

#createdb "$db_name" -O "$db_user"

psql -d "$db_name" -U "$db_user" << EOD

    SET CLIENT_ENCODING TO UTF8;
    SET STANDARD_CONFORMING_STRINGS TO ON;
    BEGIN;
    DROP TABLE IF EXISTS "public"."comments";
    CREATE TABLE "public"."comments" (
        gid serial,
        "author" varchar(20),
        "subreddit" varchar(200),
        "subreddit_id" varchar(20),
        "parent_id" varchar(20),
        "id" varchar(20),
        "score" int,
        "body" varchar(50000),
        "year" smallint,
        "month" smallint
        ) PARTITION BY RANGE(year, month);
    COMMIT;

EOD

for year in $(seq 2006 2018); do
    year_next=$(echo "$(($year+1))")

    for month in $(seq 1 12); do
    month_next=$(echo "$(($month+1))")
    combined="$year"_$(printf %02g $month)

    psql -d "$db_name" -U "$db_user" << EOD
        CREATE TABLE comments_$combined PARTITION OF comments
        FOR VALUES FROM ($year, $month) TO ($year, $month_next);
EOD
    done
done

psql -d "$db_name" -U "$db_user" -c "CREATE INDEX ON comments (year, month);"
