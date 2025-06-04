from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Category, Product, Order, OrderItem
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .forms import OrderCreateForm, UserRegistrationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .cart import Cart

@login_required
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.filter(parent__isnull=True)
    products = Product.objects.filter(available=True)
    query = request.GET.get('query', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    if query:
        products = products.filter(name__icontains=query)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
        
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        # Получаем все дочерние категории
        subcategories = category.children.all()
        if subcategories.exists():
            # Если есть дочерние категории, показываем товары из них
            products = products.filter(category__in=subcategories)
        else:
            # Если нет дочерних категорий, показываем товары текущей категории
            products = products.filter(category=category)
            
    return render(request, 'store/product/list.html',
                 {'category': category,
                  'categories': categories,
                  'products': products,
                  'query': query,
                  'min_price': min_price,
                  'max_price': max_price})

@login_required
def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'store/product/detail.html', {'product': product})

@login_required
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart/detail.html', {'cart': cart})

@login_required
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Проверяем наличие товара
    if product.stock < quantity:
        messages.error(request, f'Товар "{product.name}" доступен только в количестве {product.stock} шт.')
        return redirect('store:product_detail', id=product_id, slug=product.slug)
    
    # Проверяем, сколько товара уже в корзине
    current_quantity = cart.get_quantity(product)
    if current_quantity + quantity > product.stock:
        messages.error(request, f'Вы уже добавили {current_quantity} шт. товара "{product.name}". Доступно только {product.stock} шт.')
        return redirect('store:product_detail', id=product_id, slug=product.slug)
    
    cart.add(product=product, quantity=quantity)
    messages.success(request, f'Товар "{product.name}" добавлен в корзину')
    return redirect('store:cart_detail')

@login_required
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'Товар "{product.name}" удален из корзины')
    return redirect('store:cart_detail')

@login_required
@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Проверяем наличие товара
    if product.stock < quantity:
        messages.error(request, f'Товар "{product.name}" доступен только в количестве {product.stock} шт.')
        return redirect('store:cart_detail')
    
    cart.update(product=product, quantity=quantity)
    messages.success(request, f'Количество товара "{product.name}" обновлено')
    return redirect('store:cart_detail')

@login_required
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Проверяем наличие всех товаров
            for item in cart:
                product = item['product']
                if product.stock < item['quantity']:
                    messages.error(request, f'Товар "{product.name}" доступен только в количестве {product.stock} шт.')
                    return redirect('store:cart_detail')
            
            # Создаем заказ
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            
            # Создаем элементы заказа и списываем товары со склада
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
                # Списываем товары со склада
                product = item['product']
                product.stock -= item['quantity']
                product.save()
            
            # Очищаем корзину
            cart.clear()
            
            messages.success(request, 'Ваш заказ успешно создан!')
            return redirect('store:order_detail', order_id=order.id)
    else:
        form = OrderCreateForm()
    return render(request, 'store/order/create.html', {'cart': cart, 'form': form})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'store/order/list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order/detail.html', {'order': order})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'store/profile.html', {'orders': orders})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('store:product_list')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'store:product_list')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    
    return render(request, 'store/login.html')

def user_logout(request):
    logout(request)
    return redirect('store:product_list')

def register(request):
    if request.user.is_authenticated:
        return redirect('store:product_list')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('store:product_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'store/register.html', {'form': form})
