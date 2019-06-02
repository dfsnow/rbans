# Do a network analysis: Setup only

library(readr)

nodes <- read_csv("C:/Users/Stephen Stapleton/Downloads/polnet2018/Data files/Dataset1-Media-Example-NODES.csv")
edges <- read_csv("C:/Users/Stephen Stapleton/Downloads/polnet2018/Data files/Dataset1-Media-Example-EDGES.csv")

library(visNetwork)

nodes$shape <- "dot"
nodes$shadow <- TRUE
nodes$title <- nodes$type.label
nodes$label <- nodes$media
nodes$size <- nodes$audience.size
nodes$borderWidth <- 2
nodes$color.background <- c("#FF4850", "#2590CC", "#FFFB61")[nodes$media.type]
nodes$color.border <- "black"
nodes$color.highlight.background <- "dark grey"
nodes$color.highlight.border <- "grey"

edges$width <- 1+edges$weight/10
edges$color <- "grey"
edges$smooth <- TRUE

visnet <- visNetwork(nodes, edges)

visOptions(visnet, highlightNearest = TRUE, selectedBy = "type.label")

##############################################################

# Prepare a k-nearest neighbor matching

# incoming df has:
#### subreddit, person id, date, yes/no hate speech
df$date_fix <- as.Date(as.character(df$date), "%m%d%Y")
df$month_yr <- format(as.Date(df$date_fix), "%Y-%m")
df$treated <- ifelse(df$subreddit == "the_Donald", 1, 0)

# agglomerate posts by person_id and month
library(plyr)
df_m <- ddply(df, .(person_id, month_yr), summarize,
                 treated = max(treated, na.rm = T),
                 volume = n(),
                 mean_score = mean(hate_speech, na.rm = T))


# match on volume and mean_score in 6 months prior
library(MatchIt)
set.seed(100)

df_y %<>% df %>%
  subset(df$month_yr > 2016) %>%
  ddply(.(person_id), summarize,
        treated = max(treated, na.rm = T),
        volume = n(),
        mean_score = mean(hate_speech, na.rm = T))

match.out <- matchit(treated ~ volume + mean_score,
                     method = "nearest", data = df_y)

# get matched observations
df_matched <- match.data(match.out)

# put these matched back into the full df

# check for parallel pre-trends assumption (plot & regression)
### regression: see if control/treated slope differ across t=0

# run diff-in-diff