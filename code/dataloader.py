import json
import codecs
import pandas as pd
from torch.utils.data import Dataset
from torch.utils.data import DataLoader, random_split
from transformers import BertTokenizerFast


# import the datasets
def load_data(path):
    df = pd.read_csv(path)

    for idx, row in df.iterrows():
        row['review'] = row['review'].strip('"')
        # truncate the review string if it exceeds maximum length(512)
        if(len(row['review']) > 512):
            # add another row to the dataframe
            df.loc[len(df)] = [row['review'][512:], row['label']]
            row['review'] = row['review'][:512]
        
    return df

def load_datasets(nameList):
    datasets = []
    for name in nameList:
        path = '../data/' + name + '.csv'
        df = load_data(path)
        datasets.append(df)
        print(f"{name} dataset is prepared")

        return datasets

class SentimentDataset(Dataset):
    def __init__(self, tokenizer, nameList):
        self.tokenizer = tokenizer
        self.data = []
        dataList = load_datasets(nameList)
        for dataset in dataList:
            for idx, row in dataset.iterrows():
                self.data.append([row['review'], row['label']]) # format: [[review, label], ...]

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, item):
        review, label = self.data[item]
        encoded_text = self.tokenizer(
            review,
            add_special_tokens=True,
            max_length=512,
            padding='max_length',
            truncation=True,
            return_token_type_ids=False,
            return_attention_mask=True,
            return_tensors='pt' # return PyTorch tensors
        )

        return encoded_text['input_ids'][0], label, encoded_text['attention_mask'][0]
    
def get_dataset(ratio, tokenizer, nameList):
    my_dataset = SentimentDataset(tokenizer, nameList)

    trainlen = int(ratio * len(my_dataset))
    lengths = [trainlen, len(my_dataset) - trainlen]

    trainset, validset = random_split(my_dataset, lengths)
    return trainset, validset

def get_loader(ratio, batch_size, n_workers, tokenizer, nameList):
    trainset, validset = get_dataset(ratio, tokenizer, nameList)

    train_loader = DataLoader(
        trainset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=n_workers
    )

    valid_loader = DataLoader(
        validset,
        batch_size=batch_size,
        num_workers=n_workers
    )

    return train_loader, valid_loader


# test function
if __name__ == '__main__':
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-chinese')
    train_loader, valid_loader = get_loader(0.8, 16, 4, tokenizer, ['waimai_10k'])
    print(len(train_loader))
    print(len(valid_loader))

    for input_ids, label, attention_mask in train_loader:
        print(input_ids.shape)
        print(label.shape)
        print(attention_mask.shape)
        break

    for input_ids, label, attention_mask in valid_loader:
        print(input_ids.shape)
        print(label.shape)
        print(attention_mask.shape)
        break