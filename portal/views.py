from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RequestOrder
from .forms import UserRegistrationForm, RequestOrderForm


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
def profile(request):
    # Получаем все заявки текущего пользователя (сортировка от новых к старым задана в Meta модели)
    orders = RequestOrder.objects.filter(user=request.user)

    # Фильтрация по статусу (если передан GET-параметр ?status=...)
    status_filter = request.GET.get('status', '')
    if status_filter in ['new', 'in_progress', 'done']:
        orders = orders.filter(status=status_filter)

    return render(request, 'profile.html', {
        'orders': orders,
        'status_filter': status_filter,
    })


@login_required
def create_order(request):
    if request.method == 'POST':
        # Обязательно передаём request.FILES для загрузки изображения
        form = RequestOrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.status = 'new'  # Автоматически получает статус «Новая»
            order.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('profile')
    else:
        form = RequestOrderForm()

    return render(request, 'create_order.html', {'form': form})


@login_required
def delete_order(request, pk):
    # Ищем заявку строго среди заявок текущего пользователя
    order = get_object_or_404(RequestOrder, pk=pk, user=request.user)

    # Запрещаем удаление, если статус уже изменён администратором
    if order.status != 'new':
        messages.error(request, 'Нельзя удалить заявку, которая уже принята в работу или выполнена.')
        return redirect('profile')

    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Заявка успешно удалена.')
        return redirect('profile')

    return render(request, 'delete_order_confirm.html', {'order': order})
