# Create the FastText model outlined in this notebook:
# https://github.com/bentrevett/pytorch-sentiment-analysis/blob/master/3%20-%20Faster%20Sentiment%20Analysis.ipynb
# and further described in this paper:
# https://arxiv.org/abs/1607.01759

import torch
import torch.nn as nn
from torch.nn import functional as F

class FastText(nn.Module):
    def __init__(self, vocab_size, embedding_dim, output_dim, embedding_weights, padding_idx, unk_idx):
        super().__init__()

        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.embedding_weights = embedding_weights
        self.output_dim = output_dim
        self.padding_idx = padding_idx

        self.embeddings = nn.Embedding(vocab_size, embedding_dim, padding_idx=padding_idx)
        self.embeddings.weight.data.copy_(embedding_weights)
        self.embeddings.weight.data[unk_idx] = torch.zeros(embedding_dim)
        self.embeddings.weight.data[padding_idx] = torch.zeros(embedding_dim)

        self.label = nn.Linear(embedding_dim, output_dim)

    def forward(self, text):

        embedded = self.embeddings(text)
        embedded = embedded.permute(1, 0, 2)
        pooled = F.avg_pool2d(embedded, (embedded.shape[1], 1)).squeeze(1)

        return self.label(pooled)


def binary_accuracy(preds, y):
    rounded_preds = torch.round(torch.sigmoid(preds))
    correct = (rounded_preds == y).float()
    acc = correct.sum() / len(correct)
    return acc


def epoch_time(start_time, end_time):
    elapsed_time = end_time - start_time
    elapsed_mins = int(elapsed_time / 60)
    elapsed_secs = int(elapsed_time - (elapsed_mins * 60))
    return elapsed_mins, elapsed_secs


def train_model(model, train_iter, optimizer, loss_func, epoch):

    total_epoch_loss = 0
    total_epoch_acc = 0
    steps = 0

    model.train()
    for idx, batch in enumerate(train_iter):
        optimizer.zero_grad()
        predictions = model(batch.body).squeeze(1)
        loss = loss_func(predictions, batch.label)
        acc = binary_accuracy(predictions, batch.label)
        loss.backward()
        optimizer.step()
        steps += 1

        if steps % 5000 == 0:
            print (f'Epoch: {epoch+1}, Idx: {idx+1}, Training Loss: {loss.item():.4f}, Training Accuracy: {acc.item()*100: .2f}%')

        total_epoch_loss += loss.item()
        total_epoch_acc += acc.item()

    return total_epoch_loss / len(train_iter), total_epoch_acc / len(train_iter)


def evaluate_model(model, validate_iter, loss_func):

    total_epoch_loss = 0
    total_epoch_acc = 0

    model.eval()
    with torch.no_grad():
        for idx, batch in enumerate(validate_iter):
            predictions = model(batch.body).squeeze(1)
            loss = loss_func(predictions, batch.label)
            acc = binary_accuracy(predictions, batch.label)

            total_epoch_loss += loss.item()
            total_epoch_acc += acc.item()

    return total_epoch_loss / len(validate_iter), total_epoch_acc / len(validate_iter)
