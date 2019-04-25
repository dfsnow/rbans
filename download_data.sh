#!/bin/sh

data_dir=/data/reddit
source config.sh

# Downloading from offsite server with torrent of data
#for year in $(seq 2005 2017); do
    #for month in $(seq -f "%02g" 1 12); do
        #if [ ! -f "$data_dir"/RC_"$year"-"$month" ]; then
            #sshpass -p "$scp_pass" \
                #rsync -r -v --progress -e ssh \
                #grime@crios.bysh.me:~/torrents/data/reddit_data/"$year"/RC_"$year"-"$month".bz2 \
                #"$data_dir"/RC_"$year"-"$month"
        #fi
    #done
#done

## Downloading missing files from pushshift.io
#for year in $(seq 2018); do
    #for month in $(seq -f "%02g" 1 12); do
        #if [ ! -f "$data_dir"/RC_"$year"-"$month".xz ]; then
            #wget https://files.pushshift.io/reddit/comments/RC_"$year"-"$month".xz -P "$data_dir"
        #fi
    #done
#done

# Downloading missing files from pushshift.io
for year in $(seq 2018 2019); do
    for month in $(seq -f "%02g" 1 12); do
        if [ ! -f "$data_dir"/RC_"$year"-"$month".xz ]; then
            wget https://files.pushshift.io/reddit/comments/RC_"$year"-"$month".zst -P "$data_dir"
        fi
    done
done

