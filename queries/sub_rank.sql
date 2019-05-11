SELECT DISTINCT d.author, d.subreddit sub_b, count(*) OVER(PARTITION BY d.subreddit, d.author)
FROM comments_2008_02 c
JOIN (
SELECT DISTINCT author, subreddit
FROM comments_2008_02
WHERE subreddit IN (
    SELECT subreddit
    FROM (
        SELECT subreddit, count(*) AS comments
        FROM comments_2008_02
        GROUP BY subreddit 
        ORDER BY comments
        LIMIT 1000
    ) a
)) d ON d.author = c.author
WHERE d.subreddit != c.subreddit
ORDER BY d.author
