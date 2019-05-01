import json
import threading
import gc
import db_config
from time import sleep
from datetime import datetime
from psycopg2 import pool

gc.collect()

# Open a threaded pool connection
psql_pool = pool.ThreadedConnectionPool(
        minconn = 1,
        maxconn = 100,
        user = db_config,
        host = "localhost",
        port = "5432",
        database = "reddit",
        password = db_config)

if(psql_pool):
    print("Connection pool created successfully")

def insert_comment(fname):

    ps_connection = psql_pool.getconn()
    ps_cursor = ps_connection.cursor()

    with open(fname, 'r') as json_file:
        for line in json_file:
            comment = json.loads(line)
            timestamp = datetime.utcfromtimestamp(int(comment["created_utc"]))
            comment["year"] = timestamp.year
            comment["month"] = timestamp.month

            ps_cursor.execute("""
                INSERT INTO comments (
                author,
                subreddit,
                parent_id,
                id,
                subreddit_id,
                body,
                year,
                month
                ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s)
                ;""", (
                    comment["author"],
                    comment["subreddit"],
                    comment["parent_id"],
                    comment["id"],
                    comment["subreddit_id"],
                    comment["body"],
                    comment["year"],
                    comment["month"]
                    ))

        ps_connection.commit()
        ps_cursor.close()
        psql_pool.putconn(ps_connection)

files = ["/home/snow/temp/test_" + str(x).zfill(2) for x in range(11)]
max_threads = 24

while len(files) > 0:
    if threading.active_count() < max_threads + 1:
        filen = files.pop()
        thread = threading.Thread(target=insert_comment, args=[filen])
        thread.start()
    else:
        sleep(0.1)

while threading.active_count() > 1:
    sleep(0.1)

#insert_comment('/home/snow/temp/RC_2006-05.json')

psql_pool.closeall



