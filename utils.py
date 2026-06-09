from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "chat.log"

def log_line(text: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{ts} | {text}\n")


def build_prompt(history, user_input: str, system_prompt: str, window: int = 8) -> str:
    
    if window > 0:
        recent = history[-window:]
    else:
        recent = []

    lines = [f"system: {system_prompt}"]
    lines += [f"{role}: {text}" for role, text in recent]
    lines.append(f"user: {user_input}")

    return "\n".join(lines)
    
def ask_llm_streaming(llm, prompt: str) -> str:
    full = []
    for chunk in llm.stream(prompt):
        text = getattr(chunk, "content", "")

        if text:
            print(text, end="", flush=True)
            full.append(text)
            
    print()  # newline after streaming finishes
    return "".join(full)

