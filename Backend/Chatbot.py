import os
import datetime
from json import load, dump
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
CerebrasAPIKey = env_vars.get("CerebrasAPIKey")

# Initialize Cerebras client with error handling
client = None
try:
    from cerebras.cloud.sdk import Cerebras
    client = Cerebras(api_key=CerebrasAPIKey)
except Exception as e:
    print(f"Warning: Cerebras client initialization failed: {e}")
    print("ChatBot will attempt to reinitialize on first use.")

# System prompt definition
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Ensure Data directory exists
if not os.path.exists("Data"):
    os.makedirs("Data")

# Initialize ChatLog
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except (FileNotFoundError, ValueError):
    messages = []
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

def RealtimeInformation():
    now = datetime.datetime.now()
    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {now.strftime('%A')}\nDate: {now.strftime('%d')}\nMonth: {now.strftime('%B')}\nYear: {now.strftime('%Y')}\n"
    data += f"Time: {now.strftime('%H')} hours :{now.strftime('%M')} minutes"
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def ChatBot(Query):
    """ Sends the query to Cerebras and returns the AI's response. """
    global client
    
    try:
        # Reinitialize client if needed
        if client is None:
            from cerebras.cloud.sdk import Cerebras
            client = Cerebras(api_key=CerebrasAPIKey)
        
        # Load existing chat log
        with open(r"Data\ChatLog.json", "r") as f:
            local_messages = load(f)

        local_messages.append({"role": "user", "content": f"{Query}"})

        # Request to Cerebras Cloud
        completion = client.chat.completions.create(
            model="llama-3.3-70b", 
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + local_messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        # Process streamed response
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        # Clean response and update history
        Answer = Answer.replace("</s>", "").strip()
        local_messages.append({"role": "assistant", "content": Answer})

        # Save updated log
        with open(r"Data\ChatLog.json", "w") as f:
            dump(local_messages, f, indent=4)

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        error_msg = f"Error in ChatBot: {str(e)}"
        print(error_msg)
        
        # Try to reset log on error
        try:
            with open(r"Data\ChatLog.json", "w") as f:
                dump([], f, indent=4)
        except:
            pass
            
        return "I encountered a technical error. Please try again or check your API configuration."

if __name__ == "__main__":
    print(f"System: {Assistantname} is now online.")
    while True:
        user_input = input("Enter Your Question: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Shutting down...")
            break
            
        response = ChatBot(user_input)
        print(f"{Assistantname}: {response}")