from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth.models import User

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'Senha e confirmar senha não são iguais.')
            return redirect('cadastro')
        
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, 'Sua senha deve ter pelo meno 6 caracteres.')
            return redirect('cadastro')

        users = User.objects.filter(username=username)
        if users.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um usuário com esse username.')
            return redirect('cadastro')
        
        User.objects.create_user(
            username=username,
            password=senha
        )

        return redirect('login')

from django.contrib.auth import authenticate
from django.contrib import auth    

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(request, username=username,  password=senha)

        if user:
            auth.login(request, user)
            return redirect('treinar_ia')
        
        messages.add_message(request, constants.ERROR, 'Username ou senha inválidos.')
        return redirect('login')


def permissoes(request):
    print(request.user.is_superuser)
    if not request.user.is_superuser:
        raise Http404()
    users = User.objects.filter(is_superuser=False)
   
    return render(request, 'permissoes.html', {'users': users})

from rolepermissions.roles import assign_role

def tornar_gerente(request, id):
    user = User.objects.get(id=id)
    assign_role(user, 'gerente')
    return redirect('permissoes')