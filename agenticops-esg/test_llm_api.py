import os
import google.generativeai as genai

# ===== CONFIGURATION =====
# Make sure you have set the environment variable GEMINI_API_KEY
# e.g. in terminal: export GEMINI_API_KEY="your-new-key"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Choose your model (gemini-1.5-flash is free and fast)
MODEL_NAME = "gemini-1.5-flash"

# System prompt to shape the bot's personality
SYSTEM_PROMPT = (
    "You are a wise and practical decision advisor. "
    "Your goal is to help the user make informed choices. "
    "Ask clarifying questions if needed, weigh pros and cons, "
    "and always give a clear recommendation with reasoning. "
    "Be concise but thorough."
)

# ===== CHATBOT CLASS =====
class DecisionChatbot:
    def __init__(self):
        self.model = genai.GenerativeModel(MODEL_NAME)
        # We keep the conversation history as a list of messages
        # Each message: {"role": "user" or "model", "parts": [text]}
        self.history = [
            {"role": "user", "parts": [SYSTEM_PROMPT]},
            # Gemini expects a system instruction via the 'system_instruction' parameter,
            # but we can also inject it as the first user message and let the model adapt.
            # Better: use system_instruction when generating.
        ]
        # We'll store the full chat context for each turn
        self.chat = self.model.start_chat(history=[])

    def get_response(self, user_input):
        """Send user message, get bot response, and update history."""
        # Send the message with the system instruction included as context
        # We can use the 'system_instruction' parameter on the model,
        # but it's easier to prepend it to the chat history implicitly.
        # We'll append the user message to the chat and generate.
        response = self.chat.send_message(user_input)
        # The response object has .text
        return response.text

    def chat_loop(self):
        """Run an interactive chat session."""
        print("=" * 50)
        print("🤖 Decision Advisor Chatbot")
        print("Ask me about any decision (or type 'quit' to exit).")
        print("=" * 50)

        # Send an initial greeting (optional)
        initial_greeting = "Hello! I'm your decision advisor. What decision would you like to discuss today?"
        print(f"Bot: {initial_greeting}")

        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("Bot: Goodbye! Make wise decisions!")
                break
            if not user_input:
                continue

            try:
                response_text = self.get_response(user_input)
                print(f"Bot: {response_text}")
            except Exception as e:
                print(f"⚠️ Error: {e}. Please check your API key and network.")

# ===== MAIN =====
if __name__ == "__main__":
    bot = DecisionChatbot()
    bot.chat_loop()