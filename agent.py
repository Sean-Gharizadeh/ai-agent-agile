from langchain_ollama import ChatOllama
from utils import log_line, build_prompt, ask_llm_streaming
from commands import get_commands

commands = get_commands()

def ask_llm(llm, user_input: str) -> str:
    try:
        return llm.invoke(user_input).content
    except Exception as e:
        return f"❌ Model error: {e}"


def run_agent():
    state = {
        "model": "llama3.2",
        "temperature": 0,
        "history": [], 
        "persona": "default",
        "system_prompt": globals().get("PERSONAS", {}).get("default", "You are a helpful assistant. Be clear and concise."),
        "streaming": True,
        "window": 8,
    }

    def llm_factory(model):
        return ChatOllama(model=model, temperature=0)

    llm_ref = {
        "llm": llm_factory(state["model"]),
        "factory": llm_factory,
        "log": log_line,
    }

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye 👋")
            break

        log_line(f"user | {user_input}")

        # --- COMMAND HANDLING ---
        if user_input.startswith("/"):
            parts = user_input.split(" ", 1)
            cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else ""

            handler = commands.get(cmd)
            if handler:
                handler(state, llm_ref, arg)
            else:
                print("Unknown command. Try /help")
            continue
            
        # --- NORMAL CHAT ---
        state["history"].append(("user", user_input))

        prompt = build_prompt(
            state["history"],
            user_input,
            system_prompt=state["system_prompt"],
            window=state["window"],
       )

        print("AI: ", end="", flush=True)
        answer = ask_llm_streaming(llm_ref["llm"], prompt)

        log_line(f"ai | {answer}")
        state["history"].append(("ai", answer))
