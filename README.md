# Living Campus — AI NPC Agent

A hackathon-ready interactive campus world where AI NPCs remember you, feel emotions, and evolve relationships over time.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create your `.env` file
```bash
cp .env.example .env
```
Then open `.env` and paste your Gemini API key.
Get a free key at: https://aistudio.google.com/app/apikey

### 3. Run
```bash
streamlit run app.py
```

## Project Structure

```
app.py                      # Streamlit entry point
config/settings.py          # Environment + path config
data/npcs.json              # NPC personalities (static)
data/campus_context/        # RAG knowledge base (events, assignments, rumors...)
data/campus.db              # SQLite — auto-created on first run
core/database.py            # DB connection + schema init
core/npc_loader.py          # Load NPC profiles from JSON
core/memory_manager.py      # Save/retrieve NPC memories
core/emotion_engine.py      # Update NPC emotional state
core/relationship_engine.py # Track trust, friendship, hostility, respect
core/rag_retriever.py       # Lightweight keyword-based context retrieval
ai/gemini_client.py         # Gemini API wrapper
ai/prompt_builder.py        # Assemble system prompts with full context
ai/opening_message.py       # Generate NPC greeting on selection
ui/npc_card.py              # NPC profile card component
ui/meters.py                # Emotion + relationship bar visualizations
utils/helpers.py            # Utility functions
```

## NPCs

| NPC | Role | Vibe |
|-----|------|------|
| Dr. Marcus Webb | CS Professor | Strict, impatient, sarcastic |
| Priya Sharma | Campus Friend | Chaotic, funny, gossip queen |
| Kevin Park | Teaching Assistant | Overworked, passive-aggressive, secretly helpful |

## Features

- **Persistent memory** — NPCs remember past interactions across sessions
- **Emotion system** — 6 tracked emotions that shift based on your actions
- **Relationship system** — trust, friendship, hostility, respect evolve over time
- **RAG context** — NPCs know about campus events, deadlines, and rumors
- **Proactive opening messages** — NPCs start conversations with relevant context
