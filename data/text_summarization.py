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
    Converte i numeri romani in testo italiano utilizzando una mappatura predefinita.
    Copre i numeri da I a XXX e gestisce abbreviazioni comuni.
    
    Args:
        testo (str): Il testo contenente numeri romani e abbreviazioni da convertire
        
    Returns:
        str: Il testo con i numeri romani convertiti in parole e abbreviazioni sostituite
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
    
    # regex pattern to capture all roman numbers from I to XXX
    pattern = r'\b(?:XXX|XX|XX(?:IX|VIII|VII|VI|V|IV|III|II|I)|X(?:IX|VIII|VII|VI|V|IV|III|II|I)|IX|VIII|VII|VI|V|IV|III|II|I)\b'
    
    def sostituisci(match):
        numero_romano = match.group(0)
        return map.get(numero_romano, numero_romano)
    
    # abbreviation substitution (ordered by decreasing length)
    for abbreviazione, sostituto in sorted(map_abbreviazioni.items(), key=lambda x: -len(x[0])):
        testo = testo.replace(abbreviazione, sostituto)
    
    # roman numbers conversion
    testo = re.sub(pattern, sostituisci, testo)
    
    # isolted m conversion
    testo = re.sub(r'(?<!\d)\bm\b', "metri", testo)

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

df = pd.read_csv("/home/filippo/Scrivania/Marianna_head/wiki_naples_expanded_hyper.tsv", sep="\t")

relevant = filter_relevant_titles("/home/filippo/Scrivania/Marianna_head/database/titoli_pagina_annotati.tsv")

df_filt = df[df['title'].isin(relevant)]

##format dictionaries

formatter = dictionary_formatter(df_filt)

##save as pickle file 

with open("/home/filippo/Scrivania/Marianna_head/database/dati_per_database_riassunti.pkl", "wb") as file:
    pickle.dump(formatter, file)