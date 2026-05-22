[app]

title = OilCalc
package.name = oilcalc
package.domain = org.ganussam4jpg

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas
source.exclude_dirs = .buildozer, bin, dist, .git, __pycache__, .github
source.exclude_patterns = *.spec, *.pyc

main = main.py

requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk = 25c

version = 1.0
version.code = 1

p4a.branch = develop
