import pandas as pd
import pickle
import torch


def open_file(file_path):

    df = pd.read_csv(file_path, delimiter='\t')
    return df

data = open_file('/home/filippo/Scrivania/Marianna_head/wiki_naples_wquest.tsv')


questions = [q.lower() for q in data['question'].tolist()]
contexts = [content for content in data['text'].tolist()]


with open('/home/filippo/Scrivania/Marianna_head/vec_database.pkl', 'rb') as file:
    corpus_embeddings = pickle.load(file)


formatted_data = [{'context': content, 'question': question.lower(), 'quest_emb': emb.clone().detach()} for content, question, emb in zip(data['text'], data['question'], corpus_embeddings)]

torch.save(formatted_data, "questions_tensors.pt")
