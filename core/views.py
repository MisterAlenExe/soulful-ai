import os

import openai
from django.http import StreamingHttpResponse
from django.views import View
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


class ChatView(View):
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
        query = "I got fired from my job today. I don't know what to do."
        response = StreamingHttpResponse(
            self.generate_answer(query), content_type="text/html"
        )
        return response
