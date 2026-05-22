[app]

title = OILCALC
package.name = oilcalc
package.domain = org.oilfield.oilcalc

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.include_patterns = calc_engine.py

version = 1.0.0

requirements = python3,kivy==2.3.0

# Стабильный тег p4a v2024.01.21 — последний релиз с Python 3.11.
# Это рабочая связка с Kivy 2.3.0.
p4a.branch = v2024.01.21

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.2

# NDK r25b — рекомендован командой p4a для версии 2024.01.21
android.ndk = 25b

android.accept_sdk_license = True

android.archs = arm64-v8a, armeabi-v7a

android.release_artifact = apk
android.debug_artifact = apk

android.private_storage = True
android.allow_backup = True


[buildozer]

log_level = 2
warn_on_root = 0
