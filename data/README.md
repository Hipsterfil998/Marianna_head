# Datasets

This folder contains datasets related to Naples (Napoli), Italy, derived from Wikipedia and the website Napoli nei Particolari

## 1. napoli_wiki_seed_link.tsv

This file contains manually selected seed URLs used as the foundation for building the subsequent datasets. These URLs serve as starting points for the data collection process, ensuring a focused and relevant initial set of information about Naples.

## 2. wiki_naples.tsv

This dataset contains information extracted from the seed URLs. It includes the following headers for each entry:

- **summary**: A brief overview of the topic
- **title**: The title of the Wikipedia page
- **url**: The URL of the Wikipedia page
- **content**: The main text content of the page
- **links**: Hyperlinks found within the page

## 3. wiki_naples_expanded_hyper.tsv

This is the final, expanded version of the dataset. It includes entries for all objects that have hyperlink connections to the pages contained in wiki_naples.tsv. The structure is similar to wiki_naples.tsv, with the same headers:

- summary
- title
- url
- content
- links

This dataset has been cleaned and refined to remove elements not specific to the project, such as mentions of other Greek cities or cities in Magna Graecia, as well as personalities only tangentially related to Naples. This curation process ensures that the dataset remains focused on Naples-specific information.

## 4. wiki_naples_500.tsv

This is an expanded version of wiki_naples.tsv. The dataset starts from a seed of 500 links related to the city of Naples. This file contains the following headers:

- summary
- title
- url
- content
- links

## 5. wiki_naples_500_hyper.tsv

This is an expanded version of wiki_naples.tsv. The dataset includes entries for all objects that have hyperlink connections to the pages contained in wiki_naples_500.tsv. This file contains the following headers:

- summary
- title
- url
- content
- links

For memory issues you can download this file at the following google drive link: https://drive.google.com/file/d/1-BktWHlb87SJu8dKonufgauKPx2Q0OMJ/view?usp=sharing 
The file weights 700 MB and contains about 40000 wiki pages extracted from the 'links' section of wiki_naples_500.tsv

## 6. napoli_particolari_luoghi.tsv

This is a dataset extracted from the "places" section from the website Napoli nei Particolari (https://napolineiparticolari.altervista.org/). It contains the following headers:

- title
- text
- url

## 7. napoli_particolari_storia.tsv

This is a dataset extracted from the "history" section from the website Napoli nei Particolari (https://napolineiparticolari.altervista.org/). It contains the following headers:

- title
- text
- url

## 8. napoli_particolari_leggende.tsv

This is a dataset extracted from the "legends" section from the website Napoli nei Particolari (https://napolineiparticolari.altervista.org/). It contains the following headers:

- title
- text
- url

---

These datasets, specifically wiki_naples_expanded_hyper.tsv, have been used to provide a knowledge base for the talking head "Marianna". This application demonstrates the practical use of the curated data in creating an interactive and informative virtual agent focused on Naples-related topics.
