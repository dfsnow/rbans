# rbans
Examining the effect of subreddit bans using NLP and ML

Training Sample 2015/01/01 - 2017/02/15, ALL = 229,603,257
15 % sample of all nonhate posts
30 % sample of all hate posts (8346164)

main_data_preprocessed.csv = 229203259
main_data_filtered.csv = 227037967

Removed via SAGE = 2165292

main_train.csv = 183000000
main_test.csv = 22800000
main_validate.csv = 22800000

Applied Sample 2015/01/01 - 2019/02/28, 10 mil per month 

Epoch: 01 | Epoch Time: 28m 58s | Train Loss: 0.393 | Train Acc: 83.56%
Epoch: 02 | Epoch Time: 28m 32s | Train Loss: 0.378 | Train Acc: 84.31%
Epoch: 03 | Epoch Time: 29m 2s | Train Loss: 0.376 | Train Acc: 84.38%
Epoch: 04 | Epoch Time: 30m 37s | Train Loss: 0.375 | Train Acc: 84.41%
