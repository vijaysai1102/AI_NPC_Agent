# Living Campus — AI NPC Agent

> **An interactive campus world where AI characters remember you, feel emotions, and evolve real relationships over time.**

Built with Streamlit, Groq (Qwen 3.8 27B), and SQLite — every NPC has a persistent memory, a live emotional state, and a relationship with you that grows (or deteriorates) with every message.

---

## What Is This?

Living Campus is a conversational AI simulation set at **Westbrook University**. You play as a student navigating campus life by chatting with three unique AI-powered NPCs. Unlike a standard chatbot, these characters:

- **Remember** what you've said to them across sessions
- **Feel emotions** that shift based on how you treat them
- **Track your relationship** — trust, friendship, hostility, and respect evolve over time
- **Know what's happening on campus** — exams, events, rumors, and deadlines through a RAG system
- **Open conversations proactively** — each NPC greets you with a context-aware message, not a generic "Hello"

The entire state is persisted in a local SQLite database, so every conversation builds on the last.

---

## Meet the NPCs

| NPC | Role | Vibe |
|-----|------|------|
| 👨‍🏫 **Dr. Marcus Webb** | CS Professor | Strict, sarcastic, formally intelligent. PhD from MIT, 12 published papers. Has failed students without hesitation. |
| 🦇 **Batman** | Campus Friend / Junior CS Student | Chaotic, meme-fluent, gossip-obsessed. Secretly runs anonymous campus Instagram `@CSHallwayDrama` with 800 followers. Nobody knows it's him. |
| 😩 **Kevin Park** | Teaching Assistant | Overworked 2nd-year PhD student. Passive-aggressive but secretly helpful. Has left comments like "Are you serious right now?" on student submissions. |

Each NPC has a distinct **personality**, **speaking style**, **goal**, and **fear** that shapes every response.

---

## Features

### Persistent Memory
Every meaningful interaction is summarized and stored as a memory. The AI extracts a `memory_note` from each exchange and saves it to SQLite. On future sessions, the NPC is injected with its top recent memories — so if you lied to Kevin last week, he might remember that.

### Emotion Engine
Each NPC tracks **6 emotions** in real time, all scored 0–100:

| Emotion | Effect on behavior |
|---|---|
| Happy | Warmer, more willing to help |
| Angry | Terse, sharp, dismissive |
| Suspicious | Guarded, questions your motives |
| Stressed | Distracted, snappy |
| Excited | Enthusiastic, talkative |
| Annoyed | Passive-aggressive, short |

The LLM returns an `emotion_delta` JSON object with each reply — the engine clamps all values to [0, 100] and persists them to the database.

### Relationship System
Every NPC tracks **4 relationship axes** with the student, also scored 0–100:

| Axis | What it does |
|---|---|
| Trust | Below 30 = guarded/curt. Above 60 = open and candid. |
| Friendship | Above 60 = casual, shares extras, genuinely warm |
| Hostility | Above 50 = cold, dismissive, passive-aggressive |
| Respect | Shapes how seriously the NPC takes your input |

Relationships drift passively over time — every 5 interactions, trust and respect tick up slightly. They also change based on what you say.

### RAG Context (Campus Knowledge Base)
NPCs don't live in a vacuum. A lightweight keyword-based retrieval system pulls relevant campus context into every prompt from a structured JSON knowledge base:

- `events.json` — upcoming exams, hackathons, BBQs, study sessions
- `assignments.json` — active coursework and deadlines
- `rumors.json` — campus gossip and hearsay
- `announcements.json` — official university notices
- `lore.json` — background world-building

Each context item has `npc_relevance` tags so only the right NPCs get the right context (Batman gets rumors; Dr. Webb gets assignment deadlines).

### Prompt Architecture
Every message to the LLM is a fully assembled system prompt containing:
1. NPC identity (traits, speaking style, goal, fear, background)
2. Current emotional state (all 6 emotions with live values)
3. Current relationship stats (all 4 axes + interaction count)
4. Top 5 recent memories about the student
5. Retrieved campus context (top 3 relevant items)
6. Last 8 messages of chat history
7. The student's current message

The LLM responds with structured JSON: `reply`, `emotion_delta`, and `memory_note`.

### Proactive Opening Messages
When you first approach an NPC (or start a fresh session), they generate a context-aware greeting — not "Hi, how can I help?" but something like Kevin sighing about your last submission, or Batman texting you about a rumor he just heard. The opening prompt uses a separate template that instructs the model to reference live campus context and reflect the NPC's current emotional state.

### Chat History Persistence
All messages are saved to SQLite and reloaded on return visits. The last 50 messages per NPC are surfaced in the UI. You can reset any NPC's state from the sidebar to start fresh.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| LLM | [Groq API](https://console.groq.com) — `qwen/qwen3.8-27b` |
| Database | SQLite (via Python `sqlite3`) |
| Config | `python-dotenv` |
| NPC data | Static JSON (`data/npcs.json`) |
| Campus knowledge | JSON files in `data/campus_context/` |

---

## Project Structure

```
AI_NPC_Agent/
│
├── app.py                        # Streamlit entry point — UI, routing, chat loop
│
├── ai/
│   ├── gemini_client.py          # Groq API wrapper — generates responses + parses JSON
│   ├── prompt_builder.py         # Assembles full system prompts from all context
│   └── opening_message.py        # Generates proactive NPC greeting on first visit
│
├── core/
│   ├── database.py               # SQLite connection + schema initialization
│   ├── npc_loader.py             # Loads NPC profiles from npcs.json
│   ├── memory_manager.py         # Save/retrieve memories + chat history
│   ├── emotion_engine.py         # Read/write/reset NPC emotions
│   ├── relationship_engine.py    # Read/write relationship axes + interaction counter
│   └── rag_retriever.py          # Keyword-based context retrieval from campus JSON files
│
├── ui/
│   ├── npc_card.py               # NPC profile card sidebar component
│   └── meters.py                 # Emotion bars, relationship bars, memory timeline
│
├── config/
│   └── settings.py               # Env vars, file paths, tunable constants
│
├── data/
│   ├── npcs.json                 # NPC definitions (personality, traits, initial mood)
│   ├── campus.db                 # SQLite database — auto-created on first run (gitignored)
│   └── campus_context/
│       ├── events.json           # Campus events and exams
│       ├── assignments.json      # Active coursework and deadlines
│       ├── rumors.json           # Campus gossip
│       ├── announcements.json    # Official notices
│       └── lore.json             # World-building background
│
├── utils/
│   └── helpers.py                # Shared utility functions
│
├── .env.example                  # Template for environment variables
├── requirements.txt              # Python dependencies
└── test_api.py                   # Quick API connectivity test
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/vijaysai1102/AI_NPC_Agent.git
cd AI_NPC_Agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get a free Groq API key

Go to [console.groq.com](https://console.groq.com) → sign up → create an API key. It's free.

### 4. Create your `.env` file

```bash
cp .env.example .env
```

Open `.env` and add your key:

```
GROQ_API_KEY=your_key_here
```

### 5. Run

```bash
streamlit run app.py
```

The SQLite database (`data/campus.db`) is created automatically on first run. No setup needed.

---

## How It Works — End to End

```
User types a message
        │
        ▼
retrieve_context()     ← keyword-matches campus JSON against the message
get_recent_memories()  ← top 5 memories for this NPC from SQLite
get_emotions()         ← live emotion state from SQLite
get_relationship()     ← live relationship axes from SQLite
        │
        ▼
build_prompt()         ← assembles everything into a single system prompt
        │
        ▼
generate_response()    ← sends to Groq (Qwen 3.8 27B), gets back JSON
        │
        ├── reply          → displayed in chat
        ├── emotion_delta  → update_emotions() clamps and saves to SQLite
        └── memory_note    → save_memory() saves to SQLite if non-empty
                │
                ▼
        increment_interactions()
        passive relationship drift every 5 interactions
```

---

## Tunable Constants

All in `config/settings.py`:

| Constant | Default | What it controls |
|---|---|---|
| `GROQ_MODEL` | `qwen/qwen3.8-27b` | LLM model (override in `.env`) |
| `MEMORY_CONTEXT_COUNT` | `5` | How many memories are injected per prompt |
| `RAG_TOP_K` | `3` | How many campus context items are retrieved |
| `STAT_MIN` / `STAT_MAX` | `0` / `100` | Emotion and relationship value bounds |

---

## Adding New NPCs

1. Add a new entry to `data/npcs.json` with the same schema (id, name, role, emoji, traits, speaking_style, goal, fear, context, rag_tags, initial_mood)
2. Add `npc_relevance` tags to relevant items in `data/campus_context/` so the NPC receives the right campus context
3. Restart the app — the new NPC appears automatically in the sidebar

No code changes required.

---

## Adding New Campus Context

Drop new JSON entries into any file in `data/campus_context/`. Each item needs:

```json
{
  "id": "unique_id",
  "title": "Short title",
  "description": "Full context text",
  "tags": ["relevant", "keywords"],
  "npc_relevance": ["professor", "friend", "ta"]
}
```

The RAG retriever picks it up automatically on next message.

---

## License

MIT
