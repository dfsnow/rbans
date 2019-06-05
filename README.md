# The Effect of Subreddit Bans on Hate Speech

By Dan Snow and [Stephen Stapleton](https://github.com/sstaple15)

## Project Goals

The rise of social media has enabled unprecedented communication and community formation. Without geographic or social constraints, individuals have the opportunity to connect to others with shared hobbies, beliefs, and interests. However, the benefits of this new social landscape aren’t without costs.

Social media has given hate and 'fringe' groups new opportunities to organize. In the context of reddit, subreddits such as The_Donald have been the source of online bullying, doxxing, and propaganda. Given this problem, reddit has responded by implementing a sort of 'soft-ban' on The_Donald, enacting measures designed to limit The_Donald's site-wide presence and curtail its tendency toward hateful speech and behavior.

We examine the effect of this soft-ban on hate speech using a difference-in-difference approach. We measure the proportion of hate speech in the pre-and post-treatment periods using a FastText neural network initialized with GLoVe word embeddings and trained on a filtered corpus of pre-treatment comment data from particularly hateful subreddits. We further refine our classifier using VADER sentiment analysis, combining both our classification and the VADER compound sentiment score into a single binary outcome via a simple AND gate.

Finally, we consider the treatment group to be any active The_Donald poster (5 comments in the pre-treatment period). We establish a control group of active (20 comments in the pre-treatment period) users by matching them within the pre-treatment period on our independent variables using R's `MatchIt` package.

## Code

This project relies on a number of tools and packages. It is primarily written in Python 3.7 and utilizes PyTorch 0.4.0 and VADER. However, it also uses PostgreSQL, BigQuery, bash, and R. The nature and size of the data (~3 TB in a Postgres DB) makes it difficult to share for replication, however please feel free to reach out if you're interested in cleaned training or applied datasets.

The code structure is as follows, prefix number is lines of code. Work that is not entirely our own is marked with an asterisk.

```
rbans
├── data
│   ├── hate_subs.csv                   (list of hateful subreddits) 
│   ├── hate_words.csv                  (list of words pulled by SAGE) 
│   ├── analysis                        (dir for finished analysis data) 
│   ├── applied                         (dir for applied, monthly data samples)
│   ├── embeddings                      
│   │   └── glove.twitter.27B.100d.txt  (pre-trained GLoVe embeddings)
│   ├── model
│   │   └── NN_fasttext_data.pkl        (pickled pytorch model object)
│   └── split                           (temp dir for splitting CSVs)
├── notebooks
│   ├── matching_alg_workbook.R         (070, test workbook for matching and DiD)
│   ├── NN_apply_model.ipynb            (112, applying trained model to data)
│   ├── NN_apply_vader.ipynb            (077, applying VADER)
│   ├── NN_preprocess.ipynb             (177, preprocessing training data)
│   ├── NN_SAGE_test.ipynb              (038, testing SAGE)
│   ├── NN_train_model.ipynb            (102, training the FastText model)
│   └── author_analysis.Rmd             (100, final DiD analysis)
├── queries
│   ├── 01_create_training_sample.sql   (016, generate random pre-treat training sample)
│   ├── 02_create_applied_samples.sh    (014, generate monthly applied sample 10mil)
│   ├── 03_create_networks.sql          (029, create network comparison)
│   ├── 04_create_networks_bq.sql       (082, bigquery version of network comp.)
│   ├── 05_get_author_counts.sql        (010, get comment counts of authors)
│   └── 06_get_author_counts_bq.sql     (032, bigquery version of counts)    
├── README.md
├── scripts                             (dir for setup scripts and data loading)
│   ├── config-example.sh               (010, config file for setup scripts)
│   ├── data_download.sh                (034, download data from pushshift.io)
│   ├── data_extract.sh                 (025, extract downloaded data)
│   ├── data_split.sh                   (015, split CSV data into train, test, val)
│   ├── db_create.sh                    (046, create PSQL DB for comment data)
│   ├── db_insert.py                    (110, clean and insert comment data into DB)
│   ├── db_load.sh                      (012, entrypoint for loading comment data)
│   ├── zfs_setup_initiator.sh          (016, ZFS setup for connected machine)
│   └── zfs_setup_target.sh             (063, ZFS setup for host machine/DAS)
└── src
    ├── aggregation_funcs.R             (033, agg functions for labeled applied data)
    ├── deltaIterator.py                (*funcs for SAGE)
    ├── fasttext.py                     (090, *FastText model, mostly mine with some help)
    ├── fasttext_utils.py               (*utils for using FT model)
    ├── sage.py                         (*Python3 SAGE implementation)
    └── vaderSentiment.py               (*VADER sentiment from source)

```

## Sampling Information

The list of hateful subreddits in `data/hate_subs.csv` was compiled by manually scraping news articles and various RES filters. If you disagree with any of the subs or would like to add more, please feel free to make a pull request.

Initial data sample taken from 2015-01-01 - 2017-02-15, where hate posts are posts from the subreddits in the hate subs list
- Total size = 229,603,257
- Made up of 15% sample of all nonhate posts (221,257,093)
- Made up of 30% sample of all hate posts (8,346,164)

Preprocessing removed a few hundred thousand blank or meaningless posts. Filtering hate posts with the top 1000 words created by SAGE (in `data/hate_words.csv`) resulted in the removal of 2,165,292 posts, out of 8,346,164.

Finally, we split the resulting data into train, test, and validate subsets, resulting in the following number of posts for each set:
main_train.csv = 183000000
main_test.csv = 22800000
main_validate.csv = 22800000

Our compute power/memory was limited at the time, so we were only able to train on a small subsample of our original data. Our resulting train, test, validate split was:
main_train_subsample.csv = 22000000
main_test_subsample.csv = 2000000
main_validate_subsample.csv = 2000000

For all applied data, we sampled 10 million posts randomly for each month between 2015-01-01 and 2019-02-02.

## Model Performance

The FastText model generally performed well. It was considerably faster to train than a comparable RNN and was much simpler to implement. Using the listed hyperparameters, we had the following results:

Number of epochs = 6
Vocab size = 50,000
Learning rate = 1e-3

```
Epoch: 01 | Epoch Time: 28m 58s | Train Loss: 0.393 | Train Acc: 83.56%
Epoch: 02 | Epoch Time: 28m 32s | Train Loss: 0.378 | Train Acc: 84.31%
Epoch: 03 | Epoch Time: 29m 02s | Train Loss: 0.376 | Train Acc: 84.38%
Epoch: 04 | Epoch Time: 30m 37s | Train Loss: 0.375 | Train Acc: 84.41%
Epoch: 05 | Epoch Time: 29m 15s | Train Loss: 0.374 | Train Acc: 84.43%
Epoch: 06 | Epoch Time: 28m 29s | Train Loss: 0.372 | Train Acc: 84.44%
```

Our validation accuracy generally hovered around 82%. Accuracy on the test set using the final model was 81.5%
