[app]

# Имя приложения (что увидит пользователь под иконкой)
title = OILCALC

# Системное имя пакета
package.name = oilcalc

# Домен пакета (любой уникальный идентификатор, можно оставить)
package.domain = org.oilfield.oilcalc

# Папка с исходниками
source.dir = .

# Какие расширения файлов включать в APK
source.include_exts = py,png,jpg,kv,atlas,ttf

# Дополнительно явно включить движок
source.include_patterns = calc_engine.py

# Версия приложения
version = 1.0.0

# Что должно быть установлено внутри APK
requirements = python3,kivy==2.3.0

# Ориентация экрана
orientation = portrait

# Не fullscreen — оставляем статус-бар
fullscreen = 0

# Android-разрешения (нашему приложению ничего не нужно, но это поле
# не должно быть пустым у некоторых версий buildozer)
android.permissions = INTERNET

# Целевой API (33 = Android 13, рекомендация Google Play в 2025+)
android.api = 33

# Минимальный API (21 = Android 5.0, охватывает 99% устройств)
android.minapi = 21

# Архитектуры процессоров (arm64 - современные, armv7 - старые телефоны)
android.archs = arm64-v8a, armeabi-v7a

# Тип артефакта — именно APK (не AAB)
android.release_artifact = apk
android.debug_artifact = apk

# Использовать приватное хранилище приложения
android.private_storage = True

# Backup разрешён
android.allow_backup = True


[buildozer]

# Уровень подробности логов: 2 = debug (видно все команды)
log_level = 2

# Не предупреждать о запуске из-под root (в CI это нормально)
warn_on_root = 0
