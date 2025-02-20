import gradio as gr
import random
import berkeleydb
import pickle
import re 


class MariannaBot:
    def __init__(self):
        self.database = berkeleydb.hashopen("/home/filippo/Scrivania/Marianna_head/Marianna_testa/database/wiki_napoli_main.db", flag="w")
        self.database_legends = berkeleydb.hashopen("/home/filippo/Scrivania/Marianna_head/Marianna_testa/database/wiki_naples_leggende.db", flag="w")
        self.reset_state()
    
    def reset_state(self):
        self.state = "initial"
        self.welcome_sent = False
        self.current_further_info_values = []
        self.current_index = 0
        self.main_k = []
        self.is_telling_stories = False
    
    def get_welcome_message(self):
        return """Ciao, benvenuto!\n\nSono Marianna, la testa di Napoli, in napoletano 'a capa 'e Napule, una statua ritrovata per caso nel 1594. \nAll'epoca del mio ritrovamento, si pensò che fossi una rappresentazione della sirena Partenope, dalle cui spoglie, leggenda narra, nacque la città di Napoli. In seguito, diversi studiosi riconobbero in me una statua della dea Venere, probabilmente collocata in uno dei tanti templi che si trovavano nella città in epoca tardo-romana, quando ancora si chiamava Neapolis.
        \nPosso raccontarti molte storie sulla città di Napoli e mostrarti le sue bellezze. \nC'è qualcosa in particolare che ti interessa?
        \n(Rispondi con 'sì', 'no' o 'non so')"""
    
    def get_safe_example_keys(self, num_examples=3):
        """Safely get example keys from the database."""
        try:
            keys = list(self.database.keys())
            if not keys:
                return []
            return random.sample(keys, min(len(keys), num_examples))
        except Exception:
            return []
    
    def story_flow(self):
        """Handle random story selection from legends database"""
        try:
            legend_keys = list(self.database_legends.keys())
            if not legend_keys:
                return "Mi dispiace, al momento non ho leggende da raccontare."
            
            # Se abbiamo già raccontato tutte le storie, ricominciamo
            available_keys = [key for key in legend_keys if key.decode('utf-8') not in self.main_k]
            if not available_keys:
                self.main_k = []  # Reset della lista delle storie raccontate
                available_keys = legend_keys
            
            random_key = random.choice(available_keys)
            topic = random_key.decode('utf-8')
            content = self.database_legends[random_key].decode('utf-8')
            
            self.main_k.append(topic)
            self.state = "follow_up"
            self.is_telling_stories = True
            
            return f"Ok, lascia che ti racconti de {topic}.\n\n{content}\n\nVuoi che ti racconti un'altra storia? (sì/no)"
        except Exception:
            self.state = "initial"
            self.is_telling_stories = False
            return "Mi dispiace, c'è stato un problema nel recuperare la storia. Vuoi provare con qualcos'altro? (sì/no)"

    def handle_query(self, message):
        """Handle user queries by searching the database"""
        try:
            for key, value in self.database.items():
                decoded_key = key.decode("utf-8").lower()
                if message == decoded_key:
                    self.main_k.append(key.decode("utf-8"))
                    self.state = "follow_up"
                    self.is_telling_stories = False
                    deserialized_value = pickle.loads(value)
                    response = deserialized_value['intro']
                    self.current_further_info_values = list(deserialized_value.get('further_info', {}).values())
                    self.current_index = 0
                    return f"{response}\n\nVuoi sapere altro su {self.main_k[-1]}? (sì/no)"
            return "Mi dispiace, non ho informazioni riguardo a questa domanda. Prova a chiedermi qualcos'altro sulla città di Napoli."
        except Exception:
            self.state = "initial"
            return "Mi dispiace, c'è stato un errore. Puoi riprovare con un'altra domanda?"

    def respond(self, message, history):
        if not message:
            return "Mi dispiace, non ho capito. Potresti ripetere?"
        
        message = message.lower().strip()

        if self.state == "initial":
            if message in ["sì", "si"]:
                self.state = "query"
                self.is_telling_stories = False
                return "Potresti dirmi di cosa vorresti sapere?"
            elif message == "no":
                self.state = "end"
                return "Va bene, grazie per aver parlato con me."
            elif message == "non so":
                return self.story_flow()
            else:
                return "Scusa, non ho capito. Puoi rispondere con 'sì', 'no' o 'non so'."

        elif self.state == "query":
            return self.handle_query(message)

        elif self.state == "follow_up":
            if message in ["sì", "si"]:
                if self.is_telling_stories:
                    return self.story_flow()
                elif self.current_further_info_values and self.current_index < len(self.current_further_info_values):
                    value = self.current_further_info_values[self.current_index]
                    self.current_index += 1
                    
                    if self.current_index < len(self.current_further_info_values):
                        return f"{value}\n\nVuoi sapere altro su {self.main_k[-1]}? (sì/no)"
                    else:
                        self.state = "initial"
                        return f"{value}\n\nNon ho altre informazioni su {self.main_k[-1]}. Ti interessa qualcos'altro? (sì/no)"
                else:
                    self.state = "initial"
                    return f"Non ho altre informazioni su {self.main_k[-1]}. Ti interessa qualcos'altro? (sì/no)"
            
            elif message == "no":
                self.state = "initial"
                self.is_telling_stories = False
                return "C'è qualcos'altro che ti interessa? (sì/no)"
            else:
                return "Scusa, non ho capito. Puoi rispondere con 'sì' o 'no'."
        
        return "Mi dispiace, non ho capito. Potresti ripetere?"

def main():
    bot = MariannaBot()

    def update_chatbot(message, history):
        if not message.strip():
            return history, ""
        response = bot.respond(message, history)
        return history + [{"role": "user", "content": message}, {"role": "assistant", "content": response}], ""
    
    def reset_chat():
        bot.reset_state()
        return [{"role": "assistant", "content": bot.get_welcome_message()}], ""
    
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue")) as demo:
        with gr.Row():
            gr.Markdown("## Chat con Marianna - 'La Testa di Napoli'")
            
        with gr.Row():
            gr.Image("/home/filippo/Scrivania/Marianna_head/Marianna_testa/marianna-102.jpeg", 
                    elem_id="marianna-image", 
                    width=250)
            
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

        # Get example keys safely
        example_keys = bot.get_safe_example_keys()
        if example_keys:
            examples = [key.decode('utf-8') for key in example_keys]
            gr.Examples(
                examples=examples,
                inputs=msg
            )

    demo.launch(share=False)

if __name__ == "__main__":
    main()