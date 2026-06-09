from fastapi import FastAPI
from fastapi.responses import FileResponse
from langchain_ollama import ChatOllama
from commands import get_commands

app = FastAPI()

state = {
    "model_general": "llama3.2:3b",
    "model_reasoning": "phi4",
    "persona": "default",
    "streaming": False,
    "window": 10,
    "history": []
}

commands = get_commands()


# General-purpose model
llm_general = ChatOllama(model=state["model_general"], temperature=0)

# Reasoning-focused model
llm_reasoning = ChatOllama(model=state["model_reasoning"], temperature=0)

@app.get("/")
def root():
    return FileResponse("index.html")

@app.post("/chat")
def chat(payload: dict):
    user_input = payload.get("message", "").strip()

    #Commands first
    if user_input.startswith("/"):
        parts = user_input.split(" ", 1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else ""

        handler = commands.get(cmd)
        if not handler:
            return {"reply": "❌ Unknown command"}

        try:
            # Route reasoning-heavy commands to Phi-4
            if cmd in ["/sprint"]:
                result = handler(state, {"llm": llm_reasoning}, arg)
            else:
                result = handler(state, {"llm": llm_general}, arg)

            return {"reply": result or f"✅ Command executed: {cmd}"}

        except Exception as e:
            return {"reply": f"❌ Command error: {str(e)}"}

    # Normal chat uses Llama 3.2
    try:
        response = llm_general.invoke([
            ("human", user_input)
        ])
        return {"reply": response.content}
    except Exception as e:
        return {"reply": f"❌ LLM error: {str(e)}"}

