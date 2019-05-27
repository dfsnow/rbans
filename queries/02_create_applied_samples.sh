#!/bin/bash

for i in $(seq 1 50); do
    date=$(date -d "2014-12-01 $i months" +%Y-%m-%d)
    date=$(echo $date | cut -c 1-7 | tr '-' '_')

    echo "Now sampling: $date"

    psql reddit << EOD

    \COPY (SELECT id, date, score, subreddit, body FROM comments_$date TABLESAMPLE SYSTEM_ROWS(20000000))  TO '/home/snow/rbans/data/main_applied_sample_$date.csv' WITH CSV HEADER;

EOD
done
