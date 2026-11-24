from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import RequestOrder
from .forms import UserRegistrationForm


def index(request):
    done_orders = RequestOrder.objects.filter(status='done')[:4]
    in_progress_count = RequestOrder.objects.filter(status='in_progress').count()

    return render(request, 'index.html', {
        'done_orders': done_orders,
        'in_progress_count': in_progress_count,
    })


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['full_name']
            )
            login(request, user)
            return redirect('profile')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_stub(request):
    # Временная заглушка личного кабинета (доступна только авторизованным)
    return render(request, 'profile_stub.html')
