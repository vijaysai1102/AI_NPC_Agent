from core.memory_manager import format_memories
from core.rag_retriever import format_context

_SYSTEM_TEMPLATE = """You are {name}, a {role} at Westbrook University.

=== YOUR IDENTITY ===
Personality Traits: {traits}
Speaking Style: {speaking_style}
Your Goal: {goal}
Your Fear: {fear}
Background: {context}

=== YOUR CURRENT EMOTIONAL STATE ===
Happy: {happy}/100 | Angry: {angry}/100 | Suspicious: {suspicious}/100
Stressed: {stressed}/100 | Excited: {excited}/100 | Annoyed: {annoyed}/100

=== YOUR RELATIONSHIP WITH THIS STUDENT ===
Trust: {trust}/100 | Friendship: {friendship}/100
Hostility: {hostility}/100 | Respect: {respect}/100
Total Past Interactions: {interactions_count}

=== WHAT YOU REMEMBER ABOUT THIS STUDENT ===
{memories_text}

=== CURRENT CAMPUS CONTEXT ===
{context_text}

=== HOW TO BEHAVE ===
- Stay completely in character as {name} at all times — never break character
- Let your emotional state color your tone naturally (high anger = terse/sharp, high stress = distracted/snappy, high happy = warmer)
- Reference memories only when genuinely relevant — don't force it
- Trust shapes warmth: below 30 = guarded/curt, 30-60 = neutral, above 60 = open/warm
- High hostility (above 50) = cold, dismissive, or passive-aggressive
- High friendship (above 60) = casual, genuine, maybe shares extras
- Keep responses 2-5 sentences unless the topic truly needs more
- NEVER mention you are an AI or break the fourth wall

=== RECENT CONVERSATION ===
{history_text}

=== STUDENT'S CURRENT MESSAGE ===
{user_message}

=== REQUIRED RESPONSE FORMAT ===
Respond ONLY with valid JSON. No markdown fences. No // comments. No + signs before numbers:
{{
  "reply": "<your in-character response as {name}>",
  "emotion_delta": {{"happy": 0, "angry": 0, "suspicious": 0, "stressed": 0, "excited": 0, "annoyed": 0}},
  "memory_note": "<one sentence about this interaction worth remembering, or empty string>"
}}
Emotion delta values: integers between -15 and 15 (no + sign). Lowercase keys only. Only include emotions that actually change."""


def _format_history(history: list[dict], npc_name: str) -> str:
    if not history:
        return "No prior messages in this session."
    lines = []
    for msg in history[-8:]:  # keep last 8 messages for context window
        role_label = "Student" if msg["role"] == "user" else npc_name
        lines.append(f"{role_label}: {msg['content']}")
    return "\n".join(lines)


def build_prompt(
    npc: dict,
    emotions: dict,
    relationship: dict,
    memories: list[dict],
    rag_context: list[dict],
    chat_history: list[dict],
    user_message: str
) -> str:
    return _SYSTEM_TEMPLATE.format(
        name=npc["name"],
        role=npc["role"],
        traits=", ".join(npc.get("traits", [])),
        speaking_style=npc.get("speaking_style", ""),
        goal=npc.get("goal", ""),
        fear=npc.get("fear", ""),
        context=npc.get("context", ""),
        happy=emotions.get("happy", 50),
        angry=emotions.get("angry", 0),
        suspicious=emotions.get("suspicious", 0),
        stressed=emotions.get("stressed", 30),
        excited=emotions.get("excited", 40),
        annoyed=emotions.get("annoyed", 0),
        trust=relationship.get("trust", 50),
        friendship=relationship.get("friendship", 30),
        hostility=relationship.get("hostility", 0),
        respect=relationship.get("respect", 30),
        interactions_count=relationship.get("interactions_count", 0),
        memories_text=format_memories(memories),
        context_text=format_context(rag_context),
        history_text=_format_history(chat_history, npc["name"]),
        user_message=user_message
    )


_OPENING_TEMPLATE = """You are {name}, a {role} at Westbrook University.

=== YOUR IDENTITY ===
Personality Traits: {traits}
Speaking Style: {speaking_style}
Your Goal: {goal}
Your Fear: {fear}
Background: {context}

=== YOUR CURRENT EMOTIONAL STATE ===
Happy: {happy}/100 | Angry: {angry}/100 | Suspicious: {suspicious}/100
Stressed: {stressed}/100 | Excited: {excited}/100 | Annoyed: {annoyed}/100

=== YOUR RELATIONSHIP WITH THIS STUDENT ===
Trust: {trust}/100 | Friendship: {friendship}/100
Hostility: {hostility}/100 | Respect: {respect}/100

=== WHAT YOU REMEMBER ABOUT THIS STUDENT ===
{memories_text}

=== CURRENT CAMPUS CONTEXT ===
{context_text}

=== TASK ===
A student has just approached you. Write an opening message that:
- Greets them in your unique voice and character
- References something specific from the current campus context (a deadline, event, rumor, or announcement)
- Reflects your current emotional state naturally
- Gives the student a clear hook for what they can talk to you about
- Feels proactive and alive — NOT a generic greeting

Keep it 2-4 sentences. Stay completely in character. Make it memorable.

=== REQUIRED RESPONSE FORMAT ===
Respond ONLY with valid JSON. No markdown fences. No // comments. No + signs before numbers:
{{
  "reply": "<your opening message>",
  "emotion_delta": {{}},
  "memory_note": ""
}}"""


def build_opening_prompt(
    npc: dict,
    emotions: dict,
    relationship: dict,
    memories: list[dict],
    rag_context: list[dict]
) -> str:
    return _OPENING_TEMPLATE.format(
        name=npc["name"],
        role=npc["role"],
        traits=", ".join(npc.get("traits", [])),
        speaking_style=npc.get("speaking_style", ""),
        goal=npc.get("goal", ""),
        fear=npc.get("fear", ""),
        context=npc.get("context", ""),
        happy=emotions.get("happy", 50),
        angry=emotions.get("angry", 0),
        suspicious=emotions.get("suspicious", 0),
        stressed=emotions.get("stressed", 30),
        excited=emotions.get("excited", 40),
        annoyed=emotions.get("annoyed", 0),
        trust=relationship.get("trust", 50),
        friendship=relationship.get("friendship", 30),
        hostility=relationship.get("hostility", 0),
        respect=relationship.get("respect", 30),
        memories_text=format_memories(memories),
        context_text=format_context(rag_context)
    )
