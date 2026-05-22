[app]
title = OILCALC
package.name = oilcalc
package.domain = org.oilfield.oilcalc

source.dir = .
source.include_exts = py,kv,png,jpg,atlas,ttf
source.include_patterns = calc_engine.py

version = 1.0.0

requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 27
android.minapi = 21
android.accept_sdk_license = True

android.ndk = 28c
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
