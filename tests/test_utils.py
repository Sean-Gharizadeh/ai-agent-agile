from utils import build_prompt

def test_build_prompt_simple():
    history = [("user", "hello"), ("ai", "hi")]

    prompt = build_prompt(history, "how are you", window=2)

    assert "user: hello" in prompt
    assert "user: how are you" in prompt