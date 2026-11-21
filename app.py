import os
import random
import re
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()  # reads your secret key from the .env file

app = Flask(__name__, static_folder="static")

# Change to True later if you want to try Gemini again
USE_GEMINI = False

# ---------- Backup brain (works without internet or Gemini) ----------
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I would tell you a UDP joke, but you might not get it.",
    "Why did the developer go broke? Because he used up all his cache.",
    "There are 10 kinds of people. Those who understand binary and those who do not.",
]


def reply_for(text):
    t = text.lower().strip()
    words = set(re.findall(r"[a-z']+", t))

    def word(*options):
        return any(o in words for o in options)

    def phrase(*options):
        return any(o in t for o in options)

    if not t:
        return "I did not catch that. Could you say it again?"

    if phrase("who are you", "about fatima", "who is fatima", "about yourself", "your name"):
        return ("I am Fatima's voice assistant. Fatima Zaheer is a full stack and mobile developer, "
                "and a Computer Science student at Air University, Multan.")

    if phrase("how were you built", "how do you work", "how are you made", "this assistant", "voice assistant"):
        return ("I am one of Fatima's projects. The page listens with the browser's speech recognition, "
                "my Python and Flask brain picks a reply, and the browser speaks it out loud. "
                "The glowing orb reacts to your voice.")

    if phrase("subscription", "spending", "analyzer", "analyser", "what is next", "working on next", "next project"):
        return ("Next, Fatima is planning a subscription and spending analyzer. You upload a bank file, "
                "it finds repeating payments, and shows a dashboard. It will use a Python backend, "
                "React and a PostgreSQL database. It is not built yet.")

    if word("hello", "hi", "hey", "salaam", "assalam"):
        return "Hello! I am Fatima's assistant. Ask me for the time, a joke, or about her projects."

    if word("time"):
        return "It is " + datetime.now().strftime("%I:%M %p").lstrip("0") + "."

    if word("date", "today", "day"):
        return "Today is " + datetime.now().strftime("%A, %B %d, %Y") + "."

    if word("joke", "funny"):
        return random.choice(JOKES)

    if word("project", "projects", "built", "build"):
        return ("Fatima has built five projects: a real-time chat app with Socket.IO, an AI study notes "
                "summarizer with the Gemini API, a hand gesture rock paper scissors game with OpenCV, "
                "a job portal, and me, this voice assistant. Ask about any of them, "
                "or about what she is building next.")

    if word("skill", "skills", "technologies", "stack"):
        return ("Fatima works with JavaScript, TypeScript, Python, React, Next.js, Node.js, "
                "Express, MongoDB and Flutter.")

    if word("experience", "internship", "internships", "worked"):
        return ("Fatima was a front-end AI engineering intern at FlyRank dot AI, "
                "and a full stack developer intern at Decode Lab.")

    if word("contact", "email", "reach", "hire"):
        return "You can reach Fatima at fatimamalikk072 at gmail dot com, or through GitHub and LinkedIn."

    if word("help") or phrase("what can you do"):
        return ("You can ask me the time, the date, a joke, or about Fatima's projects, skills "
                "and experience. You can also ask how I was built, or what she is building next.")

    if word("thanks", "thank"):
        return "You are welcome!"

    if word("bye", "goodbye"):
        return "Goodbye! Have a great day."

    return "I am not sure about that yet. Try asking about the time, a joke, or Fatima's projects."


# ---------- Gemini brain (optional) ----------
# The assistant tries these models in order. If one is busy or over its limit, it tries the next.
MODELS = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite"]

SYSTEM = (
    "You are the voice assistant on the portfolio of Fatima Zaheer. Your answers are spoken aloud, "
    "so reply in plain text with one to three short sentences, no lists, no markdown, no emojis. "
    "Be warm and a little playful. Facts about Fatima: she is a full stack and mobile developer and a "
    "Computer Science student at Air University, Multan, expected to graduate in 2028. "
    "Projects she has built: a real-time chat app (Node.js, Socket.IO), an AI study notes summarizer "
    "(Next.js, TypeScript, Gemini API), a hand gesture rock paper scissors game (Python, OpenCV, MediaPipe), "
    "a job portal (Node.js, MongoDB), and this voice assistant (Python, Flask, Web Speech API). "
    "A project she is planning to build next, which does not exist yet: a subscription and spending "
    "analyzer with a Python backend, React frontend and PostgreSQL, where you upload a bank file, it "
    "finds repeating payments and shows a dashboard. Never say the analyzer is finished. "
    "Experience: front-end AI engineering intern at FlyRank.ai "
    "(Jul to Aug 2026) and full stack developer intern at Decode Lab (Jun to Jul 2026). "
    "Skills: JavaScript, TypeScript, Python, React, Next.js, Node.js, Express, MongoDB, Flutter. "
    "Email: fatimamalikk072 at gmail dot com. She is looking for a software development internship. "
    "If asked something about Fatima that is not listed here, say you do not know and suggest emailing her. "
    "You can also chat about general topics. Never invent facts about Fatima."
)

try:
    from google import genai
    from google.genai import types

    _key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=_key) if _key else None
except Exception as e:
    print("Gemini setup problem:", e)
    client = None

history = []  # the conversation so far, so it remembers what you said


def smart_reply(text):
    if not USE_GEMINI or client is None or not text.strip():
        return reply_for(text), "keywords"

    while len(history) > 10:  # keep only the latest few turns
        history.pop(0)
    history.append(types.Content(role="user", parts=[types.Part(text=text)]))

    for model in MODELS:  # try each model until one answers
        try:
            response = client.models.generate_content(
                model=model,
                contents=history,
                config=types.GenerateContentConfig(system_instruction=SYSTEM),
            )
            answer = (response.text or "").strip()
            if not answer:
                raise ValueError("empty answer")
            history.append(types.Content(role="model", parts=[types.Part(text=answer)]))
            return answer, "gemini (" + model + ")"
        except Exception as e:
            print("Gemini error with", model, ":", str(e)[:150])

    history.pop()  # nothing worked, so the keyword brain steps in
    return reply_for(text), "keywords"


# ---------- Web routes ----------
@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route("/api/reply", methods=["GET", "POST"])
def api_reply():
    if request.method == "POST":
        text = (request.get_json(silent=True) or {}).get("text", "")
    else:
        text = request.args.get("text", "")
    answer, source = smart_reply(text)
    print("Brain used:", source)
    return jsonify({"reply": answer})


if __name__ == "__main__":
    app.run(debug=True)