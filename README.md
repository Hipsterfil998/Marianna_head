# Talking Head: Marianna

Marianna is an Italian virtual agent designed to share the rich cultural heritage, fascinating history, and captivating legends of Naples, Italy. Through interactive conversations, she brings to life the stories that have shaped Naples, one of the world's most ancient cities.

<img src="Testa_di_Marianna/app_images/schemata_app.png" alt="Chat con Marianna - La Testa di Napoli"/>

## The Story Behind the Name

Our virtual guide takes her name from a fascinating piece of Neapolitan history known as "Donna Marianna 'a cap'e Napule" (Donna Marianna, the head of Naples). In the 17th century, a large marble head of a woman was discovered in the Piazza Mercato area. This remarkable find was documented in Carlo Celano's 1692 work "Notizie del bello, dell'antico e del curioso della città di Napoli" (News of the beautiful, the ancient, and the curious of the city of Naples), where it was identified as the head of the mythical Siren Parthenope.

The people of Naples affectionately named this artifact "'a cap'e Napule," and it became a beloved symbol of the city's rich historical and mythological heritage. Today, this impressive marble head is preserved in Palazzo San Giacomo, Naples' City Hall, where it continues to inspire and connect present-day Naples with its ancient past.

## Features

- Interactive conversational interface using Gradio
- Knowledge base powered by BerkeleyDB
- Integration with Ollama for natural language processing
- Support for sharing historical facts and legends about Naples
- User-friendly chat interface with image display
- Easy-to-use reset functionality
- Example queries for better user engagement

## Prerequisites

- Python 3.10.12
- Gradio
- BerkeleyDB
- Ollama

## Installation

1. Clone the repository:
```bash
https://github.com/RaffaeleMann/Marianna_head.git
cd Marianna_head
```

2. Install the required dependencies:
```bash
pip install gradio berkeleydb ollama
```

3. Set up the database paths in the code:
- Update the database paths in `Marianna_head` class initialization to match your system configuration
- Ensure the image path for Marianna's portrait is correctly set

## Usage

1. Start the chatbot:
```bash
Testa_di_Marianna/gradio_app.py
```

2. Access the web interface through your browser at `http://localhost:7860`

3. Interact with Marianna by:
- Responding to her welcome message with 'sì', 'no', or 'raccontami tu qualcosa'
- Asking questions about Naples' history and culture
- Using the example queries provided in the interface


## Contributing

Contributions are welcome! Feel free to:
- Add new historical facts and legends to the databases
- Improve the conversation flow
- Enhance the user interface
- Fix bugs and improve code quality

Please submit pull requests for any improvements you'd like to contribute.

## License

This project is licensed under the MIT License. For details, see the LICENSE file. Please note that this is a change from the previous license, and it's important to review the terms and conditions of the new license.

## Acknowledgments

- The city of Naples for preserving this important cultural artifact
- All contributors who help maintain and improve this project
