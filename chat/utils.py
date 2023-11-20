import os
from datetime import timedelta

import openai
import tiktoken
from dotenv import load_dotenv
from django.utils import timezone

from .models import Message

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print(
            "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613."
        )
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print(
            "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
        )
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def format_time_difference(past_date):
    current_date = timezone.now()
    time_difference = current_date - past_date

    if time_difference < timedelta(minutes=1):
        return "just now"
    elif time_difference < timedelta(hours=1):
        minutes = time_difference.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif time_difference < timedelta(days=1):
        hours = time_difference.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif time_difference < timedelta(weeks=1):
        days = time_difference.days
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif time_difference < timedelta(weeks=4):
        weeks = time_difference.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif time_difference < timedelta(days=365):
        months = time_difference.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = time_difference.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"


def generate_answer(queries, chat_room):
    messages = [
        {
            "role": "system",
            "content": "You are Soulful AI. You have to help people with their mental problems. Don't snap back, be kind and responsive. Write your response in HTML format. Available tags: <b>, <i>, <u>, <br>, <ul><li>item</li></ul>",
        },
    ]
    messages.extend(queries)

    print(f"Number of tokens: {num_tokens_from_messages(messages)}")
    result = ""
    for chunk in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=2000,
        temperature=0.5,
        n=1,
        stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            result += content
            yield content
        elif chunk["choices"][0]["finish_reason"] == "stop":
            Message.objects.create(
                chat_room=chat_room,
                content=result,
                is_ai=True,
            )
