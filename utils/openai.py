import os
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import Iterable


client = OpenAI()
async_client = AsyncOpenAI()

def get_llm_answer(model: str, msgs: Iterable[ChatCompletionMessageParam]):
    if not model:
        raise ValueError('Missing model argument')
    
    if not msgs:
        raise ValueError('Missing msgs argument')

    completion = client.chat.completions.create(
        model=model,
        messages=msgs,
    )

    return completion.choices[0].message.content

async def aget_llm_answer(model: str, msgs: Iterable[ChatCompletionMessageParam]):
    if not model:
        raise ValueError('Missing model argument')
    
    if not msgs:
        raise ValueError('Missing msgs argument')

    completion = await async_client.chat.completions.create(
        model=model,
        messages=msgs,
    )

    return completion.choices[0].message.content

def get_streaming_answer(model: str, system_prompt: str, msg: str):
    if not model:
        raise ValueError('Missing model argument')
    
    if not system_prompt:
        raise ValueError('Missing system_prompt argument')

    if not msg:
        raise ValueError('Missing msg argument')

    stream = client.responses.create(
        model="gpt-5.5",
        instructions=system_prompt,
        input=msg,
        stream=True,
    )

    for event in stream:
        yield event

# Need to write image processing call.