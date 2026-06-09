# commands.py

PERSONAS = {
    "default": "You are a helpful assistant. Be clear and concise.",
    "teacher": "You are a patient teacher. Explain step by step with simple examples.",
    "coder": "You are a senior Python developer. Provide clean code and brief explanations.",
    "strict": "Be precise. If unsure, say 'I don't know'. Avoid guessing.",
}


def _log(llm_ref, text: str) -> None:
    """Log helper: only logs if llm_ref contains a callable 'log'."""
    logger = llm_ref.get("log")
    if callable(logger):
        logger(text)


# -------------------------
# Basic commands
# -------------------------

def cmd_help(state, llm_ref, _arg: str):
    print("Commands:")
    print("  /help                 show this help")
    print("  /status               show current settings")
    print("  /history              show last messages")
    print("  /clear                clear chat history")
    print("  /model <name>         switch model (e.g. mistral, llama3.2:3b)")
    print("")
    print("A8 Persona & Prompt:")
    print("  /persona              show current persona + list personas")
    print("  /persona <name>       set persona (default/teacher/coder/strict)")
    print("  /system               show current system prompt")
    print("  /system <text>        set custom system prompt")
    print("")
    print("A8 Streaming & Context:")
    print("  /stream               show streaming status")
    print("  /stream on|off         toggle streaming")
    print("  /window               show current window")
    print("  /window <n>            set history window (0 = no history)")


def cmd_clear(state, llm_ref, _arg: str):
    state["history"].clear()
    print("✅ History cleared")
    _log(llm_ref, "cmd | clear")


def cmd_history(state, llm_ref, arg: str):
    # Optional: allow "/history 10"
    n = 6
    if arg.strip():
        try:
            n = int(arg.strip())
        except Exception:
            print("Usage: /history or /history <number>")
            return

    last = state["history"][-n:]
    if not last:
        print("(no history)")
        return

    for role, text in last:
        print(f"{role}: {text}")

    _log(llm_ref, f"cmd | history | {n}")


def cmd_model(state, llm_ref, arg: str):
    name = arg.strip()
    if not name:
        print("Usage: /model <name>")
        return

    state["model"] = name

    # Recreate the model immediately so it takes effect
    factory = llm_ref.get("factory")
    if callable(factory):
        llm_ref["llm"] = factory(name)

    print("✅ Model set to:", name)
    _log(llm_ref, f"cmd | model | {name}")


# -------------------------
# A8: Persona & System Prompt
# -------------------------

def cmd_persona(state, llm_ref, arg: str):
    name = arg.strip().lower()

    if not name:
        current = state.get("persona", "default")
        print(f"Current persona: {current}")
        print("Available personas:", ", ".join(PERSONAS.keys()))
        print("Usage: /persona <" + "|".join(PERSONAS.keys()) + ">")
        return

    if name not in PERSONAS:
        print(f"Unknown persona '{name}'. Options: {', '.join(PERSONAS.keys())}")
        return

    state["persona"] = name
    state["system_prompt"] = PERSONAS[name]
    print("✅ Persona set to:", name)
    _log(llm_ref, f"cmd | persona | {name}")


def cmd_system(state, llm_ref, arg: str):
    text = arg.strip()

    if not text:
        current = state.get("system_prompt", "")
        print("Current system prompt:")
        print(current if current else "(empty)")
        print("Usage: /system <your system prompt>")
        return

    state["system_prompt"] = text
    state["persona"] = "custom"
    print("✅ System prompt updated.")
    preview = text.replace("\n", " ")[:80]
    _log(llm_ref, f"cmd | system | {preview}")


# -------------------------
# A8: Streaming & Window
# -------------------------

def cmd_stream(state, llm_ref, arg: str):
    v = arg.strip().lower()

    if not v:
        current = state.get("streaming", False)
        print("Streaming is:", "ON" if current else "OFF")
        print("Usage: /stream on|off")
        return

    if v not in {"on", "off"}:
        print("Usage: /stream on|off")
        return

    state["streaming"] = (v == "on")
    print("✅ Streaming:", "ON" if state["streaming"] else "OFF")
    _log(llm_ref, f"cmd | stream | {v}")


def cmd_window(state, llm_ref, arg: str):
    text = arg.strip()

    if not text:
        current = state.get("window", 8)
        print("Window is:", current)
        print("Usage: /window <number>   (0 = no history)")
        return

    try:
        n = int(text)
        if n < 0:
            raise ValueError
    except Exception:
        print("Usage: /window <number>   (0 = no history)")
        return

    state["window"] = n
    print("✅ Window set to:", n)
    _log(llm_ref, f"cmd | window | {n}")


# -------------------------
# A8.5: Status
# -------------------------

def cmd_status(state, llm_ref, _arg: str):
    has_story = "✅ available" if state.get("last_story") else "❌ none"
    has_tasks = "✅ available" if state.get("last_tasks") else "❌ none"
    has_sprint = "✅ available" if state.get("last_sprint") else "❌ none"

    return f"""
## Agent Status

- Model: {state.get("model", "unknown")}
- Persona: {state.get("persona", "default")}
- Streaming: {"ON" if state.get("streaming", False) else "OFF"}
- Window: {state.get("window", 0)}
- History: {len(state.get("history", []))} messages
- Tasks: {has_tasks}
- Sprint: {has_sprint}
- Story: {has_story}
"""

def get_commands():
    return {
        "/help": cmd_help,
        "/clear": cmd_clear,
        "/history": cmd_history,
        "/model": cmd_model,

        "/persona": cmd_persona,
        "/system": cmd_system,
        "/stream": cmd_stream,
        "/window": cmd_window,

        "/status": cmd_status,

        "/tasks": cmd_tasks,
        "/sprint": cmd_sprint,
        "/story": cmd_story,
    }

PERSONAS = {
    "default": "You are a helpful assistant.",
    "teacher": "You are a patient teacher. Explain clearly.",
    "coder": "You are a senior Python developer.",
    "strict": "Be precise. If unsure, say you don't know."
}

def cmd_status(state, llm_ref, _arg: str):
    has_story = "✅ available" if state.get("last_story") else "❌ none"
    has_tasks = "✅ available" if state.get("last_tasks") else "❌ none"
    has_sprint = "✅ available" if state.get("last_sprint") else "❌ none"

    return f"""
## Agent Status

- General Model: {state.get("model_general", "unknown")}
- Reasoning Model: {state.get("model_reasoning", "unknown")}
- Persona: {state.get("persona", "default")}
- Streaming: {"ON" if state.get("streaming", False) else "OFF"}
- Window: {state.get("window", 0)}
- History: {len(state.get("history", []))} messages

## Workflow State
- Story: {has_story}
- Tasks: {has_tasks}
- Sprint: {has_sprint}
"""

def cmd_tasks(state, llm_ref, arg: str):
    topic = arg.strip()

    if not topic:
        return "Usage: /tasks <feature or task description>"

    llm = llm_ref.get("llm")
    if llm is None:
        return "❌ No LLM available"

    prompt = f"""
You are an Agile Project Management assistant.

Break the following request into a structured task breakdown.

Rules:
- Output in Markdown
- Use these sections exactly:
  1. Summary
  2. Assumptions
  3. Tasks
  4. Acceptance Checks
  5. Risks & Dependencies
  6. Definition of Done
- Group Tasks by area:
  - Product / UX
  - Backend
  - Frontend
  - QA / Testing
  - DevOps / Release
- Keep tasks small, specific, and actionable
- Do NOT write code
- Do NOT output pseudo-code or class definitions

Request:
{topic}
"""

    try:
        response = llm.invoke([
            ("system", "You are an Agile Project Management assistant."),
            ("human", prompt)
        ])
        result = response.content
    except Exception as e:
        return f"❌ Error while generating tasks: {e}"

    state["last_tasks"] = result
    return result


def cmd_sprint(state, llm_ref, arg: str):
    tasks = state.get("last_tasks")
    if not tasks:
        return "❌ No tasks available. Run /tasks first."

    llm = llm_ref.get("llm")
    if llm is None:
        return "❌ No LLM available"

    sprint_hint = arg.strip() or "Assume a realistic 2-week sprint."

    prompt = f"""
You are an Agile Scrum Master.

Create an intelligent sprint plan from the task breakdown below.

Sprint planning rules:
- Assume realistic sprint capacity
- Do NOT include every task if it is too much for one sprint
- Select the most important tasks for the first sprint
- Prioritize foundational and high-impact work first
- Distinguish between:
  - Must do now
  - Can follow later
  - Risks / blockers
- Identify dependencies where relevant
- Suggest what can be done in parallel
- Keep the sprint focused and realistic

User sprint hint:
{sprint_hint}

Task breakdown:
{tasks}

Output in Markdown with these sections exactly:
## Sprint Goal
## Sprint Scope
## Out of Scope
## Priorities
## Suggested Execution Order
## Parallel Work Opportunities
## Risks / Blockers
## Definition of Sprint Success
"""

    try:
        response = llm.invoke([
            ("system", "You are an Agile Scrum Master."),
            ("human", prompt)
        ])
        result = response.content
    except Exception as e:
        return f"❌ Error generating sprint: {e}"

    state["last_sprint"] = result
    return result


def cmd_story(state, llm_ref, arg: str):
    idea = arg.strip()

    if not idea:
        return "Usage: /story <idea or feature description>"

    llm = llm_ref.get("llm")
    if llm is None:
        return "❌ No LLM available"

    prompt = f"""
You are an Agile Product Owner.

Turn the following idea into a well-structured Agile user story.

Rules:
- Output in Markdown
- Use these sections exactly:
  1. Title
  2. User Story
  3. Acceptance Criteria
  4. Assumptions
  5. Risks / Open Questions
- The user story must follow this format:
  As a [type of user],
  I want [goal],
  so that [benefit].
- Acceptance Criteria must use Given / When / Then
- Do NOT write code

Idea:
{idea}
"""

    try:
        response = llm.invoke([
            ("system", "You are an Agile Product Owner."),
            ("human", prompt)
        ])
        result = response.content
    except Exception as e:
        return f"❌ Error generating story: {e}"

    state["last_story"] = result
    return result


def get_commands():
    return {
        "/status": cmd_status,
        "/tasks": cmd_tasks,
        "/sprint": cmd_sprint,
        "/story": cmd_story,
    }