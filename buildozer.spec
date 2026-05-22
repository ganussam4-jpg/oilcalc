[app]

# Название приложения (будет видно на экране)
title = OilCalc

# Имя пакета (должно быть уникальным)
package.name = oilcalc
package.domain = org.ganussam4jpg

# Главный файл приложения
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,woff
source.exclude_dirs = .buildozer, bin, dist, .git, __pycache__, .github, venv
source.exclude_patterns = *.spec, *.pyc, *.pyo, .DS_Store

# Точка входа
main = main.py

# Требования
requirements = python3,kivy==2.3.0

# Android настройки
orientation = portrait
fullscreen = 0

# Версии (критично для стабильной сборки)
android.api = 33
android.minapi = 21
android.ndk = 25c
android.ndk_api = 21

# Архитектура
android.arch = arm64-v8a

# Разрешения (добавь нужные, если понадобятся)
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# Метаданные
version = 1.0
version.code = 1

# Иконка и название (опционально, но рекомендуется)
# android.application_icon = icon.png
# android.application_label = OilCalc

# Дополнительные опции для стабильности
p4a.branch = develop
presplash.color = #FFFFFF

# Оптимизации
android.release = false
android.debug = true
