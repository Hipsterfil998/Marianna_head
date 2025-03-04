import ollama
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

    # Lista di parole da escludere dal riconoscimento romano
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
        
        # Verifica se il match è una delle parole da escludere
        match_completo = match.group(0).lower()
        for parola in parole_da_escludere:
            if match_completo.startswith(parola) or (numero_romano.lower() + parola_seguente.lower() == parola):
                return match.group(0)  # Mantieni il testo originale
        
        # Se è seguito da "secolo" o "secoli", converti il numero
        if parola_seguente in ["secolo", "secoli"]:
            return map.get(numero_romano, numero_romano) + " " + parola_seguente
        
        # Se è un singolo "I" non seguito da "secolo/secoli", mantienilo come articolo
        if numero_romano == "I":
            return match.group(0)
            
        # Altrimenti converti il numero romano
        return map.get(numero_romano, numero_romano) + (" " + parola_seguente if parola_seguente else "")
    
    # Sostituisci prima le abbreviazioni (ordinate per lunghezza decrescente)
    for abbreviazione, sostituto in sorted(map_abbreviazioni.items(), key=lambda x: -len(x[0])):
        testo = testo.replace(abbreviazione, sostituto)
    
    # Pattern che cattura il numero romano e la parola seguente (se presente)
    # Modificato per evitare di catturare parole che iniziano con numeri romani
    pattern = r'\b((?:XXX|XX|XX(?:IX|VIII|VII|VI|V|IV|III|II|I)|X(?:IX|VIII|VII|VI|V|IV|III|II|I)|IX|VIII|VII|VI|V|IV|III|II|I))\s+(\w+)?\b'
    
    # Aggiungi uno spazio tra il numero romano e la parola seguente per evitare di catturare parole come "Vomero"
    
    # Converti i numeri romani
    testo = re.sub(pattern, processa_numero_romano, testo)
    
    # Converti le 'm' isolate
    testo = re.sub(r'(?<!\d)\bm\b', "metri", testo)
    
    # Rimuovi "primo" all'inizio delle frasi
    # Questo pattern cerca "primo" all'inizio della stringa o dopo un punto seguito da spazi
    pattern_primo = r'(?:^|(?<=\.\s))primo\s+'
    testo = re.sub(pattern_primo, '', testo)

    pattern_quinto = r'(?:^|(?<=\.\s))quinto\s+'
    testo = re.sub(pattern_quinto, '', testo)
    
    return testo
    

def reformulation(text):
    
    PROMPT = """Utilizza esclusivamente le informazioni contenute nel contesto fornito per riformulare il testo in circa 80 parole.
                Assicurati che la riformulazione sia chiara e concisa, mantenendo il significato originale. Ti rivolgi ad un pubblico di non esperti.
                Non mettere nell'output informazioni tra parentesi tonde.
                Nell'output controlla che non ci siano errori grammaticali. Se trovi errori correggili.
                Non aggiungere informazioni che non sono presenti nel testo originale.
                Nell'output non dire mai che stai riassumendo il testo.
                
                testo: {context}

                output: """


    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "user", "content": PROMPT.format(context=text)}
        ]
    )
    return response["message"]["content"]


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

df = pd.read_csv("/home/filippo/Scrivania/Marianna_head/wiki_naples_expanded_hyper_2.tsv", sep="\t")

relevant = filter_relevant_titles("/home/filippo/Scrivania/Marianna_head/database/titoli_pagina_annotati.tsv")

df_filt = df[df['title'].isin(relevant)]

##format dictionaries

formatter = dictionary_formatter(df_filt)

##save as pickle file 

with open("/home/filippo/Scrivania/Marianna_head/database/dati_riassunti_new.pkl", "wb") as file:
    pickle.dump(formatter, file)
