# DimaTechTestTask
# Описание проекта
Тестовое задание для "DimaTech Ltd". В качестве логина (электронной почты) 
и пароля для тестовых пользователя и администратора использовать user@example.com, 1234 и 
admin@example.com, 1234 соответственно. После установки согласно нижеописанным инструкциям документация
проекта будет доступна по следующей ссылке:
```
http://localhost:8000/docs
```

# Установка с использованием контейнеров

1. Клонируйте репозиторий
```
git clone https://github.com/MaximBrezhnev/DimaTechTestTask.git
```

2. Установите на свое устройство docker и docker compose

3. Перейдите в директорию проекта

4. Создайте в ней файл .env по аналогии с файлом .env.example.

5. Запустите контейнеры с приложением и базой данных командой
(В случае, если не удастся установить соединение с базой данных, просто перезагрузите
контейнер приложения):
```
docker compose up -d
```


# Установка без использования контейнеров

1. Клонируйте репозиторий
```
git clone https://github.com/MaximBrezhnev/DimaTechTestTask.git
```

2. Установите на свое устройство Postgres и создайте в рамках него базу данных

3. Перейдите в директорию проекта

4. Создайте в ней файл .env по аналогии с файлом .env.example (обязательно замените параметр DB_HOST на localhost и 
убедитесь, что EXTERNAL_DB_PORT и INTERNAL_DB_PORT совпадают). Значения для POSTGRES_USER, POSTGRES_DB и 
POSTGRES_PASSWORD установите в соответствии с указанными вами при создании базы данных

5. Откройте терминал в Linux/MacOS или PowerShell в Windows.
При работе с Windows терминал должен быть открыт от лица администратора, 
а после его открытия должна быть введена следующая команда:
```
Set-ExecutionPolicy RemoteSigned
```
6. Создайте виртуальное окружение (в Windows "python" вместо "python3"):
```
python3 -m venv venv
```
7. Активируйте виртуальное окружение
(для Windows и Linux / MacOS соответственно):
```
.\venv\Scripts\activate
```
```
source venv/bin/activate
```
8. Установите зависимости:
```
pip install -r requirements.txt
```
9. В файле alembic.ini заменить в параметре sqlalchemy.url значение
database на localhost и порт на указанный вами в .env

10. Ввести в терминале команду для выполнения
миграции:
```
alembic upgrade heads
```

11. Запустить проект командой (в Windows "python" вместо "python3")
```
python3 -m src.main
```
