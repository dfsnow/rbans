import operator
import os, math, sys, re
import string
import numpy as np
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

# Import model and model helper functions
sys.path.append("..")
import src.fasttext as ft
import src.fasttext_utils as ftu

seed = 2019
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
if torch.cuda.is_available():
    torch.cuda.manual_seed(seed)

data_dir = '../data'
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
batch_size = 64
max_vocab_size = 100000


# Defining the structure of the text data
TEXT = data.Field(
    sequential=True,
    preprocessing=ftu.generate_bigrams,
    tokenize=ftu.reg_tokenize,
    lower=True)

LABEL = data.Field(
    dtype = torch.float,
    sequential=False,
    use_vocab=False,
    pad_token=None,
    unk_token=None)

nn_fields = [("id", None),
              ("score", None),
              ("body", TEXT),
              ("label", LABEL)]


# Splitting sets into train test and validate + preprocessing and tokenizing
train, validate, test = data.TabularDataset.splits(
    path=data_dir,
    train='main_train_subsample.csv',
    validation="main_validate_subsample.csv",
    test='main_test_subsample.csv',
    format='csv',
    skip_header=False,
    fields=nn_fields)

print("Data successfully loaded...")

# Load pre-trained embeddings from twitter data
vec = vocab.Vectors('glove.twitter.27B.200d.txt', os.path.join(data_dir, 'embeddings'))

# Build our corpus of vocabulary
TEXT.build_vocab(train, max_size=max_vocab_size, vectors=vec, unk_init=torch.Tensor.normal_)
with open(os.path.join(data_dir, 'model/NN_fasttext_data.pkl'), 'wb') as output:
    pickle.dump(TEXT, output, pickle.HIGHEST_PROTOCOL)

print("Vocabulary built...")

# Batch each set for processing via our model
train_iter, validate_iter, test_iter = data.BucketIterator.splits(
    (train, validate, test), batch_size=batch_size,
    sort_key=lambda x: len(x.body),
    device=device, repeat=False)

print("Iterators created...")

# Initialize the model with the following params
vocab_size = len(TEXT.vocab)
embedding_weights = TEXT.vocab.vectors
embedding_dim = 200
output_dim = 1
padding_idx = TEXT.vocab.stoi[TEXT.pad_token]
unk_idx = TEXT.vocab.stoi[TEXT.unk_token]

model = ft.FastText(vocab_size, embedding_dim, output_dim, embedding_weights, padding_idx, unk_idx)
optim = torch.optim.Adam(model.parameters())
loss = nn.BCEWithLogitsLoss()

model = model.to(device)
loss = loss.to(device)

print(f'The model has {ftu.count_parameters(model):,} trainable parameters')


# Begin actually training the model, then verify against validate and test
num_epochs = 20
for epoch in range(num_epochs):

    start_time = time.time()

    train_loss, train_acc = ft.train_model(model, train_iter, optim, loss, epoch)

    end_time = time.time()
    epoch_mins, epoch_secs = ft.epoch_time(start_time, end_time)
    torch.save(model, os.path.join(data_dir, 'model/NN_fasttext_model.pt'))
    print(f'Epoch: {epoch+1:02} | Epoch Time: {epoch_mins}m {epoch_secs}s | Train Loss: {train_loss:.3f} | Train Acc: {train_acc*100:.2f}%')


validate_loss, validate_acc = ft.evaluate_model(model, validate_iter, loss)
print(f'Val. Loss: {validate_loss:.3f} | Val. Acc: {validate_acc*100:.2f}%')


test_loss, test_acc = ft.evaluate_model(model, validate_iter, loss)
print(f'Test Loss: {test_loss:.3f} | Test Acc: {test_acc*100:.2f}%')

