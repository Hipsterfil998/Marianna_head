import pickle
import pandas as pd
import ast


df = pd.read_csv("/home/filippo/Scrivania/Marianna_head/wiki_naples_expanded_hyper.tsv", sep="\t")



def dictionary_formatter(data):
        """
        Converte un dataframe in una lista di dizionari nel formato {'title': title, 'text': text}.

        :param data: DataFrame di input.
        :return: Lista di dizionari formattati.
        """
        formatted_data = []
        all_titles = []

        for summary, title, content, url in zip(data['summary'],data['title'], data['content'], data['url']):
            all_titles.append(title)
            intro_page = {"intro": summary}
            contents = {'further_info': {}}
            try:
                content_dict = ast.literal_eval(content)
                for key, value in content_dict.items():
                    if key not in ['Voci correlate', 'Collegamenti esterni','Altri progetti','Note', 'Bibliografia']:
                        if isinstance(value, str) and value != '':
                            contents['further_info'][f"{key}"] = ' '.join(value.split('\n'))
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if sub_key not in ['Voci correlate', 'Collegamenti esterni','Altri progetti','Note', 'Bibliografia'] and sub_value != '':
                                    contents['further_info'][f"{sub_key}"] = ' '.join(sub_value.split('\n'))
            except (ValueError, SyntaxError) as e:
                print(f"Errore nella conversione del contenuto per il titolo '{title}': {e}")

            intro_page.update(contents)
            formatted_data.append(intro_page)

        return formatted_data, all_titles

all_dicts = dictionary_formatter(df)[0]
all_tits = dictionary_formatter(df)[-1]

dict_tits = list(zip(all_tits, all_dicts))

with open("dati_per_database.pkl", "wb") as file:
    pickle.dump(dict_tits, file)


#ddd = all_dicts[0]

#first_key = list(ddd.keys())[0]

# Ottenere il valore di 'further_info'
#further_info = ddd.get('further_info')

# print("First key:", first_key)
# print("Further info:", further_info)
#origini_nome = ddd['further_info'].get('Origini del nome')
#print(origini_nome)

# all_dicts_clean = [el for el in all_dicts if el['text'] != '']

# print(len(all_dicts_clean)) 

# pickle.dump(all_dicts_clean, open('/home/filippo/Scrivania/Marianna_head/database/wiki_naples.pkl', 'wb'))

