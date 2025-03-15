from llama_cpp import Llama
import pandas as pd
import pickle
import ast
import re

def filter_relevant_titles(tsv_file):
    """
    Legge un file TSV e restituisce solo i titoli marcati come pertinenti (P)
    usando pandas.
    
    Args:
        tsv_file (str): Percorso del file TSV da processare
        
    Returns:
        list: Lista dei titoli pertinenti
    """
    # read file TSV
    df = pd.read_csv(tsv_file, sep='\t')
    
    # Filter 'P' in column 'pertinenza'
    relevant_titles = df[df['pertinenza'] == 'P']['titolo_pagina'].tolist()
    
    return relevant_titles

def convert_roman_numbers(testo):
    """
    Converte i numeri romani in testo italiano e gestisce le abbreviazioni comuni.
    Rimuove 'primo' all'inizio delle frasi quando è seguito da una parola.
    
    Args:
        testo (str): Il testo contenente numeri romani e abbreviazioni da convertire
        
    Returns:
        str: Il testo convertito con 'primo' rimosso all'inizio delle frasi
    """
    # roman numbers mapping
    map = {
        "I": "primo", "II": "secondo", "III": "terzo", "IV": "quarto", "V": "quinto",
        "VI": "sesto", "VII": "settimo", "VIII": "ottavo", "IX": "nono", "X": "decimo",
        "XI": "undicesimo", "XII": "dodicesimo", "XIII": "tredicesimo", "XIV": "quattordicesimo",
        "XV": "quindicesimo", "XVI": "sedicesimo", "XVII": "diciassettesimo", "XVIII": "diciottesimo",
        "XIX": "diciannovesimo", "XX": "ventesimo", "XXI": "ventunesimo", "XXII": "ventiduesimo",
        "XXIII": "ventitreesimo", "XXIV": "ventiquattresimo", "XXV": "venticinquesimo",
        "XXVI": "ventiseiesimo", "XXVII": "ventisettesimo", "XXVIII": "ventottesimo",
        "XXIX": "ventinovesimo", "XXX": "trentesimo"
    }

    # words to exclude from conversion
    parole_da_escludere = ["vomero", "volume", "volare", "vulcano", "veneto", "venire"]
    
    # abbreviations mapping
    map_abbreviazioni = {
        "a.C.": "avanti Cristo",
        "d.C.": "dopo Cristo",
        "km²": "chilometri quadrati",
        "m²": "metri quadrati",
        "km": "chilometri",
        "ab./km²": "abitanti per chilometro quadrato",
        "n.": "numero",
        "SS.": "santissimo"
    }
    
    def processa_numero_romano(match):

        numero_romano = match.group(1)
        parola_seguente = match.group(2).lower() if match.group(2) else ""
        
        # verify match is not part of a word
        match_completo = match.group(0).lower()
        for parola in parole_da_escludere:
            if match_completo.startswith(parola) or (numero_romano.lower() + parola_seguente.lower() == parola):
                return match.group(0)
        
        
        if parola_seguente in ["secolo", "secoli"]:
            return map.get(numero_romano, numero_romano) + " " + parola_seguente
        
    
        if numero_romano == "I":
            return match.group(0)
            
        return map.get(numero_romano, numero_romano) + (" " + parola_seguente if parola_seguente else "")
    
    # substituting abbreviations
    for abbreviazione, sostituto in sorted(map_abbreviazioni.items(), key=lambda x: -len(x[0])):
        testo = testo.replace(abbreviazione, sostituto)
    
    # pattern to match roman numbers
    pattern = r'\b((?:XXX|XX|XX(?:IX|VIII|VII|VI|V|IV|III|II|I)|X(?:IX|VIII|VII|VI|V|IV|III|II|I)|IX|VIII|VII|VI|V|IV|III|II|I))\s+(\w+)?\b'
    
    # Convert roman numbers
    testo = re.sub(pattern, processa_numero_romano, testo)
    
    # Convert isolated "m" to "metri"
    testo = re.sub(r'(?<!\d)\bm\b', "metri", testo)
    
    # remove 'primo' at the beginning of sentences
    pattern_primo = r'(?:^|(?<=\.\s))primo\s+'
    testo = re.sub(pattern_primo, '', testo)

    pattern_quinto = r'(?:^|(?<=\.\s))quinto\s+'
    testo = re.sub(pattern_quinto, '', testo)
    
    return testo
    

def reformulation(text):


    PROMPT = """ <|start_header_id|>user<|end_header_id|> contesto: {contesto}
    
                Utilizza esclusivamente le informazioni contenute nel contesto fornito per riformulare il testo in circa 80 parole.
                Assicurati che la riformulazione sia chiara e concisa, mantenendo il significato originale. Ti rivolgi ad un pubblico di non esperti.
                Non mettere nell'output informazioni tra parentesi tonde.
                Nell'output controlla che non ci siano errori grammaticali. Se trovi errori correggili.
                Non aggiungere informazioni che non sono presenti nel testo originale.
                Nell'output non dire mai che stai riassumendo il testo. <|eot_id|>"""
                
    llm = Llama(
        model_path="/home/filippo/Scrivania/Marianna_head/database/Llama-3.2-3B-Instruct-Q4_K_M.gguf", #change with your path; check model repo for info
        chat_format="llama-3",
        verbose=False,
        n_ctx=8192,
        silent=True
    )
    response = llm.create_chat_completion(
        messages = [
            {"role": "system", "content": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>Sei una guida turistica per una mostra. "
            "Il tuo compito è riassumere e semplificare delle informazioni per un pubblico di non esperti. <|eot_id|>"},
            {"role": "user", "content": PROMPT.format(contesto=text)},
            {"role": "assistant", "content": "Per chi non è esperto della materia, ecco come possiamo spiegare questo tema: " }
        ],
        temperature = 0.1,  # low temperature for more conservative outputs
        max_tokens =  250    # Limited to 250 tokens (enough for ~80 words)
    )

    return response["choices"][0]["message"]["content"]


def dictionary_formatter(data):
        """
        Converte un dataframe in una lista di dizionari nel formato {'title': title, 'text': text}.

        :param data: DataFrame di input.
        :return: Lista di dizionari formattati.
        """
        formatted_data = []
        all_titles = []

        for summary, title, content in zip(data['summary'],data['title'], data['content']):
            if title not in all_titles:
                all_titles.append(title)
                intro_page = {"intro": convert_roman_numbers(reformulation(re.sub(r'\(.*?\)', '', summary).strip()))}
                contents = {'further_info': {}}
                try:
                    content_dict = ast.literal_eval(content)
                    for key, value in content_dict.items():
                        if key not in ['Voci correlate', 'Collegamenti esterni','Altri progetti','Note', 'Bibliografia']:
                            if isinstance(value, str) and value != '':
                                contents['further_info'][f"{key}"] = convert_roman_numbers(reformulation(re.sub(r'\(.*?\)', '', ' '.join(value.split('\n'))).strip()))
                            elif isinstance(value, dict):
                                for sub_key, sub_value in value.items():
                                    if sub_key not in ['Voci correlate', 'Collegamenti esterni','Altri progetti','Note', 'Bibliografia'] and sub_value != '':
                                        contents['further_info'][f"{sub_key}"] = convert_roman_numbers(reformulation(re.sub(r'\(.*?\)', '', ' '.join(sub_value.split('\n'))).strip()))
                except (ValueError, SyntaxError) as e:
                    print(f"Errore nella conversione del contenuto per il titolo '{title}': {e}")

                intro_page.update(contents)
                formatted_data.append(intro_page)
                
            else:
                pass
            
        return list(zip(all_titles, formatted_data))

##filter relevant titles

df = pd.read_csv("/home/filippo/Scrivania/Marianna_head/wiki_naples_expanded_hyper_2.tsv", sep="\t") #change with your path

relevant = filter_relevant_titles("/home/filippo/Scrivania/Marianna_head/database/titoli_pagina_annotati.tsv") #change with your path

df_filt = df[df['title'].isin(relevant)]

##format dictionaries

formatter = dictionary_formatter(df_filt)

#save as pickle file 

with open("/home/filippo/Scrivania/Marianna_head/database/dati_riassunti_new.pkl", "wb") as file: #change with your path
    pickle.dump(formatter, file)
