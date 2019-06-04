DROP TABLE IF EXISTS author_counts;
CREATE TABLE author_counts 
AS (
    SELECT author, COUNT(*) as count,
        SUM(case when subreddit = 'The_Donald' then 1 else 0 end) AS td_count
    FROM comments
    WHERE date BETWEEN '2016-02-01' AND '2017-02-15'
    AND author IN (SELECT author FROM authors)
    GROUP BY author HAVING COUNT(1) > 0)

