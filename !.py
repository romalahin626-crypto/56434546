"""
УДАЛЁНКА ДЛЯ ANDROID ЧЕРЕЗ TELEGRAM
Запускается в Termux на телефоне
"""
import os
import subprocess
import asyncio
from datetime import datetime
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ============================================
# ⚠️ НАСТРОЙКИ
# ============================================
BOT_TOKEN = "8514721426:AAG4b7jgAcJoM4Nzf8qeSop70WOoYEzUGb4"  # Тот же бот что и для ПК
ADMIN_IDS = [6272200485]  # Ваш Telegram ID

# Пути на Android
SCREENSHOT_PATH = "/sdcard/DCIM/bot_screenshot.png"
CAMERA_PHOTO_PATH = "/sdcard/DCIM/bot_photo.jpg"

# ============================================
# ОСНОВНОЙ КОД
# ============================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AndroidRemoteBot:
    def __init__(self):
        self.app = None

    async def check_admin(self, user_id):
        """Проверка прав администратора"""
        return user_id in ADMIN_IDS

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        if not await self.check_admin(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён!")
            return

        keyboard = [
            ["📱 Инфо", "📸 Скриншот"],
            ["📷 Фото", "📍 Гео"],
            ["📞 Звонки", "📱 Контакты"],
            ["🔋 Батарея", "📶 Сеть"],
            ["🗑️ Очистка", "⚙️ Система"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        info = await self.get_phone_info()

        await update.message.reply_text(
            f"📱 ANDROID REMOTE BOT\n"
            f"Управление телефоном через Telegram\n\n"
            f"{info}\n\n"
            f"Выберите действие:",
            reply_markup=reply_markup
        )

    async def get_phone_info(self):
        """Получить информацию о телефоне"""
        try:
            # Получаем базовую информацию через Termux
            info_commands = {
                "Модель": "getprop ro.product.model",
                "Бренд": "getprop ro.product.brand",
                "Версия Android": "getprop ro.build.version.release",
                "Пользователь": "whoami",
                "Время работы": "uptime",
            }

            info_text = "📊 ИНФОРМАЦИЯ О ТЕЛЕФОНЕ:\n"
            for key, cmd in info_commands.items():
                try:
                    result = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True, timeout=5
                    )
                    if result.stdout:
                        info_text += f"• {key}: {result.stdout.strip()}\n"
                except:
                    info_text += f"• {key}: Неизвестно\n"

            return info_text

        except Exception as e:
            return f"❌ Ошибка получения информации: {e}"

    async def take_screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сделать скриншот экрана"""
        if not await self.check_admin(update.effective_user.id):
            return

        await update.message.reply_text("📸 Делаю скриншот...")

        try:
            # Используем screencap через ADB или Termux
            command = f"screencap -p {SCREENSHOT_PATH}"
            subprocess.run(command, shell=True, timeout=10)

            if os.path.exists(SCREENSHOT_PATH):
                with open(SCREENSHOT_PATH, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption="📱 Текущий экран телефона"
                    )
                os.remove(SCREENSHOT_PATH)
            else:
                await update.message.reply_text("❌ Не удалось сделать скриншот")

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def take_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сделать фото с камеры"""
        if not await self.check_admin(update.effective_user.id):
            return

        await update.message.reply_text("📷 Делаю фото...")

        try:
            # Используем Termux API для камеры
            # Нужно установить: pkg install termux-api
            command = f"termux-camera-photo -c 0 {CAMERA_PHOTO_PATH}"
            subprocess.run(command, shell=True, timeout=10)

            if os.path.exists(CAMERA_PHOTO_PATH):
                with open(CAMERA_PHOTO_PATH, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption="📷 Фото с основной камеры"
                    )
                os.remove(CAMERA_PHOTO_PATH)
            else:
                await update.message.reply_text("❌ Не удалось сделать фото")

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def get_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получить геолокацию"""
        if not await self.check_admin(update.effective_user.id):
            return

        await update.message.reply_text("📍 Получаю местоположение...")

        try:
            # Используем Termux API для локации
            command = "termux-location"
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=10
            )

            if result.stdout:
                location_data = result.stdout
                # Парсим JSON
                import json
                loc = json.loads(location_data)

                latitude = loc.get('latitude', 0)
                longitude = loc.get('longitude', 0)
                accuracy = loc.get('accuracy', 0)

                await update.message.reply_location(
                    latitude=latitude,
                    longitude=longitude,
                    horizontal_accuracy=accuracy
                )

                await update.message.reply_text(
                    f"📍 Местоположение:\n"
                    f"Широта: {latitude}\n"
                    f"Долгота: {longitude}\n"
                    f"Точность: {accuracy}м\n"
                    f"\nhttps://maps.google.com/?q={latitude},{longitude}"
                )
            else:
                await update.message.reply_text("❌ Не удалось получить локацию")

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def get_battery(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Информация о батарее"""
        if not await self.check_admin(update.effective_user.id):
            return

        try:
            command = "termux-battery-status"
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=5
            )

            if result.stdout:
                import json
                battery = json.loads(result.stdout)

                percentage = battery.get('percentage', 0)
                status = battery.get('status', 'unknown')
                health = battery.get('health', 'unknown')
                temperature = battery.get('temperature', 0)

                status_ru = {
                    'CHARGING': 'Заряжается',
                    'DISCHARGING': 'Разряжается',
                    'FULL': 'Полная',
                    'NOT_CHARGING': 'Не заряжается'
                }.get(status, status)

                await update.message.reply_text(
                    f"🔋 СОСТОЯНИЕ БАТАРЕИ:\n"
                    f"• Заряд: {percentage}%\n"
                    f"• Статус: {status_ru}\n"
                    f"• Здоровье: {health}\n"
                    f"• Температура: {temperature / 10}°C"
                )
            else:
                await update.message.reply_text("❌ Не удалось получить данные о батарее")

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def get_network(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Информация о сети"""
        if not await self.check_admin(update.effective_user.id):
            return

        try:
            commands = {
                "IP адрес": "ip addr show wlan0 | grep 'inet ' | awk '{print $2}'",
                "Wi-Fi SSID": "termux-wifi-connectioninfo | grep ssid",
                "Сила сигнала": "termux-wifi-scaninfo | grep level",
                "Трафик": "cat /proc/net/dev | grep wlan0"
            }

            network_info = "📶 ИНФОРМАЦИЯ О СЕТИ:\n"
            for key, cmd in commands.items():
                try:
                    result = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True, timeout=5
                    )
                    if result.stdout:
                        network_info += f"• {key}: {result.stdout.strip()}\n"
                except:
                    network_info += f"• {key}: Неизвестно\n"

            await update.message.reply_text(network_info)

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def get_calls(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получить историю звонков"""
        if not await self.check_admin(update.effective_user.id):
            return

        await update.message.reply_text("📞 Получаю историю звонков...")

        try:
            # Чтение логов звонков (нужны разрешения)
            command = "termux-call-log -l 10"
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=10
            )

            if result.stdout:
                import json
                calls = json.loads(result.stdout)

                calls_text = "📞 ПОСЛЕДНИЕ 10 ЗВОНКОВ:\n\n"
                for call in calls[:10]:
                    number = call.get('phone_number', 'Неизвестно')
                    name = call.get('contact_name', 'Нет в контактах')
                    call_type = call.get('type', 'unknown')
                    date = call.get('date', 0)

                    type_ru = {
                        'INCOMING': 'Входящий',
                        'OUTGOING': 'Исходящий',
                        'MISSED': 'Пропущенный'
                    }.get(call_type, call_type)

                    from datetime import datetime
                    call_date = datetime.fromtimestamp(date / 1000).strftime("%d.%m.%Y %H:%M")

                    calls_text += f"• {type_ru}: {name} ({number})\n  {call_date}\n\n"

                await update.message.reply_text(calls_text)
            else:
                await update.message.reply_text("❌ Нет доступа к истории звонков")

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def get_contacts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получить список контактов"""
        if not await self.check_admin(update.effective_user.id):
            return

        await update.message.reply_text("📱 Получаю контакты...")

        try:
            command = "termux-contact-list"
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=10
            )

            if result.stdout:
                import json
                contacts = json.loads(result.stdout)

                contacts_text = "📱 КОНТАКТЫ (первые 20):\n\n"
                for contact in contacts[:20]:
                    name = contact.get('name', 'Без имени')
                    numbers = contact.get('number', [])

                    if numbers:
                        contacts_text += f"• {name}: {numbers[0]}\n"
                    else:
                        contacts_text += f"• {name}: Нет номера\n"

                if len(contacts) > 20:
                    contacts_text += f"\n... и ещё {len(contacts) - 20} контактов"

                await update.message.reply_text(contacts_text)
            else:
                await update.message.reply_text("❌ Нет доступа к контактам")

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def clean_storage(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Очистка временных файлов"""
        if not await self.check_admin(update.effective_user.id):
            return

        try:
            # Очистка кэша Termux
            commands = [
                "rm -rf ~/.cache/*",
                "rm -rf /data/data/com.termux/files/usr/tmp/*",
                "find /sdcard/DCIM -name 'bot_*' -delete",
                "rm -rf ~/.termux/*.tmp"
            ]

            cleaned = 0
            for cmd in commands:
                try:
                    subprocess.run(cmd, shell=True, timeout=5)
                    cleaned += 1
                except:
                    pass

            await update.message.reply_text(
                f"🗑️ Очистка завершена!\n"
                f"Удалено временных файлов: {cleaned}"
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def system_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подробная системная информация"""
        if not await self.check_admin(update.effective_user.id):
            return

        try:
            commands = {
                "Память": "free -h",
                "Диск": "df -h",
                "Процессы": "ps aux | head -20",
                "Температура": "cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | head -5"
            }

            for title, cmd in commands.items():
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=5
                )

                if result.stdout:
                    output = result.stdout[:1000]  # Ограничиваем длину
                    await update.message.reply_text(
                        f"⚙️ {title}:\n```\n{output}\n```",
                        parse_mode='Markdown'
                    )
                await asyncio.sleep(1)  # Пауза между командами

        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def handle_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий кнопок"""
        if not await self.check_admin(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён!")
            return

        text = update.message.text

        if text == "📱 Инфо":
            info = await self.get_phone_info()
            await update.message.reply_text(info)

        elif text == "📸 Скриншот":
            await self.take_screenshot(update, context)

        elif text == "📷 Фото":
            await self.take_photo(update, context)

        elif text == "📍 Гео":
            await self.get_location(update, context)

        elif text == "📞 Звонки":
            await self.get_calls(update, context)

        elif text == "📱 Контакты":
            await self.get_contacts(update, context)

        elif text == "🔋 Батарея":
            await self.get_battery(update, context)

        elif text == "📶 Сеть":
            await self.get_network(update, context)

        elif text == "🗑️ Очистка":
            await self.clean_storage(update, context)

        elif text == "⚙️ Система":
            await self.system_info(update, context)

        else:
            await update.message.reply_text("Используйте кнопки меню")

    def run(self):
        """Запуск бота"""
        if BOT_TOKEN == "BOT TOKEN":
            print("❌ ЗАМЕНИТЕ ТОКЕН БОТА!")
            return

        self.app = Application.builder().token(BOT_TOKEN).build()

        # Регистрация обработчиков
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_buttons))

        print("🤖 Android Remote Bot запущен!")
        print("📱 Управляйте телефоном через Telegram")

        self.app.run_polling()


if __name__ == "__main__":
    bot = AndroidRemoteBot()
    bot.run()