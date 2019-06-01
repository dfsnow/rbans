# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.3
#   kernelspec:
#     display_name: Python [conda env:pytorch_cuda_9.0]
#     language: python
#     name: conda-env-pytorch_cuda_9.0-py
# ---

# +
import os
import re
import csv
import sage
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count
from tqdm import tqdm, tqdm_notebook
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from ekphrasis.classes.preprocessor import TextPreProcessor
from ekphrasis.classes.tokenizer import SocialTokenizer
from ekphrasis.dicts.emoticons import emoticons

tqdm.pandas(tqdm_notebook)
data_path = "/home/dfsnow/rbans/data/"

# +
# Create ekphrasis preprocessor class
ekphrasis_processor = TextPreProcessor(
    normalize=['url', 'email', 'percent', 'money', 'phone', 'user', 'time', 'date', 'number'],  # normalize terms
    fix_html=True,  # fix HTML tokens
    segmenter="english",  # corpus for word segmentation
    corrector="english",  # corpus for spell correction
    unpack_hashtags=True,  # perform word segmentation on hashtags
    unpack_contractions=True,  # unpack contractions
    spell_correct_elong=False,  # spell correction for elongated words
    dicts=[emoticons]  # replace emojis with words
)

ekphrasis_tokenizer = SocialTokenizer(lowercase=True).tokenize
flatten = lambda l: [item for sublist in l for item in sublist]
# -

# ## Shuffling
#
# This section is dedicated to ensuring that the sample drawn from Postgres is sufficiently shuffled.

# Load the shuffled main training data into memory
train = pd.read_csv(
    os.path.join(data_path, "main_data_sample.csv"),
    dtype={"":np.int64, "id": str, "score": str, "body": str, "label": int}
)

# Shuffle all the training data to ensure a random distribution
train = shuffle(train)

# Save the shuffled data to disk
train.to_csv(os.path.join(data_path, "main_data_shuffled.csv"), quoting=csv.QUOTE_NONNUMERIC)


# ## Preprocessing
#
# This section is dedicated to preprocessing all of the data using ekphrasis. Doing this in chunks is more efficient, since ekphrasis takes quite awhile to run. After processing all chunks, we concatenate them back together in the command line and load the cleaned data from here on.

# +
def read_iter(start_row):
    chunksize = 100000
    filename = int(start_row / chunksize)
    shuffled_data = os.path.join(data_path, "main_data_shuffled.csv")
    chunk = pd.read_csv(
        shuffled_data, index_col=0, skiprows=start_row, nrows=chunksize,
        names=["index", "id", "score", "body", "label"],
        dtype={"index": np.int64, "id": str, "score": str, "body": str, "label": int},
    )
    chunk["body"] = chunk.body.map(ekphrasis_processor.pre_process_doc)
    chunk.to_csv(
        os.path.join(data_path, "split/" + str(filename).zfill(4) + "_preprocessed_chunk.csv"),
        quoting=csv.QUOTE_NONNUMERIC,
        header=False, index=False
    )

train_len = 229603257
completed = [int(chunk[0:4]) * 100000 for chunk in os.listdir(os.path.join(data_path, 'split/'))]
all_jobs = list(range(0, train_len, 100000))
jobs = set(all_jobs) - set(completed)
print(jobs)
pool = Pool(cpu_count() - 1)
pool.map(read_iter, jobs)
# -

# ## SAGE Filtering
#
# This section is dedicated to removing noise from our labelled posts. By using Sparse Additive Generative Model (SAGE), we can find words that are more common in hateful posts than in nonhateful posts. These words can be used as an initial filter for our training data by removing any "hateful" posts that do not container them. As a result, we filter out meaningless or nonspecific labelled posts and keep only the more specific language of hate.

# Load in the shuffled, preprocessed training data
train = pd.read_csv(
    os.path.join(data_path, "main_data_preprocessed.csv"),
    dtype={"id": str, "score": str, "body": str, "label": int},
    nrows=20000000
)

# Get word counts for the hate and non-hate samples, tokenizing with ekphrasis
base_counts = dict(Counter(flatten([ekphrasis_tokenizer(str(body)) for body in train.loc[train.label == 0].body])))
hate_counts = dict(Counter(flatten([ekphrasis_tokenizer(str(body)) for body in train.loc[train.label == 1].body])))

# Get the most common hate words
hate_vocab = [word for word,count in Counter(hate_counts).most_common(5000)]

# Convert the counts into numerically comparable arrays
hate_array = np.array([hate_counts.get(word, 0) for word in hate_vocab])
base_array = np.array([base_counts.get(word, 0) for word in hate_vocab]) + 1.

# Use the SAGE algorithm to get the top K words from hate subs
mu = np.log(base_array) - np.log(base_array.sum())
beta = sage.estimate(hate_array, mu)
hate_words = sage.topK(beta, hate_vocab, 2000)
print(hate_words)

# Save the hate words to a list CSV
with open(os.path.join(data_path, "hate_words.csv"), "w") as f:
    writer = csv.writer(f)
    for word in hate_words:
        writer.writerow([word])

# ### Filtering Step

# +
hate_words = pd.read_csv(
    os.path.join(data_path, "hate_words.csv"),
    names=["word"],
    squeeze=True
).tolist()[0:1000]

def vocab_filter(start_row):
    chunksize = 100000
    filename = int(start_row / chunksize)
    shuffled_data = os.path.join(data_path, "main_data_preprocessed.csv")
    chunk = pd.read_csv(
        shuffled_data, skiprows=start_row, nrows=chunksize,
        names=["id", "score", "body", "label"],
        dtype={"id": str, "score": str, "body": str, "label": int},
    )

    chunk = chunk.loc[
        (chunk.label == 1 & chunk.body.str.contains('|'.join(re.escape(w) for w in hate_words), case=False)) |
        (chunk.label == 0)
    ]

    chunk.to_csv(
        os.path.join(data_path, "vocab/" + str(filename).zfill(4) + "_preprocessed_chunk.csv"),
        quoting=csv.QUOTE_NONNUMERIC,
        header=False, index=False
    )

train_len = 229603257
completed = [int(chunk[0:4]) * 100000 for chunk in os.listdir(os.path.join(data_path, 'vocab/'))]
all_jobs = list(range(0, train_len, 100000))
jobs = set(all_jobs) - set(completed)
print(len(jobs))
pool = Pool(16)
pool.map(vocab_filter, jobs)
# -

# ## Splitting
#
# Splitting the data into train, test, and validate using an 80, 20, 20 split

train = pd.read_csv(
    os.path.join(data_path, "main_data_filtered.csv"),
    dtype={"id": str, "score": str, "body": str, "label": int}
)
train.label.sum()

# Split hate and nonhate datasets into train, test, and validate
train, test = train_test_split(train, test_size=0.2, random_state=2)
train, validate = train_test_split(train, test_size=0.2, random_state=2)

# Save train test and validate to CSV
train.to_csv(os.path.join(data_path, "main_train.csv"), index=False)
test.to_csv(os.path.join(data_path, "main_test.csv"), index=False)
validate.to_csv(os.path.join(data_path, "main_validate.csv"), index=False)
