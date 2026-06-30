from django.contrib.auth.models import User
from django.shortcuts import render


def one_to_one_chat(request):
    users = User.objects.order_by('username')[:2]
    return render(request, 'chat.html', {'users': users})
