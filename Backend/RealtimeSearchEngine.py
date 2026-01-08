import datetime
import requests
from json import load, dump
from dotenv import dotenv_values
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
CerebrasAPIKey = env_vars.get("CerebrasAPIKey")
SerperAPIKey = env_vars.get("SerperAPIKey")

# Initialize client with error handling
client = None
try:
    from cerebras.cloud.sdk import Cerebras
    client = Cerebras(api_key=CerebrasAPIKey)
except Exception as e:
    print(f"Warning: Cerebras client initialization failed: {e}")
    print("RealtimeSearchEngine will attempt to reinitialize on first use.")

System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except (FileNotFoundError, Exception):
    if not os.path.exists("Data"):
        os.makedirs("Data")
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)
        messages = []

def GoogleSearch(query):
    url = "https://google.serper.dev/search"
    headers = {'X-API-KEY': SerperAPIKey, 'Content-Type': 'application/json'}
    payload = {"q": query}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json()
        Answer = f"The search results for '{query}' are:\n[start]\n"
        for i in results.get('organic', [])[:5]:
            title = i.get('title', 'No Title')
            snippet = i.get('snippet', 'No Description')
            Answer += f"Title: {title}\nDescription: {snippet}\n\n"
        Answer += "[end]"
        return Answer
    except Exception as e:
        return f"Search failed: {str(e)}"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    now = datetime.datetime.now()
    return (f"Use This Real-time Information if needed:\n"
            f"Day: {now.strftime('%A')}\nDate: {now.strftime('%d')}\n"
            f"Month: {now.strftime('%B')}\nYear: {now.strftime('%Y')}\n"
            f"Time: {now.strftime('%H')}:{now.strftime('%M')}:{now.strftime('%S')}\n")

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages, client
    
    try:
        # Reinitialize client if needed
        if client is None:
            from cerebras.cloud.sdk import Cerebras
            client = Cerebras(api_key=CerebrasAPIKey)
        
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
        messages.append({"role": "user", "content": prompt})
        
        SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

        completion = client.chat.completions.create(
            model="llama-3.3-70b",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        SystemChatBot.pop()
        return AnswerModifier(Answer)
    
    except Exception as e:
        if len(SystemChatBot) > 3:
            SystemChatBot.pop()
        error_msg = f"Error in RealtimeSearchEngine: {str(e)}"
        print(error_msg)
        return "I encountered an error while searching. Please try again or check your API configuration."

if __name__ == "__main__":
    while True:
        user_input = input("Enter your query: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print(f"\n{Assistantname}:", RealtimeSearchEngine(user_input), "\n")