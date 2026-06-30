import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .models import Message


def ensure_demo_users():
    User = get_user_model()
    if not User.objects.filter(username='alice').exists():
        User.objects.create_user(username='alice', password='password123')
    if not User.objects.filter(username='bob').exists():
        User.objects.create_user(username='bob', password='password123')


def login_page(request):
    ensure_demo_users()
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('one_to_one_chat')
        return render(request, 'login.html', {'error': 'Invalid username or password', 'username': username})
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def one_to_one_chat(request):
    ensure_demo_users()
    User = get_user_model()
    users = User.objects.order_by('username')[:2]
    messages = Message.objects.select_related('sender', 'receiver').order_by('created_at')
    return render(request, 'chat.html', {'users': users, 'messages': messages, 'current_user': request.user})


def send_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST is allowed.'}, status=405)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        data = request.POST

    content = (data.get('content') or '').strip()

    if not content:
        return JsonResponse({'error': 'Content is required.'}, status=400)

    User = get_user_model()
    users = list(User.objects.order_by('username')[:2])
    if len(users) < 2:
        return JsonResponse({'error': 'At least two users are required.'}, status=400)

    sender = request.user if request.user.is_authenticated else None
    if sender is None:
        return JsonResponse({'error': 'You must be logged in.'}, status=401)

    receiver = users[1] if sender == users[0] else users[0]

    message = Message.objects.create(sender=sender, receiver=receiver, content=content)
    return JsonResponse({
        'message': {
            'id': message.id,
            'sender': sender.username,
            'receiver': receiver.username,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
        }
    })


def poll_messages(request):
    after_id = request.GET.get('after_id', 0)
    try:
        after_id = int(after_id)
    except (TypeError, ValueError):
        after_id = 0

    messages = Message.objects.filter(id__gt=after_id).select_related('sender', 'receiver').order_by('created_at')
    payload = [{
        'id': message.id,
        'sender': message.sender.username,
        'receiver': message.receiver.username,
        'content': message.content,
        'created_at': message.created_at.isoformat(),
    } for message in messages]
    return JsonResponse({'messages': payload})
