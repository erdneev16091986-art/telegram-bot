# Telegram-бот на aiogram 3.x

Простой бот: отвечает на команду `/start` приветствием и на любое текстовое
сообщение фразой «Я тебя понял!».

## ⚠️ Важно про токен

Твой токен попал в открытый чат. Обязательно отзови его:
открой **@BotFather** → `/revoke` → выбери бота → получи новый токен.
Никому не показывай токен и не выкладывай его в публичные репозитории.

## Установка

1. Установи Python 3.10 или новее: https://www.python.org/downloads/
   (при установке на Windows отметь галочку **Add Python to PATH**).

2. Открой PowerShell в папке с ботом и создай виртуальное окружение:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   Если PowerShell ругается на политику выполнения скриптов, выполни один раз:

   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```

3. Установи зависимости:

   ```powershell
   pip install -r requirements.txt
   ```

## Запуск

Рекомендуется задать токен через переменную окружения (безопаснее, чем в коде):

```powershell
$env:BOT_TOKEN = "СЮДА_НОВЫЙ_ТОКЕН"
python bot.py
```

Либо просто запусти (тогда возьмётся токен, зашитый в `bot.py`):

```powershell
python bot.py
```

После запуска открой своего бота в Telegram и напиши `/start`.

## Остановка

Нажми `Ctrl + C` в терминале.
