import os
import datetime
from json import load, dump
from dotenv import dotenv_values

# Load Environment Variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = "Prism"
CerebrasAPIKey = env_vars.get("CerebrasAPIKey")
CohereAPIKey = env_vars.get("CohereAPIKey")

# --- Initialize Clients ---
cerebras_client = None
cohere_client = None

# Try Initializing Cerebras
try:
    from cerebras.cloud.sdk import Cerebras
    if CerebrasAPIKey:
        cerebras_client = Cerebras(api_key=CerebrasAPIKey)
except Exception as e:
    print(f"⚠️ Cerebras Client Warning: {e}")

# Try Initializing Cohere (Backup)
try:
    import cohere
    if CohereAPIKey:
        cohere_client = cohere.Client(api_key=CohereAPIKey)
except Exception as e:
    print(f"⚠️ Cohere Client Warning: {e}")

# --- System Prompt ---
System = f"""You are Prism, an advanced AI assistant for {Username}.
- Provide concise, accurate responses
- Use natural, conversational language
- Don't mention your training data or limitations
- Reply in English only
- Be helpful and direct"""

# Ensure Data directory exists
if not os.path.exists("Data"):
    os.makedirs("Data")

# Initialize ChatLog
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
        if len(messages) > 10:
            messages = messages[-10:]
except (FileNotFoundError, ValueError):
    messages = []
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f)

def RealtimeInformation():
    now = datetime.datetime.now()
    return f"Current time: {now.strftime('%I:%M %p')}, Date: {now.strftime('%A, %B %d, %Y')}"

def AnswerModifier(Answer):
    lines = [line for line in Answer.split('\n') if line.strip()]
    return '\n'.join(lines).strip()

def ChatBot(Query):
    """
    Process query with Automatic Fallback:
    1. Cerebras (Llama 3.3) -> Fastest/Best
    2. Cohere (Command-R) -> Reliable Backup
    """
    global cerebras_client, cohere_client, messages
    
    # Update History
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
    except:
        messages = []

    messages.append({"role": "user", "content": Query})
    if len(messages) > 10: messages = messages[-10:]

    Answer = ""
    used_provider = "None"

    # --- ATTEMPT 1: CEREBRAS ---
    try:
        if not cerebras_client: raise Exception("Client not initialized")
        
        completion = cerebras_client.chat.completions.create(
            model="llama-3.3-70b",
            messages=[{"role": "system", "content": System + f"\n{RealtimeInformation()}"}] + messages,
            max_tokens=512,
            temperature=0.7,
            top_p=0.95,
            stream=True
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        
        used_provider = "Cerebras"

    except Exception as e1:
        print(f"❌ Cerebras Failed: {e1}")
        print("🔄 Switching to Fallback (Cohere)...")
        
        # --- ATTEMPT 2: COHERE (FALLBACK) ---
        try:
            if not cohere_client:
                # Re-init if needed
                import cohere
                cohere_client = cohere.Client(api_key=CohereAPIKey)

            # Convert format for Cohere
            chat_history = []
            for msg in messages[:-1]: # Exclude current query
                if msg["role"] == "user":
                    chat_history.append({"role": "USER", "message": msg["content"]})
                elif msg["role"] == "assistant":
                    chat_history.append({"role": "CHATBOT", "message": msg["content"]})

            response = cohere_client.chat(
                model="command-r-plus-08-2024",
                message=Query,
                chat_history=chat_history,
                preamble=System + f"\n{RealtimeInformation()}",
                temperature=0.7
            )
            Answer = response.text
            used_provider = "Cohere"

        except Exception as e2:
            print(f"❌ Cohere Failed: {e2}")
            return "I apologize, but I'm having trouble connecting to the servers right now. Please check your internet or API keys."

    # --- FINAL PROCESSING ---
    Answer = Answer.replace("</s>", "").strip()
    Answer = Answer.replace("P.R.I.S.M", "Prism").replace("PRISM", "Prism")
    
    # Save History
    messages.append({"role": "assistant", "content": Answer})
    if len(messages) > 10: messages = messages[-10:]
    
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=2)

    return AnswerModifier(Answer)

if __name__ == "__main__":
    print("Prism Chat System (with Fallback)")
    while True:
        q = input("You: ")
        if q.lower() == "exit": break
        print(f"Prism: {ChatBot(q)}")