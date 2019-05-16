
source scripts/config.sh

for file in $(ls -d "$data_dir"/*.json); do

    echo "Now loading: "$file""
#    rm "$data_dir"/split/data_*

#    pv "$file" | split -a 4 -l "$split_size" -d - "$data_dir"/split/data_
    pipenv run python scripts/db_insert.py \
        -d "$data_dir"/split -t "$max_threads" -c "$max_connections"
done
