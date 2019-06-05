library(tidyverse)
library(lubridate)

get_subreddit_stats <- function(df, subreddits, treat_date) {
  df %>%
    mutate(
      date = make_date(year(date), month(date), day = 1),
      treated = if_else(subreddit %in% subreddits, 1, 0),
      post = if_else(date >= ymd(treat_date), 1, 0)
    ) %>%
    group_by(date, subreddit) %>%
    summarize(
      mean_sent = mean(sentiment, na.rm = T),
      mean_clas = mean(classification, na.rm = T),
      mean_hate = mean(is_hate, na.rm = T),
      cnt_clas = sum(classification, na.rm = T),
      cnt_hate = sum(is_hate, na.rm = T),
      count = n(),
      treated = mean(treated),
      post = mean(post)
    ) 
}

get_subreddit_summary <- function(df, subreddits, treat_date) {
  df %>%
    mutate(
      date = make_date(year(date), month(date), day = 1),
      treated = if_else(subreddit %in% subreddits, 1, 0),
      post = if_else(date >= ymd(treat_date), 1, 0)
    ) %>%
    group_by(date, treated) %>%
    summarize(
      mean_sent = mean(sentiment, na.rm = T),
      mean_clas = mean(classification, na.rm = T),
      mean_hate = mean(is_hate, na.rm = T),
      cnt_clas = sum(classification, na.rm = T),
      cnt_hate = sum(is_hate, na.rm = T),
      count = n(),
      treated = mean(treated),
      post = mean(post)
    ) 
}

get_author_stats <- function(df, authors) {
  df %>%
    mutate(
      date = make_date(year(date), month(date), day = 1),
      treated = if_else(author %in% authors, 1, 0)
    ) %>%
    group_by(date, author) %>%
    summarize(
      mean_sent = mean(sentiment, na.rm = T),
      mean_clas = mean(classification, na.rm = T),
      mean_hate = mean(is_hate, na.rm = T),
      cnt_clas = sum(classification, na.rm = T),
      cnt_hate = sum(is_hate, na.rm = T),
      count = n(),
      treated = mean(treated)
    ) 
}


get_author_prematch <- function(df, authors, caliper_date, treat_date) {
  df %>%
    mutate(
      date = make_date(year(date), month(date), day = 1),
      treated = if_else(author %in% authors, 1, 0)
    ) %>%
    filter(between(date, ymd(caliper_date), ymd(treat_date))) %>%
    group_by(author) %>%
    summarize(
      mean_sent = mean(sentiment, na.rm = T),
      mean_clas = mean(classification, na.rm = T),
      mean_hate = mean(is_hate, na.rm = T),
      cnt_clas = sum(classification, na.rm = T),
      cnt_hate = sum(is_hate, na.rm = T),
      count = n(),
      treated = mean(treated)
    ) 
}

get_caliper <- function(df, start_date, end_date) {
  temp <- df %>%
  filter(date >= ymd(start_date) & date <= ymd(end_date)) %>%  
    group_by(author, post) %>%
    summarize(
      mean_sent = weighted.mean(mean_sent, count, na.rm = T),
      mean_clas = weighted.mean(mean_clas, count, na.rm = T),
      mean_hate = weighted.mean(mean_hate, count, na.rm = T),
      cnt_clas = sum(cnt_clas, na.rm = T),
      cnt_hate = sum(cnt_hate, na.rm = T),
      treated = mean(treated)
    )
  model_mean_hate <- lm(mean_hate ~ treated * post, data = temp)
  model_cnt_hate <- lm(cnt_hate ~ treated * post, data = temp)
  model_mean_clas <- lm(mean_clas ~ treated * post, data = temp)
  model_cnt_clas <- lm(cnt_clas ~ treated * post, data = temp)
  model_list <- list(model_mean_hate, model_cnt_hate, model_mean_clas, model_cnt_clas)
  return(model_list)
}

author_agg_by_month <- function(df) {
  df %>%
    group_by(date, treated) %>%
    summarize(
      mean_sent = weighted.mean(mean_sent, count, na.rm = T),
      mean_clas = weighted.mean(mean_clas, count, na.rm = T),
      mean_hate = weighted.mean(mean_hate, count, na.rm = T),
      cnt_clas = sum(cnt_clas, na.rm = T),
      cnt_hate = sum(cnt_hate, na.rm = T)
    )
}
