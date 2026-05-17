BEGIN;
INSERT INTO categories (id, value, slug, created_at, updated_at, is_active) VALUES
    (gen_random_uuid(), 'Электроника и периферия', 'electronics-and-peripherals', NOW(), NOW(), true),
    (gen_random_uuid(), 'Бытовая техника и уход', 'home-appliances-and-personal-care', NOW(), NOW(), true),
    (gen_random_uuid(), 'Одежда, обувь и аксессуары', 'clothing-footwear-and-accessories', NOW(), NOW(), true),
    (gen_random_uuid(), 'Мебель и домашний текстиль', 'furniture-and-home-textiles', NOW(), NOW(), true),
    (gen_random_uuid(), 'Ремонт и инструменты', 'repair-and-tools', NOW(), NOW(), true),
    (gen_random_uuid(), 'Зоотовары', 'pet-supplies', NOW(), NOW(), true),
    (gen_random_uuid(), 'Детские товары', 'baby-and-kids-products', NOW(), NOW(), true),
    (gen_random_uuid(), 'Спорт и активный отдых', 'sports-and-outdoors', NOW(), NOW(), true);
COMMIT;

BEGIN;

INSERT INTO categories (id, value, slug, parent_id, created_at, updated_at, is_active) VALUES
    -- Электроника и периферия
    (gen_random_uuid(), 'Смартфоны', 'smartphones', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Ноутбуки', 'laptops', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Наушники', 'headphones', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Часы', 'watches', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Планшеты', 'tablets', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Клавиатуры', 'keyboards', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Мыши', 'mice', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Мониторы', 'monitors', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Принтеры', 'printers', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Камеры', 'cameras', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Объективы', 'lenses', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Игровые приставки', 'gaming-consoles', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Игры', 'games', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Телевизоры', 'televisions', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Проекторы', 'projectors', (SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), NOW(), NOW(), TRUE),

    -- Бытовая техника и уход
    (gen_random_uuid(), 'Холодильники', 'refrigerators', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Плиты', 'stoves', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Микроволновки', 'microwaves', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Чайники', 'kettles', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Кофемашины', 'coffee-machines', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Блендеры', 'blenders', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Тостеры', 'toasters', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Пылесосы', 'vacuum-cleaners', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Утюги', 'irons', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Фены', 'hair-dryers', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Эпиляторы', 'epilators', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Бритвы', 'shavers', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Зубные щетки', 'toothbrushes', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Весы', 'scales', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Кондиционеры', 'air-conditioners', (SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), NOW(), NOW(), TRUE),

    -- Одежда, обувь и аксессуары
    (gen_random_uuid(), 'Платья', 'dresses', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Рубашки', 'shirts', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Джинсы', 'jeans', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Брюки', 'trousers', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Юбки', 'skirts', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Костюмы', 'suits', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Пальто', 'coats', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Куртки', 'jackets', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Свитера', 'sweaters', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Футболки', 't-shirts', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Шорты', 'shorts', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Нижнее белье', 'underwear', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Носки', 'socks', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Кроссовки', 'sneakers', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Туфли', 'shoes', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Ботинки', 'boots', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Сандалии', 'sandals', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Сумки', 'bags', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Рюкзаки', 'backpacks', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Кошельки', 'wallets', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Ремни', 'belts', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Шляпы', 'hats', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Очки', 'glasses', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Серьги', 'earrings', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Кольца', 'rings', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Браслеты', 'bracelets', (SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), NOW(), NOW(), TRUE),

    -- Мебель и домашний текстиль
    (gen_random_uuid(), 'Кровати', 'beds', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Диваны', 'sofas', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Столы', 'tables', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Стулья', 'chairs', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Шкафы', 'wardrobes', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Комоды', 'dressers', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Полки', 'shelves', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Зеркала', 'mirrors', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Матрасы', 'mattresses', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Постельное белье', 'bed-linen', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Полотенца', 'towels', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Шторы', 'curtains', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Посуда', 'tableware', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Сковородки', 'frying-pans', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Кастрюли', 'pots', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Ножи', 'knives', (SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), NOW(), NOW(), TRUE),

    -- Ремонт и инструменты
    (gen_random_uuid(), 'Инструменты', 'tools', (SELECT id FROM categories WHERE slug = 'repair-and-tools'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Дрели', 'drills', (SELECT id FROM categories WHERE slug = 'repair-and-tools'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Шуруповерты', 'screwdrivers', (SELECT id FROM categories WHERE slug = 'repair-and-tools'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Молотки', 'hammers', (SELECT id FROM categories WHERE slug = 'repair-and-tools'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Обои', 'wallpaper', (SELECT id FROM categories WHERE slug = 'repair-and-tools'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Краски', 'paints', (SELECT id FROM categories WHERE slug = 'repair-and-tools'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Ламинат', 'laminate', (SELECT id FROM categories WHERE slug = 'repair-and-tools'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Плитка', 'tiles', (SELECT id FROM categories WHERE slug = 'repair-and-tools'), NOW(), NOW(), TRUE),

    -- Зоотовары
    (gen_random_uuid(), 'Корм для кошек', 'cat-food', (SELECT id FROM categories WHERE slug = 'pet-supplies'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Корм для собак', 'dog-food', (SELECT id FROM categories WHERE slug = 'pet-supplies'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Аквариумы', 'aquariums', (SELECT id FROM categories WHERE slug = 'pet-supplies'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Клетки', 'cages', (SELECT id FROM categories WHERE slug = 'pet-supplies'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Игрушки для животных', 'pet-toys', (SELECT id FROM categories WHERE slug = 'pet-supplies'), NOW(), NOW(), TRUE),

    -- Детские товары
    (gen_random_uuid(), 'Детское питание', 'baby-food', (SELECT id FROM categories WHERE slug = 'baby-and-kids-products'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Подгузники', 'diapers', (SELECT id FROM categories WHERE slug = 'baby-and-kids-products'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Коляски', 'strollers', (SELECT id FROM categories WHERE slug = 'baby-and-kids-products'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Автокресла', 'car-seats', (SELECT id FROM categories WHERE slug = 'baby-and-kids-products'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Конструкторы', 'building-sets', (SELECT id FROM categories WHERE slug = 'baby-and-kids-products'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Куклы', 'dolls', (SELECT id FROM categories WHERE slug = 'baby-and-kids-products'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Машинки', 'toy-cars', (SELECT id FROM categories WHERE slug = 'baby-and-kids-products'), NOW(), NOW(), TRUE),

    -- Спорт и активный отдых
    (gen_random_uuid(), 'Спортивная одежда', 'sportswear', (SELECT id FROM categories WHERE slug = 'sports-and-outdoors'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Мячи', 'balls', (SELECT id FROM categories WHERE slug = 'sports-and-outdoors'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Гантели', 'dumbbells', (SELECT id FROM categories WHERE slug = 'sports-and-outdoors'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Йога', 'yoga', (SELECT id FROM categories WHERE slug = 'sports-and-outdoors'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Туризм', 'tourism', (SELECT id FROM categories WHERE slug = 'sports-and-outdoors'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Палатки', 'tents', (SELECT id FROM categories WHERE slug = 'sports-and-outdoors'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Спальники', 'sleeping-bags', (SELECT id FROM categories WHERE slug = 'sports-and-outdoors'), NOW(), NOW(), TRUE),
    (gen_random_uuid(), 'Фонари', 'flashlights', (SELECT id FROM categories WHERE slug = 'sports-and-outdoors'), NOW(), NOW(), TRUE);

COMMIT;

BEGIN;
INSERT INTO categories_keywords (category_id, name) VALUES
    -- Электроника и периферия
    ((SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), 'электроника'),
    ((SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), 'периферия'),
    ((SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), 'гаджеты'),
    ((SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), 'комплектующие'),
    ((SELECT id FROM categories WHERE slug = 'electronics-and-peripherals'), 'компьютерные аксессуары'),

    -- Смартфоны
    ((SELECT id FROM categories WHERE slug = 'smartphones'), 'телефон'),
    ((SELECT id FROM categories WHERE slug = 'smartphones'), 'мобильник'),
    ((SELECT id FROM categories WHERE slug = 'smartphones'), 'смарт'),
    ((SELECT id FROM categories WHERE slug = 'smartphones'), 'айфон'),
    ((SELECT id FROM categories WHERE slug = 'smartphones'), 'андроид'),

    -- Ноутбуки
    ((SELECT id FROM categories WHERE slug = 'laptops'), 'ноут'),
    ((SELECT id FROM categories WHERE slug = 'laptops'), 'компьютер портативный'),
    ((SELECT id FROM categories WHERE slug = 'laptops'), 'лэптоп'),
    ((SELECT id FROM categories WHERE slug = 'laptops'), 'macbook'),
    ((SELECT id FROM categories WHERE slug = 'laptops'), 'ноутбук для работы'),

    -- Наушники
    ((SELECT id FROM categories WHERE slug = 'headphones'), 'гарнитура'),
    ((SELECT id FROM categories WHERE slug = 'headphones'), 'наушники беспроводные'),
    ((SELECT id FROM categories WHERE slug = 'headphones'), 'затычки'),
    ((SELECT id FROM categories WHERE slug = 'headphones'), 'airpods'),
    ((SELECT id FROM categories WHERE slug = 'headphones'), 'микрофон'),

    -- Часы
    ((SELECT id FROM categories WHERE slug = 'watches'), 'умные часы'),
    ((SELECT id FROM categories WHERE slug = 'watches'), 'smart watch'),
    ((SELECT id FROM categories WHERE slug = 'watches'), 'электронные часы'),
    ((SELECT id FROM categories WHERE slug = 'watches'), 'apple watch'),
    ((SELECT id FROM categories WHERE slug = 'watches'), 'фитнес браслет'),

    -- Планшеты
    ((SELECT id FROM categories WHERE slug = 'tablets'), 'планшет'),
    ((SELECT id FROM categories WHERE slug = 'tablets'), 'ipad'),
    ((SELECT id FROM categories WHERE slug = 'tablets'), 'планшет самсунг'),
    ((SELECT id FROM categories WHERE slug = 'tablets'), 'детский планшет'),

    -- Клавиатуры
    ((SELECT id FROM categories WHERE slug = 'keyboards'), 'клава'),
    ((SELECT id FROM categories WHERE slug = 'keyboards'), 'клавиатура механическая'),
    ((SELECT id FROM categories WHERE slug = 'keyboards'), 'клавиатура беспроводная'),
    ((SELECT id FROM categories WHERE slug = 'keyboards'), 'игровая клавиатура'),

    -- Мыши
    ((SELECT id FROM categories WHERE slug = 'mice'), 'мышка'),
    ((SELECT id FROM categories WHERE slug = 'mice'), 'компьютерная мышь'),
    ((SELECT id FROM categories WHERE slug = 'mice'), 'игровая мышь'),
    ((SELECT id FROM categories WHERE slug = 'mice'), 'мышь беспроводная'),

    -- Мониторы
    ((SELECT id FROM categories WHERE slug = 'monitors'), 'экран'),
    ((SELECT id FROM categories WHERE slug = 'monitors'), 'дисплей'),
    ((SELECT id FROM categories WHERE slug = 'monitors'), 'монитор для компьютера'),
    ((SELECT id FROM categories WHERE slug = 'monitors'), 'игровой монитор'),

    -- Принтеры
    ((SELECT id FROM categories WHERE slug = 'printers'), 'принтер лазерный'),
    ((SELECT id FROM categories WHERE slug = 'printers'), 'мфу'),
    ((SELECT id FROM categories WHERE slug = 'printers'), 'струйный принтер'),
    ((SELECT id FROM categories WHERE slug = 'printers'), 'картридж'),

    -- Камеры
    ((SELECT id FROM categories WHERE slug = 'cameras'), 'фотоаппарат'),
    ((SELECT id FROM categories WHERE slug = 'cameras'), 'зеркалка'),
    ((SELECT id FROM categories WHERE slug = 'cameras'), 'беззеркалка'),
    ((SELECT id FROM categories WHERE slug = 'cameras'), 'экшн камера'),
    ((SELECT id FROM categories WHERE slug = 'cameras'), 'видеокамера'),

    -- Объективы
    ((SELECT id FROM categories WHERE slug = 'lenses'), 'линза'),
    ((SELECT id FROM categories WHERE slug = 'lenses'), 'объектив камеры'),
    ((SELECT id FROM categories WHERE slug = 'lenses'), 'фикс объектив'),
    ((SELECT id FROM categories WHERE slug = 'lenses'), 'зум объектив'),

    -- Игровые приставки
    ((SELECT id FROM categories WHERE slug = 'gaming-consoles'), 'плойка'),
    ((SELECT id FROM categories WHERE slug = 'gaming-consoles'), 'playstation'),
    ((SELECT id FROM categories WHERE slug = 'gaming-consoles'), 'xbox'),
    ((SELECT id FROM categories WHERE slug = 'gaming-consoles'), 'nintendo switch'),
    ((SELECT id FROM categories WHERE slug = 'gaming-consoles'), 'игровая консоль'),

    -- Игры
    ((SELECT id FROM categories WHERE slug = 'games'), 'игровой диск'),
    ((SELECT id FROM categories WHERE slug = 'games'), 'компьютерные игры'),
    ((SELECT id FROM categories WHERE slug = 'games'), 'игры для приставок'),
    ((SELECT id FROM categories WHERE slug = 'games'), 'ключ активации'),

    -- Телевизоры
    ((SELECT id FROM categories WHERE slug = 'televisions'), 'телек'),
    ((SELECT id FROM categories WHERE slug = 'televisions'), 'тв'),
    ((SELECT id FROM categories WHERE slug = 'televisions'), 'телевизор жк'),
    ((SELECT id FROM categories WHERE slug = 'televisions'), 'smart tv'),

    -- Проекторы
    ((SELECT id FROM categories WHERE slug = 'projectors'), 'проектор для дома'),
    ((SELECT id FROM categories WHERE slug = 'projectors'), 'кинопроектор'),
    ((SELECT id FROM categories WHERE slug = 'projectors'), 'экран для проектора'),

    -- Бытовая техника и уход
    ((SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), 'техника для дома'),
    ((SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), 'бытовая электроника'),
    ((SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), 'уход за собой'),
    ((SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), 'мелкая бытовая техника'),
    ((SELECT id FROM categories WHERE slug = 'home-appliances-and-personal-care'), 'крупная бытовая техника'),

    -- Холодильники
    ((SELECT id FROM categories WHERE slug = 'refrigerators'), 'холодильник двухкамерный'),
    ((SELECT id FROM categories WHERE slug = 'refrigerators'), 'морозильник'),
    ((SELECT id FROM categories WHERE slug = 'refrigerators'), 'холодильник ноу фрост'),

    -- Плиты
    ((SELECT id FROM categories WHERE slug = 'stoves'), 'газовая плита'),
    ((SELECT id FROM categories WHERE slug = 'stoves'), 'электрическая плита'),
    ((SELECT id FROM categories WHERE slug = 'stoves'), 'варочная панель'),
    ((SELECT id FROM categories WHERE slug = 'stoves'), 'духовка'),

    -- Микроволновки
    ((SELECT id FROM categories WHERE slug = 'microwaves'), 'микроволновая печь'),
    ((SELECT id FROM categories WHERE slug = 'microwaves'), 'свч'),

    -- Чайники
    ((SELECT id FROM categories WHERE slug = 'kettles'), 'электрочайник'),
    ((SELECT id FROM categories WHERE slug = 'kettles'), 'термопот'),

    -- Кофемашины
    ((SELECT id FROM categories WHERE slug = 'coffee-machines'), 'кофеварка'),
    ((SELECT id FROM categories WHERE slug = 'coffee-machines'), 'кофемашина капсульная'),
    ((SELECT id FROM categories WHERE slug = 'coffee-machines'), 'кофе в зернах'),

    -- Блендеры
    ((SELECT id FROM categories WHERE slug = 'blenders'), 'блендер погружной'),
    ((SELECT id FROM categories WHERE slug = 'blenders'), 'стационарный блендер'),

    -- Тостеры
    ((SELECT id FROM categories WHERE slug = 'toasters'), 'тостер для хлеба'),

    -- Пылесосы
    ((SELECT id FROM categories WHERE slug = 'vacuum-cleaners'), 'пылесос робот'),
    ((SELECT id FROM categories WHERE slug = 'vacuum-cleaners'), 'моющий пылесос'),
    ((SELECT id FROM categories WHERE slug = 'vacuum-cleaners'), 'вертикальный пылесос'),

    -- Утюги
    ((SELECT id FROM categories WHERE slug = 'irons'), 'утюг с парогенератором'),
    ((SELECT id FROM categories WHERE slug = 'irons'), 'паровая станция'),

    -- Фены
    ((SELECT id FROM categories WHERE slug = 'hair-dryers'), 'фен для волос'),

    -- Эпиляторы
    ((SELECT id FROM categories WHERE slug = 'epilators'), 'эпилятор женский'),
    ((SELECT id FROM categories WHERE slug = 'epilators'), 'лазерный эпилятор'),

    -- Бритвы
    ((SELECT id FROM categories WHERE slug = 'shavers'), 'электробритва'),
    ((SELECT id FROM categories WHERE slug = 'shavers'), 'триммер'),

    -- Зубные щетки
    ((SELECT id FROM categories WHERE slug = 'toothbrushes'), 'электрическая зубная щетка'),
    ((SELECT id FROM categories WHERE slug = 'toothbrushes'), 'ирригатор'),

    -- Весы
    ((SELECT id FROM categories WHERE slug = 'scales'), 'напольные весы'),
    ((SELECT id FROM categories WHERE slug = 'scales'), 'кухонные весы'),

    -- Кондиционеры
    ((SELECT id FROM categories WHERE slug = 'air-conditioners'), 'сплит система'),
    ((SELECT id FROM categories WHERE slug = 'air-conditioners'), 'кондиционер для дома'),

    -- Одежда, обувь и аксессуары
    ((SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), 'одежда'),
    ((SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), 'обувь'),
    ((SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), 'аксессуары'),
    ((SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), 'мода'),
    ((SELECT id FROM categories WHERE slug = 'clothing-footwear-and-accessories'), 'стиль'),

    -- Платья
    ((SELECT id FROM categories WHERE slug = 'dresses'), 'женское платье'),
    ((SELECT id FROM categories WHERE slug = 'dresses'), 'вечернее платье'),

    -- Рубашки
    ((SELECT id FROM categories WHERE slug = 'shirts'), 'мужская рубашка'),
    ((SELECT id FROM categories WHERE slug = 'shirts'), 'женская блузка'),

    -- Джинсы
    ((SELECT id FROM categories WHERE slug = 'jeans'), 'мужские джинсы'),
    ((SELECT id FROM categories WHERE slug = 'jeans'), 'женские джинсы'),

    -- Брюки
    ((SELECT id FROM categories WHERE slug = 'trousers'), 'штаны'),
    ((SELECT id FROM categories WHERE slug = 'trousers'), 'слаксы'),

    -- Юбки
    ((SELECT id FROM categories WHERE slug = 'skirts'), 'юбка женская'),

    -- Костюмы
    ((SELECT id FROM categories WHERE slug = 'suits'), 'деловой костюм'),
    ((SELECT id FROM categories WHERE slug = 'suits'), 'спортивный костюм'),

    -- Пальто
    ((SELECT id FROM categories WHERE slug = 'coats'), 'зимнее пальто'),
    ((SELECT id FROM categories WHERE slug = 'coats'), 'демисезонное пальто'),

    -- Куртки
    ((SELECT id FROM categories WHERE slug = 'jackets'), 'пуховик'),
    ((SELECT id FROM categories WHERE slug = 'jackets'), 'ветровка'),
    ((SELECT id FROM categories WHERE slug = 'jackets'), 'кожаная куртка'),

    -- Свитера
    ((SELECT id FROM categories WHERE slug = 'sweaters'), 'джемпер'),
    ((SELECT id FROM categories WHERE slug = 'sweaters'), 'пуловер'),
    ((SELECT id FROM categories WHERE slug = 'sweaters'), 'худи'),

    -- Футболки
    ((SELECT id FROM categories WHERE slug = 't-shirts'), 'майка'),
    ((SELECT id FROM categories WHERE slug = 't-shirts'), 'поло'),

    -- Шорты
    ((SELECT id FROM categories WHERE slug = 'shorts'), 'бермуды'),

    -- Носки
    ((SELECT id FROM categories WHERE slug = 'socks'), 'гольфы'),
    ((SELECT id FROM categories WHERE slug = 'socks'), 'чулки'),

    -- Кроссовки
    ((SELECT id FROM categories WHERE slug = 'sneakers'), 'кеды'),
    ((SELECT id FROM categories WHERE slug = 'sneakers'), 'спортивная обувь'),

    -- Туфли
    ((SELECT id FROM categories WHERE slug = 'shoes'), 'лодочки'),
    ((SELECT id FROM categories WHERE slug = 'shoes'), 'женские туфли'),

    -- Ботинки
    ((SELECT id FROM categories WHERE slug = 'boots'), 'сапоги'),
    ((SELECT id FROM categories WHERE slug = 'boots'), 'ботинки зимние'),

    -- Сумки
    ((SELECT id FROM categories WHERE slug = 'bags'), 'женская сумка'),
    ((SELECT id FROM categories WHERE slug = 'bags'), 'клатч'),
    ((SELECT id FROM categories WHERE slug = 'bags'), 'шоппер'),

    -- Рюкзаки
    ((SELECT id FROM categories WHERE slug = 'backpacks'), 'рюкзак городской'),
    ((SELECT id FROM categories WHERE slug = 'backpacks'), 'школьный рюкзак'),

    -- Кошельки
    ((SELECT id FROM categories WHERE slug = 'wallets'), 'портмоне'),

    -- Очки
    ((SELECT id FROM categories WHERE slug = 'glasses'), 'солнцезащитные очки'),
    ((SELECT id FROM categories WHERE slug = 'glasses'), 'очки для зрения'),

    -- Мебель и домашний текстиль
    ((SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), 'мебель'),
    ((SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), 'текстиль для дома'),
    ((SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), 'интерьер'),
    ((SELECT id FROM categories WHERE slug = 'furniture-and-home-textiles'), 'дом и уют'),

    -- Кровати
    ((SELECT id FROM categories WHERE slug = 'beds'), 'кровать двуспальная'),
    ((SELECT id FROM categories WHERE slug = 'beds'), 'кровать односпальная'),

    -- Диваны
    ((SELECT id FROM categories WHERE slug = 'sofas'), 'диван угловой'),
    ((SELECT id FROM categories WHERE slug = 'sofas'), 'диван раскладной'),
    ((SELECT id FROM categories WHERE slug = 'sofas'), 'тахта'),

    -- Столы
    ((SELECT id FROM categories WHERE slug = 'tables'), 'письменный стол'),
    ((SELECT id FROM categories WHERE slug = 'tables'), 'обеденный стол'),
    ((SELECT id FROM categories WHERE slug = 'tables'), 'журнальный столик'),

    -- Стулья
    ((SELECT id FROM categories WHERE slug = 'chairs'), 'стул кухонный'),
    ((SELECT id FROM categories WHERE slug = 'chairs'), 'кресло'),
    ((SELECT id FROM categories WHERE slug = 'chairs'), 'компьютерное кресло'),

    -- Шкафы
    ((SELECT id FROM categories WHERE slug = 'wardrobes'), 'шкаф купе'),
    ((SELECT id FROM categories WHERE slug = 'wardrobes'), 'шкаф платяной'),

    -- Постельное белье
    ((SELECT id FROM categories WHERE slug = 'bed-linen'), 'простыня'),
    ((SELECT id FROM categories WHERE slug = 'bed-linen'), 'пододеяльник'),
    ((SELECT id FROM categories WHERE slug = 'bed-linen'), 'наволочка'),

    -- Шторы
    ((SELECT id FROM categories WHERE slug = 'curtains'), 'портьеры'),
    ((SELECT id FROM categories WHERE slug = 'curtains'), 'гардины'),
    ((SELECT id FROM categories WHERE slug = 'curtains'), 'жалюзи'),

    -- Посуда
    ((SELECT id FROM categories WHERE slug = 'tableware'), 'тарелки'),
    ((SELECT id FROM categories WHERE slug = 'tableware'), 'чашки'),
    ((SELECT id FROM categories WHERE slug = 'tableware'), 'столовые приборы'),

    -- Ножи
    ((SELECT id FROM categories WHERE slug = 'knives'), 'кухонный нож'),
    ((SELECT id FROM categories WHERE slug = 'knives'), 'набор ножей'),

    -- Ремонт и инструменты
    ((SELECT id FROM categories WHERE slug = 'repair-and-tools'), 'стройматериалы'),
    ((SELECT id FROM categories WHERE slug = 'repair-and-tools'), 'инструмент'),
    ((SELECT id FROM categories WHERE slug = 'repair-and-tools'), 'ремонт квартиры'),

    -- Инструменты
    ((SELECT id FROM categories WHERE slug = 'tools'), 'инструмент набор'),
    ((SELECT id FROM categories WHERE slug = 'tools'), 'ручной инструмент'),

    -- Дрели
    ((SELECT id FROM categories WHERE slug = 'drills'), 'дрель ударная'),
    ((SELECT id FROM categories WHERE slug = 'drills'), 'перфоратор'),

    -- Шуруповерты
    ((SELECT id FROM categories WHERE slug = 'screwdrivers'), 'шуруповерт аккумуляторный'),

    -- Обои
    ((SELECT id FROM categories WHERE slug = 'wallpaper'), 'обои для стен'),
    ((SELECT id FROM categories WHERE slug = 'wallpaper'), 'флизелиновые обои'),

    -- Краски
    ((SELECT id FROM categories WHERE slug = 'paints'), 'интерьерная краска'),
    ((SELECT id FROM categories WHERE slug = 'paints'), 'фасадная краска'),

    -- Ламинат
    ((SELECT id FROM categories WHERE slug = 'laminate'), 'ламинат влагостойкий'),

    -- Плитка
    ((SELECT id FROM categories WHERE slug = 'tiles'), 'керамогранит'),
    ((SELECT id FROM categories WHERE slug = 'tiles'), 'кафель'),

    -- Зоотовары
    ((SELECT id FROM categories WHERE slug = 'pet-supplies'), 'товары для животных'),
    ((SELECT id FROM categories WHERE slug = 'pet-supplies'), 'зоомагазин'),

    -- Корм для кошек
    ((SELECT id FROM categories WHERE slug = 'cat-food'), 'сухой корм для кошек'),
    ((SELECT id FROM categories WHERE slug = 'cat-food'), 'влажный корм для кошек'),

    -- Корм для собак
    ((SELECT id FROM categories WHERE slug = 'dog-food'), 'корм для собак'),

    -- Аквариумы
    ((SELECT id FROM categories WHERE slug = 'aquariums'), 'аквариум с рыбками'),
    ((SELECT id FROM categories WHERE slug = 'aquariums'), 'оборудование для аквариума'),

    -- Клетки
    ((SELECT id FROM categories WHERE slug = 'cages'), 'клетка для птиц'),
    ((SELECT id FROM categories WHERE slug = 'cages'), 'клетка для грызунов'),

    -- Игрушки для животных
    ((SELECT id FROM categories WHERE slug = 'pet-toys'), 'игрушка для кошки'),
    ((SELECT id FROM categories WHERE slug = 'pet-toys'), 'игрушка для собаки'),

    -- Детские товары
    ((SELECT id FROM categories WHERE slug = 'baby-and-kids-products'), 'детские товары'),
    ((SELECT id FROM categories WHERE slug = 'baby-and-kids-products'), 'для детей'),
    ((SELECT id FROM categories WHERE slug = 'baby-and-kids-products'), 'магазин для детей'),

    -- Детское питание
    ((SELECT id FROM categories WHERE slug = 'baby-food'), 'смесь для новорожденных'),
    ((SELECT id FROM categories WHERE slug = 'baby-food'), 'детское пюре'),

    -- Подгузники
    ((SELECT id FROM categories WHERE slug = 'diapers'), 'памперсы'),

    -- Коляски
    ((SELECT id FROM categories WHERE slug = 'strollers'), 'коляска люлька'),
    ((SELECT id FROM categories WHERE slug = 'strollers'), 'коляска трость'),

    -- Автокресла
    ((SELECT id FROM categories WHERE slug = 'car-seats'), 'детское автокресло'),

    -- Конструкторы
    ((SELECT id FROM categories WHERE slug = 'building-sets'), 'лего'),
    ((SELECT id FROM categories WHERE slug = 'building-sets'), 'конструктор для детей'),

    -- Куклы
    ((SELECT id FROM categories WHERE slug = 'dolls'), 'кукла барби'),

    -- Машинки
    ((SELECT id FROM categories WHERE slug = 'toy-cars'), 'детские машинки'),

    -- Спорт и активный отдых
    ((SELECT id FROM categories WHERE slug = 'sports-and-outdoors'), 'спорттовары'),
    ((SELECT id FROM categories WHERE slug = 'sports-and-outdoors'), 'туризм и отдых'),
    ((SELECT id FROM categories WHERE slug = 'sports-and-outdoors'), 'активный отдых'),

    -- Спортивная одежда
    ((SELECT id FROM categories WHERE slug = 'sportswear'), 'спортивная форма'),

    -- Мячи
    ((SELECT id FROM categories WHERE slug = 'balls'), 'футбольный мяч'),
    ((SELECT id FROM categories WHERE slug = 'balls'), 'баскетбольный мяч'),

    -- Гантели
    ((SELECT id FROM categories WHERE slug = 'dumbbells'), 'гантели разборные'),

    -- Йога
    ((SELECT id FROM categories WHERE slug = 'yoga'), 'коврик для йоги'),

    -- Туризм
    ((SELECT id FROM categories WHERE slug = 'tourism'), 'туристическое снаряжение'),

    -- Палатки
    ((SELECT id FROM categories WHERE slug = 'tents'), 'туристическая палатка'),
    ((SELECT id FROM categories WHERE slug = 'tents'), 'палатка для кемпинга'),

    -- Спальники
    ((SELECT id FROM categories WHERE slug = 'sleeping-bags'), 'спальный мешок'),

    -- Фонари
    ((SELECT id FROM categories WHERE slug = 'flashlights'), 'налобный фонарь');
COMMIT;