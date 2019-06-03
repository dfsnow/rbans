import re

flatten = lambda l: [item for sublist in l for item in sublist]

def generate_bigrams(x):
    n_grams = set(zip(*[x[i:] for i in range(2)]))
    for n_gram in n_grams:
        x.append(' '.join(n_gram))
    return x


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def reg_tokenize(text):
    words = re.compile(r'\w+').findall(text)
    return words

