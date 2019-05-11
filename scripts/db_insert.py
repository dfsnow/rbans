import db_config
import json
import threading
import gc
import os
import argparse
from time import sleep
from datetime import datetime
from psycopg2 import pool

gc.collect()

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

parser = argparse.ArgumentParser(description='Load chunks into PSQL')
parser.add_argument("-d", "--dir", help="specify input directory",
        type=str, required=True)
parser.add_argument("-t", "--threads", help="max number of threads",
        type=str, required=True)
parser.add_argument("-c", "--connections",
        help="max number of psql connections",
        type=str, required=True)

args = parser.parse_args()
max_threads = int(args.threads)
max_conns = args.connections
working_dir = args.dir

files = listdir_fullpath(working_dir)

# Open a threaded pool connection
psql_pool = pool.ThreadedConnectionPool(
        minconn = 1,
        maxconn = max_conns,
        user = db_config.db_user,
        host = "localhost",
        port = "5432",
        database = "reddit",
        password = db_config.db_password)

# Check if pool creation successful
if(psql_pool):
    print("Connection pool created successfully")

# Main insert function
def insert_comment(fname):

    # Retreive connection from threaded pool
    ps_connection = psql_pool.getconn()
    ps_cursor = ps_connection.cursor()

    # Open JSON chunk file, parse, and extract year and month
    with open(fname, 'r') as json_file:
        for line in json_file:
            comment = json.loads(line)
            timestamp = datetime.utcfromtimestamp(int(comment["created_utc"]))
            comment["date"] = timestamp.date()

            # Cursor execute insertion
            ps_cursor.execute("""
                INSERT INTO comments (
                author,
                subreddit,
                parent_id,
                id,
                score,
                body,
                date
                ) VALUES (
                %s, %s, %s, %s, %s, %s, %s)
                ;""", (
                    comment["author"],
                    comment["subreddit"],
                    comment["parent_id"],
                    comment["id"],
                    comment["score"],
                    comment["body"],
                    comment["date"]
                    ))

        # Commit changes, close connection, return conn to pool
        ps_connection.commit()
        ps_cursor.close()
        ps_connection.close()
        psql_pool.putconn(ps_connection)

        print("Successfully inserted: " + fname)


# Threading bit
while len(files) > 0:
    if threading.active_count() < max_threads + 1:
        filen = files.pop()
        thread = threading.Thread(target=insert_comment, args=[filen])
        thread.start()
    else:
        sleep(0.1)

while threading.active_count() > 1:
    sleep(0.1)

# Close all connections
psql_pool.closeall



