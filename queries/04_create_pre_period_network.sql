-- Bigquery SQL for finding network for the pre-period
WITH comments AS (
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2015_01`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2015_02`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2015_03`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2015_04`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2015_05`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2015_06`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2015_07`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2015_08`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2015_09`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2015_10`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2015_11`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2015_12`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2016_01`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2016_02`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2016_03`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2016_04`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2016_05`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2016_06`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2016_07`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2016_08`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2016_09`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2016_10`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2016_11`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2016_12`
union all
SELECT subreddit, author FROM `fh-bigquery.reddit_comments.2017_01`
),
sub_rank AS (
SELECT subreddit, authors, DENSE_RANK() OVER (ORDER BY authors DESC) AS author_rank
FROM (
    SELECT subreddit, SUM(1) AS authors
    FROM (
        SELECT subreddit, author 
        FROM comments
        GROUP BY subreddit, author HAVING COUNT(1) > 0) xa
    GROUP BY subreddit) xb
ORDER BY authors DESC
)
SELECT l.subreddit AS subl, r.subreddit AS subr, SUM(1) AS auths
FROM (
    SELECT subreddit, author, COUNT(1) as count
    FROM comments
    WHERE subreddit IN (
        SELECT subreddit FROM sub_rank
        WHERE author_rank > 20 AND author_rank < 2000)
        OR subreddit IN (
        SELECT subreddit FROM `adv-ml-reddit-queries.comments.hate_subs`)
    GROUP BY subreddit, author) l
JOIN (
    SELECT subreddit, author, COUNT(1) as count
    FROM comments
    GROUP BY subreddit, author) r
ON l.author = r.author
WHERE l.subreddit != r.subreddit
GROUP BY l.subreddit, r.subreddit
ORDER BY auths DESC

