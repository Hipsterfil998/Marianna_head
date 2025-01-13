import torch
import pandas as pd
import pickle
import ollama
from sentence_transformers import SentenceTransformer, util

loaded_questions_tensors = torch.load("/home/filippo/Scrivania/Marianna_head/questions_tensors.pt", weights_only=True)

all_q_vecs = [triplet['quest_emb'] for triplet in loaded_questions_tensors]

model_name = 'HipFil98/sbert-mariannaQA-ita' #https://huggingface.co/HipFil98/sbert-mariannaQA-ita
model = SentenceTransformer(model_name)

def search(inp_question):
    question_embedding = model.encode(inp_question, convert_to_tensor=True)
    hits = util.semantic_search(question_embedding, all_q_vecs)
    hits = hits[0] 

    return hits

def best_context(best_ids):
    best_quests = [all_q_vecs[el['corpus_id']] for el in best_ids]

    best_context = []
    for el in best_quests:
        best_c = [item['context'] for item in loaded_questions_tensors if torch.equal(item['quest_emb'], el)]
        best_context.append(best_c[0])

    return best_context[0]



def Marianna_head(query):

    SYSTEM_PROMPT = """Sei un assistente virtuale per una mostra dedicata alla storia, alle attrazioni, ai siti e alla geografia della città di Napoli. 
                        Il tuo compito è dare risposte esaustive alle domande che ti vengono poste utilizzando esclusivamente le informazioni contenute nel contesto che ti viene fornito. 
                        Riformula il contesto in circa 80 parole per rispondere alla domanda dell'utente. 
                        Ricorda di: 
                        - Non inventare informazioni che non sono esplicitamente presenti nel contesto. 
                        - Rispondere in modo chiaro e conciso in italiano usando un linguaggio di tipo divulgativo. 
                        - Informare l'utente che non hai i dati necessari se il contesto non contiene informazioni rilevanti per rispondere alla domanda. 
                        - Mantenere un tono cordiale, uno stile semplice e divulgativo adatto a un pubblico di turisti interessati alla storia e all'archeologia.""" 

    
    CONTEXT_PROMPT = """Utilizza esclusivamente le informazioni contenute nel contesto fornito per generare una risposta alla domanda riformulando il contenuto 
                        del contesto fornito in circa 80 parole.

                        - usa le informazioni del contesto per costruire una risposta aderente alla domanda.
                        - Se il contesto non è sufficiente per rispondere, dichiara che non hai abbastanza informazioni.
                        - Non aggiungere informazioni inventate o non presenti nel contesto.
    
                        contesto: {context}
    
                        domanda: {question}
                        
                        risposta: """

    #prompt = input("\nCiao! mi chiamo Marianna e se vuoi sapere qualcosa su storia e archeologia della città Napoli ti posso aiutare!\n"
                  #"Fammi una domanda e farò del mio meglio per risponderti!\n\n"
                   #"domanda: ")
    
    best_ids = search(query)

    full_context = best_context(best_ids)


    response = ollama.chat(
    model="llama3.2",
    messages=[ 
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": CONTEXT_PROMPT.format(context=full_context, question=query)}
        ]
    )

    
    return full_context, response["message"]["content"]
    


with open('/home/filippo/Scrivania/Marianna_head/evaluation_queries.pkl', 'rb') as file:
    all_queries = pickle.load(file)


all_best_contexts = []
all_responses = []

for q in all_queries:
    results = Marianna_head(q)
    all_best_contexts.append(results[0])
    all_responses.append(results[-1])


data_eval = {'query': all_queries,
             'testo_recuperato': all_best_contexts,
             'testo_generato': all_responses}


df_eval = pd.DataFrame(data_eval)

df_eval.to_csv('/home/filippo/Scrivania/Marianna_head/evaluation_results.tsv', sep='\t', index=False, encoding='utf-8')
