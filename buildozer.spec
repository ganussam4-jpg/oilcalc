[app]

title = OILCALC
package.name = oilcalc
package.domain = org.oilfield.oilcalc

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.include_patterns = calc_engine.py

version = 1.0.0

requirements = python3,kivy==2.3.0

# Фиксируем стабильный p4a 2024.01.21 — последний релиз с Python 3.11.
# Master содержит Python 3.14, под который Kivy 2.3.0 не собирается.
p4a.branch = master
p4a.commit = 2024.01.21

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

# Стабильные API
android.api = 33
android.minapi = 21

# Фиксируем версию build-tools, чтобы не пыталось скачать 37 (новейшие, с непринятой лицензией)
android.build_tools_version = 33.0.2

# Стабильный NDK для Kivy 2.3
# android.ndk = 25b

# КЛЮЧЕВОЕ: автоматически принимать ВСЕ лицензии SDK
android.accept_sdk_license = True

# Архитектуры
android.archs = arm64-v8a, armeabi-v7a

# Тип артефакта — именно APK
android.release_artifact = apk
android.debug_artifact = apk

android.private_storage = True
android.allow_backup = True


[buildozer]

log_level = 2
warn_on_root = 0
