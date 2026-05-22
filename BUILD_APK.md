# Сборка OILCALC APK

Этот документ — пошаговая инструкция по сборке Android APK-файла из исходников
Kivy-версии OILCALC. На месторождении делать это **не нужно**: APK собирается
один раз на любой Linux-машине (или WSL под Windows), затем готовый файл
устанавливается на телефоны через флешку / Bluetooth.

---

## Что собираем

- **Целевой APK**: ~30–50 МБ (Python 3 + Kivy + наш код), работает на
  Android 5.0+ (API 21).
- **Архитектуры**: arm64-v8a (современные телефоны) + armeabi-v7a (старые).
- **Зависимости приложения**: только Kivy 2.3.0 (без интернета, без сетевых вызовов).

---

## Где собирать

**Поддерживается:**
- Linux (Ubuntu 22.04 / Debian 12 / Fedora — рекомендуется).
- macOS (с дополнительной настройкой).
- **Windows через WSL2** с Ubuntu — обычно проще всего.

**НЕ поддерживается:** Windows нативно. python-for-android — Linux/macOS only.

Первая сборка скачает Android SDK + NDK + OpenJDK (~3–5 ГБ) и идёт 30–90 минут.
Последующие — 2–5 минут.

---

## Установка зависимостей (Ubuntu / WSL Ubuntu)

```bash
sudo apt update
sudo apt install -y \
    python3 python3-pip python3-venv \
    git zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config zlib1g-dev \
    libncurses-dev libncursesw5-dev libtinfo6 \
    cmake libffi-dev libssl-dev \
    build-essential libsqlite3-dev libbz2-dev liblzma-dev
```

---

## Установка buildozer

В отдельном venv (чтобы не ломать систему):

```bash
python3 -m venv ~/venv-bz
source ~/venv-bz/bin/activate
pip install --upgrade pip wheel
pip install buildozer cython==3.0.11
```

Cython 3.0.x обязателен под Kivy 2.3.x.

---

## Сборка APK

1. Распакуйте `oilcalc_apk.zip` где-нибудь под Linux, например в `~/oilcalc_apk`.
2. Активируйте venv с buildozer:
   ```bash
   source ~/venv-bz/bin/activate
   cd ~/oilcalc_apk
   ```
3. Запустите debug-сборку:
   ```bash
   buildozer android debug
   ```

Первый запуск:
- скачает Android SDK, NDK, build-tools;
- скачает и скомпилирует Python 3 для Android;
- скомпилирует Kivy под ARM;
- упакует ваш `main.py + calc_engine.py` в APK.

Результат: `bin/oilcalc-1.0.0-arm64-v8a_armeabi-v7a-debug.apk`.

Это и есть **тот самый APK-файл**, который ставится на любой Android-телефон.

---

## Если буду ошибки

Типичные:

| Симптом | Причина / решение |
|---------|-------------------|
| `command not found: buildozer` | venv не активирован: `source ~/venv-bz/bin/activate`. |
| `AIDL is missing` | SDK build-tools не доскачались, повторить `buildozer android debug` (buildozer докачает). |
| `Cython compilation failed` | Cython не 3.0.x: `pip install cython==3.0.11 --force-reinstall`. |
| `JAVA_HOME is not set` | `export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64`. |
| Сборка падает при загрузке NDK | Сеть нестабильна. Перезапустить, buildozer продолжит с того же места. |
| APK устанавливается, но падает при старте | Подключите телефон в режиме отладки USB и: `adb logcat | grep -i python` — будут видны точные ошибки Python. |

---

## Release-сборка (для распространения)

Debug-APK подписан тестовым ключом и не предназначен для долгого использования
(некоторые телефоны его ограничивают через 14 дней). Для production:

1. Создать keystore:
   ```bash
   keytool -genkey -v -keystore oilcalc.keystore \
     -alias oilcalc -keyalg RSA -keysize 2048 -validity 10000
   ```
2. Добавить в `buildozer.spec`:
   ```ini
   [app]
   android.release_artifact = apk

   [app:android]
   android.keystore = /полный/путь/oilcalc.keystore
   android.keyalias = oilcalc
   ```
3. Собрать:
   ```bash
   buildozer android release
   ```

---

## Установка готового APK на телефон

1. Скопировать `bin/oilcalc-1.0.0-...-debug.apk` на телефон (через кабель,
   Bluetooth, флешку — без интернета).
2. На телефоне: разрешить «Установка из неизвестных источников»
   (Настройки → Безопасность).
3. Открыть APK файловым менеджером и нажать «Установить».
4. Иконка **OILCALC** появится в меню приложений.

Готово — приложение работает офлайн, как и Termux-версия.

---

## Тестирование на ПК до сборки APK

Полезно: можно запустить ровно тот же код Kivy на компьютере как обычное
desktop-приложение и убедиться, что всё работает:

```bash
pip install kivy==2.3.0
cd ~/oilcalc_apk
python main.py
```

Откроется окно с тем же UI. Сборка APK обязательна только перед заливкой на
телефон.
