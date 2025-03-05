-- Создание таблицы для хранения информации о цветах
CREATE TABLE flowers (
    id SERIAL PRIMARY KEY,         -- Уникальный идентификатор
    name VARCHAR(100) NOT NULL,    -- Название цветка
    value NUMERIC(10,2) NOT NULL,  -- Стоимость
    category VARCHAR(50) NOT NULL  -- Категория
);

-- Наполнение таблицы начальными данными
INSERT INTO flowers (name, value, category) VALUES
    ('Rose', 100, 'Cut Flowers'),
    ('Tulip', 200, 'Cut Flowers'),
    ('Orchid', 35, 'House Plant');

-- Вывод всех записей из таблицы flowers
SELECT * FROM flowers;

-- Функция поиска цветка по имени
CREATE OR REPLACE FUNCTION search_flower(flower_name VARCHAR)
RETURNS TABLE(id INT, name VARCHAR, value NUMERIC, category VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT flowers.id, flowers.name, flowers.value, flowers.category 
    FROM flowers 
    WHERE flowers.name ILIKE '%' || flower_name || '%'; -- Поиск по частичному совпадению имени
END;
$$ LANGUAGE plpgsql;

-- Функция удаления цветка по имени
CREATE OR REPLACE FUNCTION delete_flower(flower_name VARCHAR)
RETURNS VOID AS $$
BEGIN
    DELETE FROM flowers WHERE name = flower_name;
END;
$$ LANGUAGE plpgsql;

-- Функция добавления нового цветка
CREATE OR REPLACE FUNCTION add_flower(flower_name VARCHAR, flower_value NUMERIC, flower_category VARCHAR)
RETURNS VOID AS $$
BEGIN
    INSERT INTO flowers (name, value, category) VALUES (flower_name, flower_value, flower_category);
END;
$$ LANGUAGE plpgsql;

-- Добавление нового цветка
SELECT add_flower('Lily', 150, 'Cut Flowers');

-- Поиск цветка по имени
SELECT * FROM search_flower('Lily');

-- Удаление цветка по имени
SELECT delete_flower('Lily');

-- Повторное добавление цветка "Rose" после удаления
INSERT INTO flowers (name, value, category) VALUES ('Rose', 100, 'Cut Flowers');
