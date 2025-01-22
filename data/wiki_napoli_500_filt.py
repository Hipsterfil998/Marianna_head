import pandas as pd
import pickle
from tqdm import tqdm
import ollama

df = pd.read_csv('/home/filippo/Scrivania/Marianna_head/wiki_naples_500.tsv', sep='\t') 

titles = df.drop_duplicates()['title'].tolist()


def title_filter(tit):

    SYSTEM_PROMPT = """Sei un moderatore di contenuti e il tuo compito è quello di filtrare i contenuti in base alle indicazioni che ti vengono fornite.
                    Classifica con una label. il formato dell'output è la sola etichetta"""

    INSTRUCTION_PROMPT = """Ti viene presentato il titolo di un testo breve. Il tuo compito è quello di individuare se il titolo ha a che fare con la città di Napoli
                            nelle seguenti categorie:

                            - archeologia
                            - storia antica (greca e romana) e moderna
                            - geografia
                            - turismo
                            - folklore 

                            Le informazioni possono essere direttamente su Napoli o può essere parzialmente citata.
                            Le categorie possono essere presenti singolarmente o in combinazioni.
                            Dai un unico giudizio complessivo, è sufficiente entrare ad in una categoria per considerare il titolo rilevante.
                            Condidera non rilevanti personaggi dello spettacolo (musica, tv e cinema) e dello sport (calcio), cronaca nera recente, 
                            indagini o contenuti offensivi anche se appartenenti a Napoli.

                            L'etichetta positiva è RILEVANTE
                            L'etichetta negativa è NON RILEVANTE"""

    PROMPT = """Analizza il contenuto del titolo {titolo} e classifica il suo contenuto in base alle indicazioni con l'etichetta opportuna."""



    response = ollama.chat(
    model="llama3.2",
    messages = [
      {"role": "system", "content": SYSTEM_PROMPT},
      {"role": "user", "content": INSTRUCTION_PROMPT},
      {"role": "user", "content": PROMPT.format(titolo=tit)}
]
    )

    
    return response["message"]["content"]



titles_filtered = [title_filter(el) for el in tqdm(titles, desc="Processing paragraphs")]

with open('/home/filippo/Scrivania/Marianna_head/marianna_head/labels_filtered_500.pkl', "wb") as file:
    pickle.dump(titles_filtered, file)

    

