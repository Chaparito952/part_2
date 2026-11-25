from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import RequestOrder, Category
from .forms import (
    UserRegistrationForm,
    RequestOrderForm,
    CompleteOrderForm,
    InProgressOrderForm,
    CategoryForm,
)


def is_admin(user):
    return user.is_authenticated and user.is_staff


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
    if request.user.is_staff:
        return redirect('admin_dashboard')

    orders = RequestOrder.objects.filter(user=request.user)
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
        form = RequestOrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.status = 'new'
            order.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('profile')
    else:
        form = RequestOrderForm()

    return render(request, 'create_order.html', {'form': form})


@login_required
def delete_order(request, pk):
    order = get_object_or_404(RequestOrder, pk=pk, user=request.user)

    if order.status != 'new':
        messages.error(request, 'Нельзя удалить заявку, которая уже принята в работу или выполнена.')
        return redirect('profile')

    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Заявка успешно удалена.')
        return redirect('profile')

    return render(request, 'delete_order_confirm.html', {'order': order})


@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    orders = RequestOrder.objects.all()
    categories = Category.objects.all()
    category_form = CategoryForm()

    return render(request, 'admin_dashboard.html', {
        'orders': orders,
        'categories': categories,
        'category_form': category_form,
    })


@user_passes_test(is_admin, login_url='login')
def set_order_in_progress(request, pk):
    order = get_object_or_404(RequestOrder, pk=pk)

    if order.status != 'new':
        messages.error(request, 'Сменить статус можно только у заявки со статусом «Новая».')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = InProgressOrderForm(request.POST, instance=order)
        if form.is_valid():
            updated_order = form.save(commit=False)
            updated_order.status = 'in_progress'
            updated_order.save()
            messages.success(request, f'Заявка «{order.title}» принята в работу.')
            return redirect('admin_dashboard')
    else:
        form = InProgressOrderForm(instance=order)

    return render(request, 'admin_order_status.html', {
        'order': order,
        'form': form,
        'target_status': 'Принято в работу',
    })


@user_passes_test(is_admin, login_url='login')
def set_order_done(request, pk):
    order = get_object_or_404(RequestOrder, pk=pk)

    if order.status != 'new':
        messages.error(request, 'Сменить статус можно только у заявки со статусом «Новая».')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = CompleteOrderForm(request.POST, request.FILES, instance=order)
        if form.is_valid():
            updated_order = form.save(commit=False)
            updated_order.status = 'done'
            updated_order.save()
            messages.success(request, f'Заявка «{order.title}» переведена в статус «Выполнено».')
            return redirect('admin_dashboard')
    else:
        form = CompleteOrderForm(instance=order)

    return render(request, 'admin_order_status.html', {
        'order': order,
        'form': form,
        'target_status': 'Выполнено',
    })


@user_passes_test(is_admin, login_url='login')
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно добавлена.')
    return redirect('admin_dashboard')


@user_passes_test(is_admin, login_url='login')
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Категория «{category_name}» и все связанные с ней заявки удалены.')
        return redirect('admin_dashboard')

    return render(request, 'delete_category_confirm.html', {'category': category})
