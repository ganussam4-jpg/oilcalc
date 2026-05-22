[app]

title = OilCalc
package.name = oilcalc
package.domain = org.ganussam4jpg

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,woff
source.exclude_dirs = .buildozer, bin, dist, .git, __pycache__, .github, venv
source.exclude_patterns = *.spec, *.pyc, *.pyo

main = main.py

requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

# Важные настройки для стабильной сборки
android.api = 33
android.minapi = 21
android.ndk = 25c
android.ndk_api = 21
android.arch = arm64-v8a

android.permissions = INTERNET, ACCESS_NETWORK_STATE

version = 1.0
version.code = 1

p4a.branch = develop
presplash.color = #FFFFFF
