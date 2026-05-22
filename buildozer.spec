[app]

title = OILCALC
package.name = oilcalc
package.domain = org.oilfield.oilcalc

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.include_patterns = calc_engine.py

version = 1.0.0

requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

# Целевой API
android.api = 33
android.minapi = 21

# Стабильная связка NDK + p4a для Kivy 2.3.0
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True

# Архитектуры
android.archs = arm64-v8a, armeabi-v7a

# Тип артефакта
android.release_artifact = apk
android.debug_artifact = apk

android.private_storage = True
android.allow_backup = True


[buildozer]

log_level = 2
warn_on_root = 0
