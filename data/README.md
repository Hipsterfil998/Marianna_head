# Datasets

This folder contains datasets related to Naples (Napoli), Italy, derived from Wikipedia. 

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

---

These datasets, specifically wiki_naples_expanded_hyper.tsv, have been used to provide a knowledge base for the talking head "Marianna". This application demonstrates the practical use of the curated data in creating an interactive and informative virtual agent focused on Naples-related topics.
