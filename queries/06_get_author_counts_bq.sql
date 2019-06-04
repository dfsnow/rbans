WITH comments AS (
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date FROM `fh-bigquery.reddit_comments.2016_02`
union all
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date FROM `fh-bigquery.reddit_comments.2016_03`
union all
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date  FROM `fh-bigquery.reddit_comments.2016_04`
union all
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date  FROM `fh-bigquery.reddit_comments.2016_05`
union all
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date  FROM `fh-bigquery.reddit_comments.2016_06`
union all
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date FROM `fh-bigquery.reddit_comments.2016_07`
union all
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date  FROM `fh-bigquery.reddit_comments.2016_08`
union all
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date  FROM `fh-bigquery.reddit_comments.2016_09`
union all
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date FROM `fh-bigquery.reddit_comments.2016_10`
union all
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date FROM `fh-bigquery.reddit_comments.2016_11`
union all
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date  FROM `fh-bigquery.reddit_comments.2016_12`
union all
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date  FROM `fh-bigquery.reddit_comments.2017_01`
union all
SELECT subreddit, author, DATE(TIMESTAMP_SECONDS(created_utc)) as date FROM `fh-bigquery.reddit_comments.2017_02`
)
SELECT author, COUNT(*) as count, SUM(case when subreddit = 'The_Donald' then 1 else 0 end) AS td_count
FROM comments
WHERE date BETWEEN '2016-02-01' AND '2017-02-15'
AND author IN (SELECT author FROM `adv-ml-reddit-queries.comments.authors`)
GROUP BY author HAVING COUNT(1) > 0

