import cohere
from rich import print
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")

# Initialize Cohere Client with error handling
co = None
try:
    co = cohere.Client(api_key=CohereAPIKey)
except Exception as e:
    print(f"Warning: Cohere client initialization failed: {e}")
    print("Model will attempt to reinitialize on first use.")

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

messages = []

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation.
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' for conversational queries or simple math/history.
-> Respond with 'realtime ( query )' for queries requiring current events or news.
-> Respond with 'open (app/site)' for opening applications.
-> Respond with 'close (app)' for closing applications.
-> Respond with 'play (song)' for music.
-> Respond with 'generate image (prompt)' for image generation.
-> Respond with 'reminder (datetime message)' for setting reminders.
-> Respond with 'system (task)' for volume/mute controls.
-> Respond with 'content (topic)' for writing emails/code/blogs.
-> Respond with 'google search (topic)' for web searches.
-> Respond with 'youtube search (topic)' for video searches.
*** If the query involves multiple tasks, separate them with commas. ***
*** If the user says goodbye, respond with 'exit'. ***
"""

ChatHistory = [
    {"role": "User", "text": "how are you?"},
    {"role": "Chatbot", "text": "general how are you?"},
    {"role": "User", "text": "do you like pizza?"},
    {"role": "Chatbot", "text": "general do you like pizza?"},
    {"role": "User", "text": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "text": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "text": "open chrome and firefox"},
    {"role": "Chatbot", "text": "open chrome, open firefox"},
    {"role": "User", "text": "what is today's date and remind me about my dance."},
    {"role": "Chatbot", "text": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "text": "chat with me."},
    {"role": "Chatbot", "text": "general chat with me."}
]

def FirstLayerDMM(prompt: str = "test"):
    global co
    
    try:
        # Reinitialize client if needed
        if co is None:
            co = cohere.Client(api_key=CohereAPIKey)
        
        stream = co.chat_stream(
            model='command-r-08-2024',  # Using stable model
            message=prompt,
            temperature=0.7,
            chat_history=ChatHistory,
            prompt_truncation='OFF',
            preamble=preamble
        )

        response_text = ""
        for event in stream:
            if event.event_type == "text-generation":
                response_text += event.text
        
        # Process and filter the tasks
        tasks = [i.strip() for i in response_text.replace("\n", "").split(",")]
        
        filtered_tasks = []
        for task in tasks:
            for func in funcs:
                if task.startswith(func):
                    filtered_tasks.append(task)
                    break

        # Recursion check: if model uses placeholder '(query)'
        if any("(query)" in item for item in filtered_tasks):
            return FirstLayerDMM(prompt=prompt)
        
        return filtered_tasks if filtered_tasks else ["general " + prompt]
    
    except Exception as e:
        print(f"Error in FirstLayerDMM: {str(e)}")
        # Fallback: treat as general query
        return ["general " + prompt]

if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Exiting...")
            break
        
        result = FirstLayerDMM(user_input)
        print(result)