from decimal import Decimal
from django.conf import settings
from store.models import Product

class Cart:
    def __init__(self, request):
        """Инициализация корзины."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # сохраняем пустую корзину в сессии
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        """Добавление товара в корзину или обновление его количества."""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        self.cart[product_id]['quantity'] = quantity
        self.save()

    def update(self, product, quantity=1):
        """Обновление количества товара в корзине."""
        product_id = str(product.id)
        if product_id in self.cart:
            if isinstance(self.cart[product_id], dict):
                self.cart[product_id]['quantity'] = quantity
            else:
                # Конвертируем старый формат в новый
                self.cart[product_id] = {
                    'quantity': quantity,
                    'price': str(product.price)
                }
            self.save()

    def save(self):
        """Сохранение корзины в сессии."""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        """Удаление товара из корзины."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Перебор элементов в корзине и получение товаров из базы данных."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            product_id = str(product.id)
            if product_id in cart:
                item = cart[product_id]
                if isinstance(item, dict):
                    # Новый формат
                    item['product'] = product
                    item['price'] = Decimal(item['price'])
                    item['total_price'] = item['price'] * item['quantity']
                    yield item
                elif isinstance(item, int):
                    # Старый формат
                    price = product.price
                    yield {
                        'product': product,
                        'quantity': item,
                        'price': price,
                        'total_price': price * item
                    }

    def get_quantity(self, product):
        """Получение количества товара в корзине."""
        product_id = str(product.id)
        item = self.cart.get(product_id)
        if isinstance(item, dict):
            return item.get('quantity', 0)
        elif isinstance(item, int):
            # старый формат, для совместимости
            return item
        return 0

    def get_total_price(self):
        """Подсчет общей стоимости товаров в корзине."""
        total = Decimal('0')
        for item in self:
            total += item['total_price']
        return total

    def clear(self):
        """Удаление корзины из сессии."""
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True 