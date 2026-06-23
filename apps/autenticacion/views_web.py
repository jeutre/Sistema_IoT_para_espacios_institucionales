from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def login_web(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        usuario  = authenticate(request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            from .models import SesionUsuario
            ip = request.META.get('REMOTE_ADDR')
            SesionUsuario.objects.create(usuario=usuario, ip=ip)
            return redirect('dashboard')
        else:
            error = 'Usuario o contraseña incorrectos.'

    return render(request, 'autenticacion.html', {'error': error})


@login_required
def logout_web(request):
    from .models import SesionUsuario
    SesionUsuario.objects.filter(
        usuario=request.user, activa=True
    ).update(activa=False)
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    return render(request, 'dashboard/index.html')