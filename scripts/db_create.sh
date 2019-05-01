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
        "parent_id" varchar(20),
        "id" varchar(20),
        "subreddit_id" varchar(20),
        "body" varchar(50000),
        "year" smallint,
        "month" smallint
        );
    COMMIT;

EOD
