# Voice Assistant

A voice assistant you talk to in the browser. A glowing orb reacts to your voice, live captions show what you say, and the assistant answers out loud.

## Features
- Voice input with live captions (Web Speech API)
- Orb that changes color for listening, thinking and speaking, and moves with your voice volume
- Spoken replies and a text chat as a backup
- Python and Flask backend that decides the reply
- Answers about the time, jokes, and Fatima's projects, skills and experience

## Tech
Python, Flask, JavaScript, HTML/CSS, Web Speech API

## How to run
```
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000 in Chrome or Edge.

## Optional: Gemini
Create a `.env` file with `GEMINI_API_KEY=your_key` and set `USE_GEMINI = True` in `app.py`.