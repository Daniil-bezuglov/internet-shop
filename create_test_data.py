import os
import django
import random
import urllib.request
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()

from store.models import Category, Product, Order, OrderItem
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

# Удаляем все заказы, товары и категории
OrderItem.objects.all().delete()
Order.objects.all().delete()
Product.objects.all().delete()
Category.objects.all().delete()

# Функция транслитерации для слага
def slugify(value):
    mapping = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m',
        'н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sch',
        'ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya'
    }
    value = value.lower()
    value = ''.join(mapping.get(c, c) for c in value)
    value = re.sub(r'[^a-z0-9_-]', '-', value)
    value = re.sub(r'-+', '-', value)
    return value.strip('-')

# Категории и подкатегории
category_structure = {
    'Смартфоны': ['Android', 'iOS', 'Кнопочные'],
    'Ноутбуки': ['Windows-ноутбуки', 'MacBook', 'Chromebook'],
    'Аксессуары': ['Чехлы', 'Зарядные устройства', 'Кабели', 'Переходники'],
    'Телевизоры': ['4K', '8K', 'Full HD'],
    'Планшеты': ['Android-планшеты', 'iPad'],
}

# Создание категорий и подкатегорий
category_objs = {}
subcategory_objs = {}

for cat_name, subcats in category_structure.items():
    cat_slug = slugify(cat_name)
    cat, _ = Category.objects.get_or_create(name=cat_name, slug=cat_slug, parent=None)
    category_objs[cat_slug] = cat
    subcategory_objs[cat_slug] = []
    for subcat_name in subcats:
        subcat_slug = slugify(subcat_name)
        subcat, _ = Category.objects.get_or_create(name=subcat_name, slug=subcat_slug, parent=cat)
        subcategory_objs[cat_slug].append(subcat)

# Примеры картинок (можно добавить свои)
image_urls = [
    'https://images.unsplash.com/photo-1631701179964-6b2b1b1b1b1b?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=600&q=80',
    'https://images.samsung.com/is/image/samsung/p6pim/ru/qa55q60aauxru/gallery/ru-qled-q60aauxru-411594-qa55q60aauxru-530347406?$650_519_PNG$',
    'https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/airtag-single-select-202104?wid=470&hei=556&fmt=png-alpha&.v=1617761672000',
    'https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SL1500_.jpg',
    'https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/MKU93_VW_34FR+watch-45-alum-silver-cell-7s_VW_34FR_WF_CO_GEO_RU?wid=2000&hei=2000&fmt=jpeg&qlt=95&.v=1632171067000',
    'https://www.canon.ru/media/EOS-R6-front_tcm87-1917272.png',
]

# Реальные товары по подкатегориям
real_products = [
    # Смартфоны - Android
    {
        'category': 'android',
        'name': 'Samsung Galaxy S24 Ultra',
        'slug': 'samsung-galaxy-s24-ultra',
        'short_description': 'Флагман Samsung 2024 года',
        'description': 'Samsung Galaxy S24 Ultra — это топовый смартфон с камерой 200 Мп, AMOLED-экраном 6.8", поддержкой S Pen и мощным процессором Snapdragon 8 Gen 3.',
        'features': [
            {'Дисплей': '6.8" AMOLED, 120 Гц'},
            {'Камера': '200 Мп + 12 Мп + 10 Мп + 50 Мп'},
            {'Батарея': '5000 мАч'}
        ],
        'price': 120000,
        'stock': 3,
        'image_url': image_urls[0],
    },
    {
        'category': 'android',
        'name': 'Xiaomi 14 Pro',
        'slug': 'xiaomi-14-pro',
        'short_description': 'Флагман Xiaomi с AMOLED-экраном',
        'description': 'Xiaomi 14 Pro — мощный смартфон с AMOLED-экраном, быстрой зарядкой и камерой Leica.',
        'features': [
            {'Дисплей': '6.73" AMOLED, 120 Гц'},
            {'Камера': '50 Мп + 50 Мп + 50 Мп'},
            {'Зарядка': '120 Вт'}
        ],
        'price': 70000,
        'stock': 0,
        'image_url': image_urls[1],
    },
    {
        'category': 'android',
        'name': 'Google Pixel 8',
        'slug': 'google-pixel-8',
        'short_description': 'Чистый Android и отличная камера',
        'description': 'Google Pixel 8 — смартфон с лучшей камерой и чистым Android.',
        'features': [
            {'Дисплей': '6.2" OLED, 120 Гц'},
            {'Камера': '50 Мп + 12 Мп'},
            {'Процессор': 'Google Tensor G3'}
        ],
        'price': 80000,
        'stock': 15,
        'image_url': image_urls[2],
    },
    {
        'category': 'android',
        'name': 'OnePlus 12',
        'slug': 'oneplus-12',
        'short_description': 'Быстрый смартфон с зарядкой 100W',
        'description': 'OnePlus 12 — производительный смартфон с быстрой зарядкой и плавным экраном.',
        'features': [
            {'Дисплей': '6.82" AMOLED, 120 Гц'},
            {'Зарядка': '100 Вт'},
            {'Память': '12/256 ГБ'}
        ],
        'price': 65000,
        'stock': 3,
        'image_url': image_urls[3],
    },
    {
        'category': 'android',
        'name': 'realme GT 5',
        'slug': 'realme-gt-5',
        'short_description': 'Игровой смартфон с мощным процессором',
        'description': 'realme GT 5 — смартфон для игр с высокой производительностью и быстрой зарядкой.',
        'features': [
            {'Процессор': 'Snapdragon 8 Gen 2'},
            {'Зарядка': '150 Вт'},
            {'Экран': '6.74" AMOLED'}
        ],
        'price': 50000,
        'stock': 0,
        'image_url': image_urls[4],
    },
    {
        'category': 'android',
        'name': 'HONOR Magic6 Pro',
        'slug': 'honor-magic6-pro',
        'short_description': 'Смартфон с отличной автономностью',
        'description': 'HONOR Magic6 Pro — смартфон с большой батареей и камерой высокого разрешения.',
        'features': [
            {'Батарея': '5600 мАч'},
            {'Камера': '180 Мп'},
            {'Экран': '6.8" OLED'}
        ],
        'price': 60000,
        'stock': 4,
        'image_url': image_urls[5],
    },
    {
        'category': 'android',
        'name': 'OPPO Find X6',
        'slug': 'oppo-find-x6',
        'short_description': 'Флагман OPPO с топовой камерой',
        'description': 'OPPO Find X6 — смартфон с камерой Hasselblad и ярким дисплеем.',
        'features': [
            {'Камера': '50 Мп + 50 Мп + 50 Мп'},
            {'Дисплей': '6.82" AMOLED'},
            {'Память': '16/512 ГБ'}
        ],
        'price': 85000,
        'stock': 2,
        'image_url': image_urls[6],
    },
    {
        'category': 'android',
        'name': 'Vivo X100 Pro',
        'slug': 'vivo-x100-pro',
        'short_description': 'Смартфон с Zeiss-оптикой',
        'description': 'Vivo X100 Pro — камерафон с оптикой Zeiss и отличной автономностью.',
        'features': [
            {'Камера': '50 Мп + 50 Мп + 64 Мп'},
            {'Оптика': 'Zeiss'},
            {'Батарея': '5400 мАч'}
        ],
        'price': 90000,
        'stock': 1,
        'image_url': image_urls[7],
    },
    # Смартфоны - iOS
    {
        'category': 'ios',
        'name': 'iPhone 15 Pro Max',
        'slug': 'iphone-15-pro-max',
        'short_description': 'Флагман Apple 2024 года',
        'description': 'iPhone 15 Pro Max — топовый смартфон Apple с процессором A17 и ProMotion-дисплеем.',
        'features': [
            {'Дисплей': '6.7" OLED, 120 Гц'},
            {'Камера': '48 Мп + 12 Мп + 12 Мп'},
            {'Процессор': 'Apple A17 Pro'}
        ],
        'price': 150000,
        'stock': 2,
        'image_url': image_urls[2],
    },
    {
        'category': 'ios',
        'name': 'iPhone 14',
        'slug': 'iphone-14',
        'short_description': 'Смартфон Apple iPhone 14 128GB',
        'description': 'iPhone 14 — сбалансированный смартфон Apple с отличной камерой и автономностью.',
        'features': [
            {'Дисплей': '6.1" OLED'},
            {'Камера': '12 Мп + 12 Мп'},
            {'Процессор': 'Apple A15 Bionic'}
        ],
        'price': 95000,
        'stock': 8,
        'image_url': image_urls[0],
    },
    {
        'category': 'ios',
        'name': 'iPhone 13 mini',
        'slug': 'iphone-13-mini',
        'short_description': 'Компактный iPhone с отличной камерой',
        'description': 'iPhone 13 mini — маленький, но мощный смартфон Apple.',
        'features': [
            {'Дисплей': '5.4" OLED'},
            {'Камера': '12 Мп + 12 Мп'},
            {'Процессор': 'Apple A15 Bionic'}
        ],
        'price': 70000,
        'stock': 0,
        'image_url': image_urls[1],
    },
    {
        'category': 'ios',
        'name': 'iPhone SE (2022)',
        'slug': 'iphone-se-2022',
        'short_description': 'Доступный iPhone с мощным процессором',
        'description': 'iPhone SE — компактный смартфон Apple с процессором от флагмана.',
        'features': [
            {'Дисплей': '4.7" Retina'},
            {'Камера': '12 Мп'},
            {'Процессор': 'Apple A15 Bionic'}
        ],
        'price': 50000,
        'stock': 12,
        'image_url': image_urls[3],
    },
    {
        'category': 'ios',
        'name': 'iPhone 12',
        'slug': 'iphone-12',
        'short_description': 'Классика Apple с OLED-экраном',
        'description': 'iPhone 12 — популярный смартфон Apple с OLED-экраном и поддержкой 5G.',
        'features': [
            {'Дисплей': '6.1" OLED'},
            {'Камера': '12 Мп + 12 Мп'},
            {'Процессор': 'Apple A14 Bionic'}
        ],
        'price': 60000,
        'stock': 4,
        'image_url': image_urls[4],
    },
    {
        'category': 'ios',
        'name': 'iPhone 11',
        'slug': 'iphone-11',
        'short_description': 'Популярный iPhone с двойной камерой',
        'description': 'iPhone 11 — смартфон Apple с отличной камерой и автономностью.',
        'features': [
            {'Дисплей': '6.1" IPS'},
            {'Камера': '12 Мп + 12 Мп'},
            {'Процессор': 'Apple A13 Bionic'}
        ],
        'price': 45000,
        'stock': 0,
        'image_url': image_urls[5],
    },
    # Смартфоны - Кнопочные
    {
        'category': 'knopochnye',
        'name': 'Nokia 3310',
        'slug': 'nokia-3310',
        'short_description': 'Легендарный кнопочный телефон',
        'description': 'Nokia 3310 — легендарный кнопочный телефон с невероятной прочностью и долгой работой от батареи.',
        'features': [
            {'Батарея': '1200 мАч'},
            {'Время работы': 'до 22 часов в режиме разговора'},
            {'Прочность': 'Ударопрочный корпус'}
        ],
        'price': 3500,
        'stock': 25,
        'image_url': image_urls[3]
    },
    {
        'category': 'knopochnye',
        'name': 'Philips Xenium E570',
        'slug': 'philips-xenium-e570',
        'short_description': 'Телефон с рекордной автономностью',
        'description': 'Philips Xenium E570 — кнопочный телефон с рекордной автономностью.',
        'features': [
            {'Батарея': '1800 мАч'},
            {'Время работы': 'до 30 дней в режиме ожидания'},
            {'Фонарик': 'Мощный LED-фонарик'}
        ],
        'price': 4000,
        'stock': 3,
        'image_url': image_urls[4]
    },
    {
        'category': 'knopochnye',
        'name': 'Alcatel 2008G',
        'slug': 'alcatel-2008g',
        'short_description': 'Простой и надёжный телефон',
        'description': 'Alcatel 2008G — простой и надёжный кнопочный телефон с базовым набором функций.',
        'features': [
            {'Батарея': '1000 мАч'},
            {'Экран': '2.4" TFT'},
            {'FM-радио': 'Встроенный радиоприёмник'}
        ],
        'price': 2500,
        'stock': 0,
        'image_url': image_urls[5]
    },
    {
        'category': 'knopochnye',
        'name': 'Nokia 105',
        'slug': 'nokia-105',
        'short_description': 'Бюджетный телефон с фонариком',
        'description': 'Nokia 105 — доступный кнопочный телефон с встроенным фонариком и FM-радио.',
        'features': [
            {'Батарея': '800 мАч'},
            {'Фонарик': 'Встроенный LED-фонарик'},
            {'Радио': 'FM-радио с наушниками'}
        ],
        'price': 1500,
        'stock': 7,
        'image_url': image_urls[6]
    },

    # Ноутбуки - Windows-ноутбуки
    {
        'category': 'windows-noutbuki',
        'name': 'Lenovo ThinkPad X1 Carbon',
        'slug': 'lenovo-thinkpad-x1-carbon',
        'short_description': 'Премиальный бизнес-ноутбук',
        'description': 'Lenovo ThinkPad X1 Carbon — премиальный бизнес-ноутбук с превосходной клавиатурой и прочным корпусом.',
        'features': [
            {'Процессор': 'Intel Core i7 13-го поколения'},
            {'Память': '16 ГБ RAM, 512 ГБ SSD'},
            {'Экран': '14" 4K IPS'}
        ],
        'price': 110000,
        'stock': 2,
        'image_url': image_urls[4]
    },
    {
        'category': 'windows-noutbuki',
        'name': 'ASUS ZenBook 14',
        'slug': 'asus-zenbook-14',
        'short_description': 'Стильный ультрабук с OLED-экраном',
        'description': 'ASUS ZenBook 14 — стильный ультрабук с OLED-экраном и инновационным тачпадом-дисплеем.',
        'features': [
            {'Процессор': 'Intel Core i5 13-го поколения'},
            {'Экран': '14" OLED, 90 Гц'},
            {'Вес': '1.2 кг'}
        ],
        'price': 90000,
        'stock': 5,
        'image_url': image_urls[5]
    },
    {
        'category': 'windows-noutbuki',
        'name': 'HP Spectre x360',
        'slug': 'hp-spectre-x360',
        'short_description': 'Премиальный трансформер',
        'description': 'HP Spectre x360 — премиальный трансформер с отличным дисплеем и стильным дизайном.',
        'features': [
            {'Процессор': 'Intel Core i7 13-го поколения'},
            {'Экран': '13.5" 3K2K OLED'},
            {'Стилус': 'HP Rechargeable MPP2.0 Tilt Pen'}
        ],
        'price': 120000,
        'stock': 0,
        'image_url': image_urls[6]
    },
    {
        'category': 'windows-noutbuki',
        'name': 'Dell XPS 13',
        'slug': 'dell-xps-13',
        'short_description': 'Компактный ноутбук с тонкими рамками',
        'description': 'Dell XPS 13 — компактный ноутбук с минимальными рамками экрана и премиальным дизайном.',
        'features': [
            {'Процессор': 'Intel Core i5 13-го поколения'},
            {'Экран': '13.4" 4K UHD+'},
            {'Вес': '1.17 кг'}
        ],
        'price': 100000,
        'stock': 3,
        'image_url': image_urls[7]
    },

    # Ноутбуки - MacBook
    {
        'category': 'macbook',
        'name': 'MacBook Pro 16\" M3',
        'slug': 'macbook-pro-16-m3',
        'short_description': 'Мощный MacBook Pro на чипе M3',
        'description': 'MacBook Pro 16\" с чипом M3 — самый мощный ноутбук Apple для профессионалов.',
        'features': [
            {'Процессор': 'Apple M3 Pro/Max'},
            {'Экран': '16" Liquid Retina XDR'},
            {'Память': 'до 128 ГБ RAM'}
        ],
        'price': 250000,
        'stock': 1,
        'image_url': image_urls[6]
    },
    {
        'category': 'macbook',
        'name': 'MacBook Air 15\"',
        'slug': 'macbook-air-15',
        'short_description': 'Тонкий и лёгкий MacBook Air',
        'description': 'MacBook Air 15\" — тонкий и лёгкий ноутбук с большим экраном и отличной автономностью.',
        'features': [
            {'Процессор': 'Apple M2'},
            {'Экран': '15" Liquid Retina'},
            {'Вес': '1.51 кг'}
        ],
        'price': 140000,
        'stock': 8,
        'image_url': image_urls[1]
    },
    {
        'category': 'macbook',
        'name': 'MacBook Pro 14\" M2',
        'slug': 'macbook-pro-14-m2',
        'short_description': 'Профессиональный MacBook Pro',
        'description': 'MacBook Pro 14\" с чипом M2 — профессиональный ноутбук с отличной производительностью.',
        'features': [
            {'Процессор': 'Apple M2 Pro/Max'},
            {'Экран': '14" Liquid Retina XDR'},
            {'Память': 'до 64 ГБ RAM'}
        ],
        'price': 210000,
        'stock': 4,
        'image_url': image_urls[2]
    },

    # Ноутбуки - Chromebook
    {
        'category': 'chromebook',
        'name': 'Acer Chromebook Spin 713',
        'slug': 'acer-chromebook-spin-713',
        'short_description': 'Мощный Chromebook с сенсорным экраном',
        'description': 'Acer Chromebook Spin 713 — мощный Chromebook с сенсорным экраном и отличной производительностью.',
        'features': [
            {'Процессор': 'Intel Core i5 11-го поколения'},
            {'Экран': '13.5" 2K IPS'},
            {'Автономность': 'до 10 часов'}
        ],
        'price': 60000,
        'stock': 6,
        'image_url': image_urls[2]
    },
    {
        'category': 'chromebook',
        'name': 'HP Chromebook x360',
        'slug': 'hp-chromebook-x360',
        'short_description': 'Универсальный Chromebook-трансформер',
        'description': 'HP Chromebook x360 — универсальный трансформер с Chrome OS.',
        'features': [
            {'Процессор': 'Intel Pentium Gold'},
            {'Экран': '14" Full HD IPS'},
            {'Стилус': 'HP Active Pen'}
        ],
        'price': 45000,
        'stock': 0,
        'image_url': image_urls[3]
    },
    {
        'category': 'chromebook',
        'name': 'Lenovo IdeaPad Flex 5',
        'slug': 'lenovo-ideapad-flex-5',
        'short_description': 'Доступный Chromebook для учёбы',
        'description': 'Lenovo IdeaPad Flex 5 — доступный Chromebook с сенсорным экраном и стилусом.',
        'features': [
            {'Процессор': 'MediaTek MT8183'},
            {'Экран': '13.3" Full HD IPS'},
            {'Стилус': 'В комплекте'}
        ],
        'price': 40000,
        'stock': 10,
        'image_url': image_urls[4]
    },

    # Аксессуары - Чехлы
    {
        'category': 'chehly',
        'name': 'Чехол для iPhone 15 Pro Max',
        'slug': 'case-iphone-15-pro-max',
        'short_description': 'Прочный силиконовый чехол',
        'description': 'Оригинальный силиконовый чехол для iPhone 15 Pro Max с защитой от ударов и стильным дизайном.',
        'features': [
            {'Материал': 'Силикон'},
            {'Защита': 'Ударопрочный'},
            {'Цвета': '5 вариантов'}
        ],
        'price': 2500,
        'stock': 15,
        'image_url': image_urls[3]
    },
    {
        'category': 'chehly',
        'name': 'Чехол для Samsung Galaxy S24',
        'slug': 'case-galaxy-s24',
        'short_description': 'Стильный чехол для Galaxy S24',
        'description': 'Стильный чехол для Samsung Galaxy S24 с защитой от царапин и ударов.',
        'features': [
            {'Материал': 'Поликарбонат'},
            {'Защита': 'Ударопрочный'},
            {'Дизайн': 'Прозрачный'}
        ],
        'price': 2000,
        'stock': 3,
        'image_url': image_urls[4]
    },
    {
        'category': 'chehly',
        'name': 'Чехол для Xiaomi 14 Pro',
        'slug': 'case-xiaomi-14-pro',
        'short_description': 'Прозрачный чехол для Xiaomi',
        'description': 'Прозрачный защитный чехол для Xiaomi 14 Pro с защитой от царапин.',
        'features': [
            {'Материал': 'TPU'},
            {'Защита': 'От царапин'},
            {'Толщина': '1.2 мм'}
        ],
        'price': 1500,
        'stock': 0,
        'image_url': image_urls[5]
    },

    # Аксессуары - Зарядные устройства
    {
        'category': 'zaryadnye-ustroystva',
        'name': 'Сетевое зарядное устройство Anker',
        'slug': 'anker-charger',
        'short_description': 'Быстрая зарядка 65W',
        'description': 'Мощное сетевое зарядное устройство Anker с поддержкой быстрой зарядки для ноутбуков и смартфонов.',
        'features': [
            {'Мощность': '65 Вт'},
            {'Порты': 'USB-C'},
            {'Поддержка': 'PD 3.0'}
        ],
        'price': 3500,
        'stock': 8,
        'image_url': image_urls[4]
    },
    {
        'category': 'zaryadnye-ustroystva',
        'name': 'Apple MagSafe Charger',
        'slug': 'apple-magsafe-charger',
        'short_description': 'Беспроводная зарядка для iPhone',
        'description': 'Оригинальное беспроводное зарядное устройство Apple MagSafe для iPhone с магнитным креплением.',
        'features': [
            {'Мощность': '15 Вт'},
            {'Тип': 'Беспроводная'},
            {'Магнит': 'MagSafe'}
        ],
        'price': 5000,
        'stock': 2,
        'image_url': image_urls[5]
    },
    {
        'category': 'zaryadnye-ustroystva',
        'name': 'Samsung 25W Charger',
        'slug': 'samsung-25w-charger',
        'short_description': 'Оригинальная зарядка Samsung',
        'description': 'Оригинальное зарядное устройство Samsung с поддержкой быстрой зарядки Super Fast Charging.',
        'features': [
            {'Мощность': '25 Вт'},
            {'Порты': 'USB-C'},
            {'Поддержка': 'Super Fast Charging'}
        ],
        'price': 2500,
        'stock': 5,
        'image_url': image_urls[6]
    },

    # Аксессуары - Кабели
    {
        'category': 'kabeli',
        'name': 'Кабель USB-C — Lightning',
        'slug': 'usb-c-lightning-cable',
        'short_description': 'Оригинальный кабель Apple',
        'description': 'Оригинальный кабель Apple для быстрой зарядки и синхронизации iPhone с поддержкой USB-C.',
        'features': [
            {'Длина': '1 м'},
            {'Скорость': '480 Мбит/с'},
            {'Зарядка': 'Быстрая'}
        ],
        'price': 2500,
        'stock': 20,
        'image_url': image_urls[0]
    },
    {
        'category': 'kabeli',
        'name': 'Кабель Baseus USB-C — USB-C',
        'slug': 'baseus-usbc-usbc-cable',
        'short_description': 'Качественный кабель для зарядки',
        'description': 'Высококачественный кабель Baseus для быстрой зарядки ноутбуков и смартфонов с USB-C портами.',
        'features': [
            {'Длина': '2 м'},
            {'Скорость': '10 Гбит/с'},
            {'Мощность': '100 Вт'}
        ],
        'price': 1200,
        'stock': 4,
        'image_url': image_urls[1]
    },
    {
        'category': 'kabeli',
        'name': 'Кабель Samsung USB-A — USB-C',
        'slug': 'samsung-usba-usbc-cable',
        'short_description': 'Надёжный кабель Samsung',
        'description': 'Оригинальный кабель Samsung для быстрой передачи данных и зарядки устройств.',
        'features': [
            {'Длина': '1 м'},
            {'Скорость': '480 Мбит/с'},
            {'Зарядка': 'Быстрая'}
        ],
        'price': 900,
        'stock': 0,
        'image_url': image_urls[2]
    },

    # Аксессуары - Переходники
    {
        'category': 'perehodniki',
        'name': 'Переходник USB-C — HDMI',
        'slug': 'usbc-hdmi-adapter',
        'short_description': 'Для подключения к монитору',
        'description': 'Универсальный переходник для подключения ноутбука или смартфона к монитору или телевизору через HDMI.',
        'features': [
            {'Разрешение': '4K@30Hz'},
            {'Порты': 'USB-C, HDMI'},
            {'Длина': '15 см'}
        ],
        'price': 1800,
        'stock': 3,
        'image_url': image_urls[3]
    },
    {
        'category': 'perehodniki',
        'name': 'Переходник Lightning — 3.5mm',
        'slug': 'lightning-35mm-adapter',
        'short_description': 'Для наушников с iPhone',
        'description': 'Оригинальный переходник Apple для подключения наушников с разъёмом 3.5 мм к iPhone.',
        'features': [
            {'Тип': 'Lightning — 3.5mm'},
            {'Длина': '10 см'},
            {'Качество': 'Цифровой ЦАП'}
        ],
        'price': 1200,
        'stock': 6,
        'image_url': image_urls[4]
    },

    # Телевизоры - 4K
    {
        'category': '4k',
        'name': 'Samsung QLED 4K',
        'slug': 'samsung-qled-4k',
        'short_description': 'Телевизор Samsung QLED 4K',
        'description': 'Телевизор Samsung QLED 4K с технологией квантовых точек и отличной цветопередачей.',
        'features': [
            {'Диагональ': '55"'},
            {'Разрешение': '4K UHD'},
            {'Технология': 'QLED'}
        ],
        'price': 59990,
        'stock': 2,
        'image_url': image_urls[3]
    },
    {
        'category': '4k',
        'name': 'LG OLED 4K',
        'slug': 'lg-oled-4k',
        'short_description': 'Телевизор LG с OLED-экраном',
        'description': 'Телевизор LG с OLED-экраном и идеальным чёрным цветом. Отличный выбор для киноманов.',
        'features': [
            {'Диагональ': '65"'},
            {'Разрешение': '4K UHD'},
            {'Технология': 'OLED'}
        ],
        'price': 120000,
        'stock': 1,
        'image_url': image_urls[4]
    },
    {
        'category': '4k',
        'name': 'Sony Bravia XR 4K',
        'slug': 'sony-bravia-xr-4k',
        'short_description': 'Телевизор Sony с процессором XR',
        'description': 'Телевизор Sony Bravia с процессором XR и превосходным качеством изображения.',
        'features': [
            {'Диагональ': '55"'},
            {'Разрешение': '4K UHD'},
            {'Процессор': 'XR'}
        ],
        'price': 110000,
        'stock': 0,
        'image_url': image_urls[5]
    },

    # Телевизоры - 8K
    {
        'category': '8k',
        'name': 'Samsung QLED 8K',
        'slug': 'samsung-qled-8k',
        'short_description': 'Телевизор Samsung 8K',
        'description': 'Телевизор Samsung QLED с разрешением 8K и технологией квантовых точек.',
        'features': [
            {'Диагональ': '75"'},
            {'Разрешение': '8K'},
            {'Технология': 'QLED'}
        ],
        'price': 250000,
        'stock': 1,
        'image_url': image_urls[6]
    },
    {
        'category': '8k',
        'name': 'LG NanoCell 8K',
        'slug': 'lg-nanocell-8k',
        'short_description': 'Телевизор LG 8K',
        'description': 'Телевизор LG с технологией NanoCell и разрешением 8K.',
        'features': [
            {'Диагональ': '65"'},
            {'Разрешение': '8K'},
            {'Технология': 'NanoCell'}
        ],
        'price': 200000,
        'stock': 0,
        'image_url': image_urls[7]
    },

    # Телевизоры - Full HD
    {
        'category': 'full-hd',
        'name': 'Philips Full HD TV',
        'slug': 'philips-full-hd-tv',
        'short_description': 'Телевизор Philips Full HD',
        'description': 'Телевизор Philips с разрешением Full HD и технологией Ambilight.',
        'features': [
            {'Диагональ': '43"'},
            {'Разрешение': 'Full HD'},
            {'Технология': 'Ambilight'}
        ],
        'price': 35000,
        'stock': 5,
        'image_url': image_urls[0]
    },
    {
        'category': 'full-hd',
        'name': 'Sony KDL-40',
        'slug': 'sony-kdl-40',
        'short_description': 'Телевизор Sony Full HD',
        'description': 'Телевизор Sony с диагональю 40 дюймов и отличным качеством изображения.',
        'features': [
            {'Диагональ': '40"'},
            {'Разрешение': 'Full HD'},
            {'Процессор': 'X-Reality'}
        ],
        'price': 40000,
        'stock': 3,
        'image_url': image_urls[1]
    },

    # Планшеты - Android-планшеты
    {
        'category': 'android-planshety',
        'name': 'Samsung Galaxy Tab S9',
        'slug': 'samsung-galaxy-tab-s9',
        'short_description': 'Флагманский планшет Samsung',
        'description': 'Samsung Galaxy Tab S9 — флагманский планшет с AMOLED-экраном и поддержкой S Pen.',
        'features': [
            {'Экран': '11" AMOLED, 120 Гц'},
            {'Процессор': 'Snapdragon 8 Gen 2'},
            {'Стилус': 'S Pen в комплекте'}
        ],
        'price': 80000,
        'stock': 2,
        'image_url': image_urls[2]
    },
    {
        'category': 'android-planshety',
        'name': 'Lenovo Tab P12 Pro',
        'slug': 'lenovo-tab-p12-pro',
        'short_description': 'Планшет Lenovo с AMOLED-экраном',
        'description': 'Lenovo Tab P12 Pro — мощный планшет с AMOLED-экраном и стилусом для творчества.',
        'features': [
            {'Экран': '12.6" AMOLED'},
            {'Процессор': 'Snapdragon 870'},
            {'Стилус': 'Precision Pen 2'}
        ],
        'price': 60000,
        'stock': 0,
        'image_url': image_urls[3]
    },

    # Планшеты - iPad
    {
        'category': 'ipad',
        'name': 'iPad Pro 12.9\"',
        'slug': 'ipad-pro-12-9',
        'short_description': 'Профессиональный iPad Pro',
        'description': 'iPad Pro 12.9\" — самый мощный планшет Apple с чипом M2 и дисплеем Liquid Retina XDR.',
        'features': [
            {'Экран': '12.9" Liquid Retina XDR'},
            {'Процессор': 'Apple M2'},
            {'Стилус': 'Apple Pencil 2'}
        ],
        'price': 120000,
        'stock': 1,
        'image_url': image_urls[4]
    },
    {
        'category': 'ipad',
        'name': 'iPad Air 2024',
        'slug': 'ipad-air-2024',
        'short_description': 'Лёгкий и мощный iPad Air',
        'description': 'iPad Air 2024 — тонкий и лёгкий планшет с чипом M2 и поддержкой Apple Pencil 2.',
        'features': [
            {'Экран': '10.9" Liquid Retina'},
            {'Процессор': 'Apple M2'},
            {'Стилус': 'Apple Pencil 2'}
        ],
        'price': 90000,
        'stock': 4,
        'image_url': image_urls[5]
    },
]

def download_image(url):
    return None
    img_temp = NamedTemporaryFile()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as u:
            img_temp.write(u.read())
        img_temp.flush()
        return img_temp
    except Exception as e:
        print(f'Ошибка загрузки изображения {url}: {e}')
        return None

# --- Создаём товары только из real_products ---
for prod_data in real_products:
    # Находим объект подкатегории по слагу
    subcat = None
    for cat_subcats in subcategory_objs.values():
        for s in cat_subcats:
            if s.slug == prod_data['category']:
                subcat = s
                break
        if subcat:
            break
    if not subcat:
        print(f"Не найдена подкатегория для товара: {prod_data.get('name', 'NO_NAME')}")
        continue
    product, created = Product.objects.get_or_create(
        category=subcat,
        name=prod_data['name'],
        slug=prod_data['slug'],
        defaults={
            'short_description': prod_data.get('short_description', ''),
            'description': prod_data.get('description', ''),
            'features': prod_data.get('features', []),
            'price': prod_data['price'],
            'stock': prod_data.get('stock', 0),
        }
    )
    if created and prod_data.get('image_url'):
        img_temp = download_image(prod_data['image_url'])
        if img_temp:
            product.image.save(f"{prod_data['slug']}.jpg", File(img_temp), save=True)
            img_temp.close()

print("Категории, подкатегории и реальные товары с описаниями и характеристиками успешно созданы!") 