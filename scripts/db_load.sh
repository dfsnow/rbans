
source scripts/config.sh

for file in $(ls -d "$data_dir"/*.json); do

    echo "Now loading: "$file""
    rm "$data_dir"/split/data_*

    split -l "$split_size" -d "$file" "$data_dir"/split/data_
    pipenv run python scripts/db_insert.py \
        -d "$data_dir"/split -t "$max_threads" -c "$max_connections"
done
