from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle
from openai import OpenAI
from django.conf import settings
from django.urls import reverse
from .models import Chat

@api_view(['POST',])
@throttle_classes([UserRateThrottle,])
def single_prompt(request):
    prompt = request.data.get('prompt', None)
    if not prompt:
        return Response({"error": "Prompt field is required"}, status=status.HTTP_400_BAD_REQUEST)
    chat = Chat(prompt=prompt, user=request.user)
    client = OpenAI(api_key=settings.OPENAI_SECRET_KEY)
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ]
        )
    except Exception as e:
        chat.save()
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    chat.response = completion.choices[0].message.content
    chat.save()
    if request.user.is_subscribed():
        response = {"response": completion.choices[0].message.content}
    else:
        response = {
            "response": completion.choices[0].message.content[:250]+"...[Please subscribe via provided subscription-url to see full response. You can examine all your chat history via chat-history endpoint after subscription.]",
            "subscription-url": settings.BASE_URL + reverse('subscribe'),
            "chat-history endpoint": settings.BASE_URL + reverse('chat_history')
        }
    return Response(response)

@api_view(['GET'])
@throttle_classes([UserRateThrottle])
def chat_history(request):
    if not request.user.is_subscribed():
        return Response({"message": "Only subscribed users can access this endpoint"}, status=status.HTTP_402_PAYMENT_REQUIRED)
    history_queryset = Chat.objects.filter(user=request.user).order_by('created_at')
    history = []
    for item in history_queryset:
        history.append(
            {
                "prompt": item.prompt,
                "response": item.response,
                "date": item.created_at
            }
        )
    return Response(history)
