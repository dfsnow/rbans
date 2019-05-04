



-- SELECT author, subreddit
    -- FROM comments_2011_05
    -- WHERE subreddit IN (
    --     SELECT subreddit
    --     FROM (
            SELECT subreddit, COUNT(DISTINCT author) AS authors, COUNT(*) AS comments
            FROM comments
            WHERE date >= '2011-05-01' AND date < '2011-06-01'
            GROUP BY subreddit 
            ORDER BY authors DESC
       --  ) b
       --  WHERE authors > 100
    -- )
