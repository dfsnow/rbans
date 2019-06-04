library(tidyverse)
library(lubridate)

sub_agg <- function(df) {
  df %>%
    mutate(
      month = month(date),
      year = year(date)
      ) %>%
    group_by(subreddit, year, month) %>%
    summarize(
      mean_sent = mean(sentiment, na.rm = T),
      mean_clas = mean(classification, na.rm = T),
      mean_hate = mean(is_hate, na.rm = T),
      cnt_clas = sum(classification, na.rm = T),
      cnt_hate = sum(is_hate, na.rm = T),
      count = n()
    )
}

auth_agg <- function(df) {
  df %>%
    mutate(month = month(date)) %>%
    group_by(author, month) %>%
    summarize(
      mean_sent = mean(sentiment, na.rm = T),
      mean_clas = mean(classification, na.rm = T),
      mean_hate = mean(is_hate, na.rm = T),
      cnt_clas = sum(classification, na.rm = T),
      cnt_hate = sum(is_hate, na.rm = T),
      count = n()
    )
}
