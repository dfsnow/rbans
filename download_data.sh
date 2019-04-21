#!/bin/sh

EXT=bz2

for year in $(seq 2014 2017); do
    for month in $(seq -f "%02g" 1 12); do
        echo "Now downloading "$year"-"$month" file"
        wget https://files.pushshift.io/reddit/comments/RC_"$year"-"$month"."$EXT" -P /data
        pv /data/RC_"$year"-"$month"."$EXT" \
            | pbzip2 -c -d \
            > /data/RC_"$year"-"$month".json
        rm /data/RC_"$year"-"$month"."$EXT"
    done
done
