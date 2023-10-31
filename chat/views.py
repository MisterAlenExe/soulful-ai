import json
from unittest import result
from django.shortcuts import render
from django.views.generic.edit import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import StreamingHttpResponse

import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

csrf_protect_m = method_decorator(csrf_protect)


class ChatPageView(LoginRequiredMixin, View):
    def generate_answer(self, query):
        for chunk in openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are Soulful AI. You have to help people with their mental problems. Don't snap back, be kind and responsive.",
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
            max_tokens=2000,
            temperature=0.9,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=["\n"],
            stream=True,
        ):
            content = chunk["choices"][0].get("delta", {}).get("content")
            if content is not None:
                yield content

    def get(self, request):
        return render(request, "chat/chat.html")

    @csrf_protect_m
    def post(self, request):
        try:
            data = json.loads(request.body)
            prompt = data["prompt"]

            print(prompt)

            response = self.generate_answer(prompt)

            return StreamingHttpResponse(response)
        except Exception as e:
            print(e)
            return StreamingHttpResponse("Something went wrong")
