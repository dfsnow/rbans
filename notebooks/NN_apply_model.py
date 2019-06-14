import operator
import csv
import os, math, sys
import string
import re
import ast
import numpy as np
import pandas as pd
import random
import time
import pickle
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from torch.nn import functional as F
from torchtext import data
from torchtext import datasets
from torchtext import vocab
from itertools import product
from multiprocessing import Pool, cpu_count
from ekphrasis.classes.preprocessor import TextPreProcessor
from ekphrasis.dicts.emoticons import emoticons

# Import model and model helper functions
sys.path.append("..")
import src.fasttext as ft
import src.fasttext_utils as ftu
from src.vaderSentiment import SentimentIntensityAnalyzer

data_dir = '../data'
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


# Load the trained model created by NN_train_model
model = torch.load(os.path.join(data_dir, 'model/NN_fasttext_model.pt'))
model.eval()
with open(os.path.join(data_dir, 'model/NN_fasttext_data.pkl'), 'rb') as input:
    TEXT = pickle.load(input)


# Initialize preprocessor for converting raw sentences to tokenized input data
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


def predict_from_preprocessed(sentence):
    tokenized = ast.literal_eval(sentence)
    if len(tokenized) == 0:
        return 0.0
    else:
        indexed = [TEXT.vocab.stoi[t] for t in tokenized]
        tensor = torch.LongTensor(indexed).to(device)
        tensor = tensor.unsqueeze(1)
        prediction = torch.round(torch.sigmoid(model(tensor)))
        return prediction.item()


def predict_from_sentence(sentence):
    tokenized = ftu.generate_bigrams([tok.lower() for tok in ekphrasis_processor.pre_process_doc(sentence)])
    if len(tokenized) == 0:
        return 0.0
    else:
        indexed = [TEXT.vocab.stoi[t] for t in tokenized]
        tensor = torch.LongTensor(indexed).to(device)
        tensor = tensor.unsqueeze(1)
        prediction = torch.round(torch.sigmoid(model(tensor)))
        return prediction.item()


def predict_from_list(body_list):
    tokenized = [ast.literal_eval(i) for i in body_list]
    indexed = [[TEXT.vocab.stoi[t] for t in tok] for tok in tokenized]
    b = np.zeros([len(indexed),len(max(indexed,key = lambda x: len(x)))])
    for i, j in enumerate(indexed):
        b[i][0:len(j)] = j
    b = np.array(b).transpose()
    tensor = torch.LongTensor(b).to(device)
    prediction = torch.round(torch.sigmoid(model(tensor)))
    return ftu.flatten(prediction.tolist())


# Testing the model
sent = """Ireland as a whole is far too leftist and cucked to leave the EU unfortunately."""

if predict_from_sentence(sent) == 1.0:
    print("This is hate speech!")
else:
    print("This is not hate speech!")


# Defining a function to take a list of all files in a month, concatenate them,
# run the model, and then output the combined CSV for each month
def concat_chunks(filelist):
    file_date = filelist[0][-11:-4]
    df = pd.concat((pd.read_csv(
        file,
        names=["id", "date", "author", "subreddit", "body", "sentiment"],
        dtype={"id": str, "date": str, "author": str, "subreddit": str, "body": str, "sentiment": float}
        ) for file in filelist))
    print("Finished concatenating", file_date)
    df["classification"] = df.body.map(predict_from_preprocessed)
#     df["classification"] = predict_from_list(df.body.tolist())
    print("Finished classifying", file_date)
    df["is_hate"] = (df.classification == 1.0) & (df.sentiment < -0.05).astype(int)
    df.drop(columns=["body", "id"], inplace=True)
    df.to_csv(
        os.path.join(data_dir, "analysis/concat_applied_data_" + file_date + ".csv"),
        quoting=csv.QUOTE_NONNUMERIC,
        header=True, index=False
    )


# Defining a list of jobs that need to be finished
completed_jobs = os.listdir(os.path.join(data_dir, 'split/'))
concat_jobs = os.listdir(os.path.join(data_dir, 'analysis/'))

batch = []
for year in range(2015, 2020):
    for month in range(1, 13):
        batch.append([
            os.path.join(data_dir, 'split/' + x) for
            x in completed_jobs if x[-11:-4] == str(year) + '_' + str(month).zfill(2) and
            'concat_applied_data_' + x[-11:-4] + '.csv' not in concat_jobs
        ])

batch = [x for x in batch if x != []]
print(len(ftu.flatten(batch)))


# Running the actual model and concatenation
# Noteably, this cannot be done in parallel since it relies on the
# CUDA implementation of the model for speed
for b in batch:
    concat_chunks(b)

