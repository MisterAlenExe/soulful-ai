import json

from django.shortcuts import render
from django.views.generic.edit import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, StreamingHttpResponse

from .models import ChatRoom, Message
from .utils import generate_answer, format_time_difference


csrf_protect_m = method_decorator(csrf_protect)


class ChatPageView(LoginRequiredMixin, View):
    login_url = "/auth/login/"

    def get(self, request, uuid=None):
        user = request.user
        chat_rooms = ChatRoom.objects.filter(created_by=user).order_by("-created_at")
        for room in chat_rooms:
            room.created_at = format_time_difference(room.created_at)
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

            messages = Message.objects.filter(chat_room=chat_room)[:4:-1]
            queries = []
            for message in messages:
                print(message.content)
                if message.is_ai:
                    queries.append({"role": "assistant", "content": message.content})
                else:
                    queries.append({"role": "user", "content": message.content})

            response = generate_answer(queries, chat_room)

            return StreamingHttpResponse(response)
        except Exception as e:
            print(e)
            return StreamingHttpResponse("Something went wrong")

    def delete(self, request, uuid):
        try:
            chat_room = ChatRoom.objects.get(
                uuid=uuid,
                created_by=request.user,
            )
            chat_room.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            print(e)
            return JsonResponse({"error": "Something went wrong"})


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
