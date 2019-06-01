# Split the shuffled, preprocessed, filtered data into train, test, and validate
tail -n +2 ../data/main_data_filtered.csv \
    | head -n 183000000 \
    > ../data/main_train.csv
echo "Created training split..."

tail -n +183000000 ../data/main_data_filtered.csv \
    | head -n 22800000 \
    > ../data/main_validate.csv
echo "Created validate split..."

tail -n +205800000 ../data/main_data_filtered.csv \
    | head -n 22800000 \
    > ../data/main_test.csv
echo "Created test split..."
