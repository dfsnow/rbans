import json
import psycopg2
import datetime
from psycopg2 import pool
from multiprocessing import Pool

psql_pool = pool.ThreadedConnectionPool(1, 40, user = "snow",
        host = "localhost",
        port = "5432",
        database = "reddit",
        password = "Stonefish21")

if(psql_pool):
    print("Connection pool created successfully")

ps_connection  = psql_pool.getconn()
def insert_comment(fname):

    ps_cursor = ps_connection.cursor()

    with open(fname, 'r') as json_file:
        for line in json_file:
            comment = json.loads(line)
            timestamp = datetime.datetime.utcfromtimestamp(comment["created_utc"])
            comment["year"] = timestamp.year
            comment["month"] = timestamp.month
            comment["day"] = timestamp.day
            del comment["gilded"]
            del comment["edited"]
            del comment["controversiality"]
            del comment["created_utc"]

            ps_cursor.execute("""
                INSERT INTO comments (
                author,
                subreddit,
                parent_id,
                id,
                subreddit_id,
                body,
                year,
                month,
                day) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ;""", (
                    comment["author"],
                    comment["subreddit"],
                    comment["parent_id"],
                    comment["id"],
                    comment["subreddit_id"],
                    comment["body"],
                    comment["year"],
                    comment["month"],
                    comment["day"]
                    ))

        ps_connection.commit()

files = ["/home/snow/temp/data_" + str(x).zfill(2) for x in range(36)]

process_pool = Pool()
process_pool.map(insert_comment, files)

psql_pool.closeall



