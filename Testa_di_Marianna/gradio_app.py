import gradio as gr
import random
import berkeleydb
import ollama

def marianna_head(text):
    SYSTEM_PROMPT = """Sei un assistente virtuale per una mostra dedicata alla città di Napoli. 
                    Il tuo compito è dare risposte brevi ed esaustive utilizzando le informazioni contenute nel testo che ti viene fornito"""
    
    
    PROMPT = """Utilizza esclusivamente le informazioni contenute nel contesto fornito per riformulare il testo in circa 80 parole. 
                Assicurati che la riformulazione sia chiara e concisa, mantenendo il significato originale. 
                Non aggiungere informazioni che non sono presenti nel testo originale.

                testo: {context}

                riformulazione:"""


    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": PROMPT.format(context=text)}
        ]
    )
    return response["message"]["content"]

class MariannaBot:
    def __init__(self):
        self.database = berkeleydb.hashopen("/home/filippo/Scrivania/Marianna_head/Marianna_testa/database/wiki_naples.db", flag="w")
        self.database_legends = berkeleydb.hashopen("/home/filippo/Scrivania/Marianna_head/database/wiki_naples_leggende.db", flag="w")
        self.state = "initial"
        self.welcome_sent = False
        
    def get_welcome_message(self):
        return """Ciao, benvenuto!\n\nSono Marianna, la testa di Napoli, in napoletano ‘a capa ‘e napule, una statua ritrovata per caso nel 1594. \nAll’epoca del mio ritrovamento, si pensò che fossi una rappresentazione della sirena Partenope, dalle cui spoglie, leggenda narra, nacque la città di Napoli. In seguito, diversi studiosi riconobbero in me una statua della dea Venere, probabilmente collocata in uno dei tanti templi che si trovavano nella città in epoca tardo-romana, quando ancora si chiamava Neapolis.
        \nPosso raccontarti molte storie sulla città di Napoli e mostrarti le sue bellezze. \nC’è qualcosa in particolare che ti interessa?
        \n(Rispondi con 'sì', 'no' o 'raccontami tu qualcosa')"""

    def respond(self, message, history):
        message = message.lower().strip()

        if self.state == "initial":
            if message == "sì":
                self.state = "query"
                return "Potresti dirmi di cosa vorresti sapere?"
            elif message == "no":
                self.state = "end"
                return "Va bene, grazie per aver parlato con me."
            elif message == "raccontami tu qualcosa":
                if not self.database:  # Controlla se il database è vuoto
                    return "Mi dispiace, al momento non ho informazioni da raccontarti."

                # Se il database ha dati, sceglie un argomento casuale
                random_key = random.choice(list(self.database_legends.keys()))
                topic = random_key.decode('utf-8')
                content = self.database_legends[random_key].decode('utf-8')

                self.state = "follow_up"

                return f"Ok, lascia che ti racconti la leggenda de {topic}.\n\n{content}\n\nVuoi sapere altro? (sì/no)"
            else:
                return "Scusa, non ho capito. Puoi rispondere con 'sì', 'no' o 'raccontami tu qualcosa'."

        elif self.state == "query":
            for key, value in self.database.items():
                if key.decode("utf-8").lower() == message:
                    self.state = "follow_up"
                    response = marianna_head(value.decode("utf-8"))
                    return f"{response}\n\nVuoi sapere altro? (sì/no)"
            return "Mi dispiace, non ho informazioni riguardo a questa domanda. Prova a chiedermi qualcos'altro sulla città di Napoli."

        elif self.state == "follow_up":
            if message == "sì":
                self.state = "query"
                return "Ok, di cosa vorresti sapere?"
            elif message == "no":
                self.state = "end"
                return "Va bene, grazie per aver parlato con me."
            else:
                return "Scusa, non ho capito. Puoi rispondere con 'sì' o 'no'."


def main():
    bot = MariannaBot()

    # Estrai tre chiavi casuali dal database per gli esempi
    example_keys = random.sample(list(bot.database.keys()), 3)
    examples = [key.decode('utf-8') for key in example_keys]
    
    def update_chatbot(message, history):
        response = bot.respond(message, history)
        return history + [{"role": "user", "content": message}, {"role": "assistant", "content": response}], ""
    
    def reset_chat():
        bot.__init__()  # Reinizializza lo stato del bot
        return [{"role": "assistant", "content": bot.get_welcome_message()}], ""
    
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue")) as demo:
        with gr.Row():
            
            # Titolo
            gr.Markdown("## Chat con Marianna 'La Testa di Napoli'")
            
    
        with gr.Row():
            gr.Image("/home/filippo/Scrivania/Marianna_head/Marianna_testa/app_images/marianna-102.jpeg", elem_id="marianna-image", width=250)  # Aggiungi il percorso dell'immagine
            chatbot = gr.Chatbot(
                value=[{"role": "assistant", "content": bot.get_welcome_message()}],
                height=500,
                type="messages"
            )
        
        msg = gr.Textbox(
            placeholder="Scrivi il tuo messaggio qui...",
            container=False
        )
        
        with gr.Row():
            clear = gr.Button("Clicca qui per ricominciare")

        msg.submit(
            update_chatbot,
            [msg, chatbot],
            [chatbot, msg]  
        )

        clear.click(
            reset_chat,
            [],
            [chatbot, msg]

        )

        gr.Examples(
            examples=examples,
            inputs=msg
        )

    demo.launch(share=False)

if __name__ == "__main__":
    main()
