import os
from typing import Iterable


def get_llm_answer(model: str, msgs: Iterable[dict]) -> str:
    if not model:
        raise ValueError('Missing model argument')
    if not msgs:
        raise ValueError('Missing msgs argument')

    msgs = list(msgs)

    if model.startswith("claude"):
        return _anthropic_answer(model, msgs)
    else:
        return _openai_answer(model, msgs)


def _openai_answer(model: str, msgs: list[dict]) -> str:
    from openai import OpenAI
    client = OpenAI()
    completion = client.chat.completions.create(model=model, messages=msgs)
    return completion.choices[0].message.content


def _anthropic_answer(model: str, msgs: list[dict]) -> str:
    import anthropic
    client = anthropic.Anthropic()

    system_prompt = ""
    user_msgs = []
    for m in msgs:
        if m["role"] == "system":
            system_prompt = m["content"]
        else:
            user_msgs.append(m)

    if not user_msgs:
        user_msgs = [{"role": "user", "content": system_prompt}]
        system_prompt = ""

    kwargs = {"model": model, "max_tokens": 1024, "messages": user_msgs}
    if system_prompt:
        kwargs["system"] = system_prompt

    response = client.messages.create(**kwargs)
    return response.content[0].text
