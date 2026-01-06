# PRISM - Personal Responsive Intelligence System Manager

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![PRISM Logo](Frontend/Graphics/prism.gif)

**PRISM** is a personal AI assistant. It is designed to be a responsive, intelligent, and proactive companion that manages daily tasks, automates routines, provides real-time information, generates images, and interacts via voice and text with a modern graphical user interface.

PRISM delivers clear insights, multi-faceted automation, and seamless integration across tasks, devices, and personal workflows.

## Features

- **Voice Interaction**: Speech-to-Text (STT) and Text-to-Speech (TTS) for natural conversation.
- **Chatbot Intelligence**: Contextual conversation powered by local or API-based language models.
- **Real-Time Search**: Integrated search engine for up-to-date web information.
- **Image Generation**: AI-powered image creation from text prompts.
- **Task Automation**: Custom automation scripts for repetitive tasks and smart home integration.
- **Modern GUI**: Clean, customizable desktop interface with voice activation, chat history, and visual feedback.
- **Data Persistence**: Local storage for responses, status, microphone data, and generated images.


1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/PRISM.git
   cd PRISM

Create a virtual environment (recommended)Bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies
Create a requirements.txt with the following (example – adjust based on your actual dependencies):textopenai
whisper  # or faster-whisper for SpeechToText
pyttsx3  # or elevenlabs/gTTS for TextToSpeech
tkinter  # usually included with Python
pillow
requests
python-dotenv
# Add any additional libraries (e.g., torch for local models)Then run:Bashpip install -r requirements.txt
Set up environment variables
Copy .env.example to .env and fill in your API keys:textOPENAI_API_KEY=your_openai_key
IMAGE_GEN_API_KEY=your_image_gen_key
# Add other keys as needed

Usage

Run the application:Bashpython Main.py
The GUI will launch. Click the microphone icon or press a hotkey to start voice interaction.
Type or speak commands – PRISM will respond via voice and text.
Use the chat window for conversation history, settings for customization, and image generation features as implemented.

Contributing
Contributions are welcome! Feel free to:

Open issues for bugs or feature requests
Submit pull requests with improvements
Enhance modules (better models, new automations, UI polish)

Please follow standard GitHub flow: fork → branch → PR.
License
This project is licensed under the MIT License – see the LICENSE file for details.
Acknowledgments

Built for personal productivity and futuristic interfaces
