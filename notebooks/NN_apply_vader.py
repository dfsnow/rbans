import operator
import csv
import os, sys, re
import ast
import string
import numpy as np
import pandas as pd
import random
import time
import pickle
from ekphrasis.classes.preprocessor import TextPreProcessor
from ekphrasis.dicts.emoticons import emoticons
from multiprocessing import Pool, cpu_count
from itertools import product

# Import model and model helper functions
sys.path.append("..")
import src.fasttext as ft
import src.fasttext_utils as ftu
from src.vaderSentiment import SentimentIntensityAnalyzer

data_dir = '../data'

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Initialize ekphrasis preprocessing using GitHub defaults + a regex tokenizer
ekphrasis_processor = TextPreProcessor(
    normalize=['url', 'email', 'percent', 'money', 'phone', 'user', 'time', 'date', 'number'],  # normalize terms
    fix_html=True,  # fix HTML tokens
    segmenter="english",  # corpus for word segmentation
    corrector="english",  # corpus for spell correction
    unpack_hashtags=True,  # perform word segmentation on hashtags
    unpack_contractions=True,  # unpack contractions
    spell_correct_elong=False,  # spell correction for elongated words
    tokenizer=ftu.reg_tokenize,
    dicts=[emoticons]  # replace emojis with words
)

# Add simple error handling to the VADER analyzer
def compound_analyzer(sentence):
    try:
        return analyzer.polarity_scores(sentence)['compound']
    except:
        return 0.0

# Function for converting a raw sentence to preprocessed, tokenized list
def model_preprocess(sentence):
    tokenized = ftu.generate_bigrams([tok.lower() for tok in ekphrasis_processor.pre_process_doc(sentence)])
    return tokenized


# This function takes in the name of an output file and creates
# that file based on a subsection of the correct input file
# It splits input files into chunks and preforms preprocessing in parallel
def apply_vader(file):
    chunksize = 100000
    start_row = int(float(file[0:4]) * chunksize)
    if start_row == 0:
        start_row = 1
    filename = "applied/" + str(file[5:])
    applied_data = os.path.join(data_dir, filename)
    chunk = pd.read_csv(
        applied_data, skiprows=start_row, nrows=chunksize,
        names=["id", "date", "author", "subreddit", "body"],
        dtype={"id": str, "date": str, "author": str, "subreddit": str, "body": str},
    )
    chunk["sentiment"] = chunk.body.map(compound_analyzer)
    chunk["body"] = chunk.body.map(model_preprocess)
    chunk.to_csv(
        os.path.join(data_dir, "split/" + file),
        quoting=csv.QUOTE_NONNUMERIC,
        header=False, index=False
    )

# Creating a list of all jobs
file_list = os.listdir(os.path.join(data_dir, 'applied/'))
chnk_list = [str(x).zfill(4) + "_" for x in range(101)]
all_jobs = [''.join(x) for x in list(product(chnk_list, file_list))]

completed_jobs = os.listdir(os.path.join(data_dir, 'split/'))

jobs = set(all_jobs) - set(completed_jobs)
jobs = [x for x in jobs if x[-4:] == ".csv"]

# Running all jobs
print(len(jobs))
pool = Pool(18)
pool.map(apply_vader, jobs)
