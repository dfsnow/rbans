WITH sub_rank AS (
SELECT subreddit, authors, DENSE_RANK() OVER (ORDER BY authors DESC) AS author_rank
FROM (
    SELECT subreddit, SUM(1) AS authors
    FROM (
        SELECT subreddit, author 
        FROM comments_2012_01
        GROUP BY subreddit, author HAVING COUNT(1) > 0) xa
    GROUP BY subreddit) xb
ORDER BY authors DESC
)
SELECT l.subreddit AS subl, r.subreddit AS subr, SUM(1) AS auths
FROM (
    SELECT subreddit, author, COUNT(1) 
    FROM comments_2012_01 
    WHERE subreddit IN (
        SELECT subreddit FROM sub_rank
        WHERE author_rank > 20 AND author_rank < 300)
    OR subreddit IN (
        SELECT subreddit FROM hate_subs)
    GROUP BY subreddit, author) l
JOIN (
    SELECT subreddit, author, COUNT(1)
    FROM comments_2012_01 
    GROUP BY subreddit, author) r
ON l.author = r.author
WHERE l.subreddit != r.subreddit
GROUP BY l.subreddit, r.subreddit
ORDER BY auths DESC
