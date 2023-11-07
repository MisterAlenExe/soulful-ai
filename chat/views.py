import json

from django.shortcuts import render
from django.views.generic.edit import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, StreamingHttpResponse

import openai
import tiktoken
import os
from dotenv import load_dotenv

from .models import ChatRoom, Message

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

csrf_protect_m = method_decorator(csrf_protect)


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


class ChatPageView(LoginRequiredMixin, View):
    login_url = "/auth/login/"

    def generate_answer(self, queries, chat_room):
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

    def get(self, request, uuid=None):
        user = request.user
        chat_rooms = ChatRoom.objects.filter(created_by=user)
        if uuid is not None:
            current_room = ChatRoom.objects.get(uuid=uuid)
            if current_room is None:
                return render(request, "chat/chat.html", {"chat_rooms": chat_rooms})
            messages = Message.objects.filter(chat_room=current_room)
            return render(
                request,
                "chat/chat.html",
                {
                    "current_room": current_room,
                    "messages": messages,
                    "chat_rooms": chat_rooms,
                    "user": user,
                },
            )
        return render(request, "chat/chat.html", {"chat_rooms": chat_rooms})

    @csrf_protect_m
    def post(self, request):
        try:
            data = json.loads(request.body)
            prompt = data["prompt"]
            chat_room_id = data["chat_room_id"]

            chat_room = ChatRoom.objects.get(uuid=chat_room_id)

            print(prompt)

            Message.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=prompt,
                is_ai=False,
            )

            messages = Message.objects.filter(chat_room=chat_room)
            queries = []
            for message in messages:
                if message.is_ai:
                    queries.append({"role": "assistant", "content": message.content})
                else:
                    queries.append({"role": "user", "content": message.content})

            response = self.generate_answer(queries, chat_room)

            return StreamingHttpResponse(response)
        except Exception as e:
            print(e)
            return StreamingHttpResponse("Something went wrong")


class NewChatPageView(LoginRequiredMixin, View):
    login_url = "/auth/login/"

    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data["name"]

            chat_room = ChatRoom.objects.create(name=name, created_by=request.user)

            return JsonResponse(
                {"uuid": chat_room.uuid},
                status=201,
            )
        except Exception as e:
            print(e)
            return JsonResponse({"error": "Something went wrong"})
