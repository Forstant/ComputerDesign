import torch
import torch.nn as nn
import torch.nn.functional as F
import tqdm
import os
from dataloader import *

def predict(model, dataset, device):    # the dataset here has to be a torch.utils.data.Dataset object
    model.eval()

    preds = []
    for batch in tqdm(dataset):
        with torch.no_grad():
            batch = tuple(t.to(device) for t in batch)
            X, y, attention_mask = batch
            output = model(X, attention_mask=attention_mask, labels=y)
            logits = output.logits
            preds.extend(logits.cpu().tolist())

    return preds


if __name__ == '__main__':

    # load model from local file
    model_path = ''
    dataset_name = ''  # the path to the dataset, the dataset is a .csv file stored in the ../data directory
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
    dataset = SentimentDataset(tokenizer, [dataset_name])

    if os.path.exists(model_path) == True:
        model = torch.load(model_path)
        preds = predict(model, dataset, 'cuda')


