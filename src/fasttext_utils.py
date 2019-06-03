# Some user-defined helper functions

flatten = lambda l: [item for sublist in l for item in sublist]

def generate_bigrams(x):
    n_grams = set(zip(*[x[i:] for i in range(2)]))
    for n_gram in n_grams:
        x.append(' '.join(n_gram))
    return x


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def predict_from_sentence(model, sentence):
    model.eval()
    tokenized = generate_bigrams([tok for tok in SocialTokenizer(lowercase=True).tokenize(sentence)])
    indexed = [TEXT.vocab.stoi[t] for t in tokenized]
    tensor = torch.LongTensor(indexed).to(device)
    tensor = tensor.unsqueeze(1)
    prediction = torch.round(torch.sigmoid(model(tensor)))
    return prediction.item()


def predict_from_batch(sentence):
    model.eval()
    indexed = [TEXT.vocab.stoi[t] for t in sentence]
    tensor = torch.LongTensor(indexed).to(device)
    tensor = tensor.unsqueeze(1)
    prediction = torch.round(torch.sigmoid(model(tensor)))
    return prediction.item()
