# Music Downloader (Yandex Music)

CLI для скачивания альбомов, плейлистов и треков из **Яндекс.Музыки** в MP3/AAC.  
Построен на [yandex-music](https://github.com/MarshalX/yandex-music-api), архитектура позволяет добавлять другие стриминги.

## Возможности

- Скачивание по URL: альбом, трек, плейлист, «Мне нравится», треки артиста
- OAuth через Device Flow (`auth`)
- Параллельная загрузка, ID3-теги, прогресс-бар
- Конфиг, повтор ошибок, `--dry-run`
- Обёртка `ym.ps1` — вставил ссылку из буфера и Enter

## Установка

```powershell
git clone https://github.com/Evgeniy16312/music-dl.git
cd music-dl
pip install -r requirements.txt
```

Или с установкой команды `music-dl`:

```powershell
pip install -e .
```

Файлы по умолчанию: `%USERPROFILE%\Music\YandexMusic\`

## Быстро: только ссылка

Скопируй URL в буфер обмена и запусти — команда подставится сама:

```powershell
.\ym.ps1
```

Или с URL сразу:

```powershell
.\ym.ps1 "https://music.yandex.ru/album/12345"
.\ym.cmd "https://music.yandex.ru/artist/3379147/tracks"
```

То же через Python (без `download`):

```powershell
python ym_download.py "https://music.yandex.ru/album/12345"
```

Чтобы вызывать `ym` из любой папки, добавь в профиль PowerShell:

```powershell
Set-Alias ym "C:\path\to\music-dl\ym.ps1"
```

---

## Авторизация (один раз)

```powershell
python ym_download.py auth
```

1. Открой ссылку из терминала и введи код.
2. **Не закрывай терминал** — дождись `Авторизация OK`.
3. Токен сохранится в `.token` (файл в `.gitignore`).

Токен также можно передать через:
- переменную окружения `YANDEX_MUSIC_TOKEN`
- флаг `--token` (строка или путь к файлу)

---

## Команды

| Команда | Описание |
|---------|----------|
| `auth` | Получить OAuth-токен через Device Flow |
| `init-config` | Создать пример файла настроек |
| `download` | Скачать альбом, плейлист, трек или «Мне нравится» |
| `pick` | Интерактивно выбрать плейлист(ы) и скачать |
| `list-playlists` | Показать список своих плейлистов |

Справка по любой команде:

```powershell
python ym_download.py --help
python ym_download.py download --help
python ym_download.py auth --help
python ym_download.py pick --help
python ym_download.py list-playlists --help
python ym_download.py init-config --help
```

---

### `auth` — авторизация

```powershell
python ym_download.py auth
python ym_download.py auth --token-file D:\secrets\ym.token
```

| Флаг | Описание |
|------|----------|
| `--token-file` | Куда сохранить access_token (по умолчанию `.token` в папке скрипта) |

---

### `init-config` — настройки по умолчанию

```powershell
python ym_download.py init-config
```

Создаёт `%APPDATA%\ym_download\config.json` (если файла ещё нет):

```json
{
  "output": "C:\\Users\\...\\Music\\YandexMusic",
  "bitrate": 320,
  "codec": "mp3",
  "skip_existing": true,
  "workers": 3,
  "filename_template": "{n:02d} - {artist} - {title}",
  "embed_tags": true,
  "flat": false
}
```

Значения из конфига подхватываются командами `download` и `pick`, их можно переопределить флагами.

---

### `download` — скачивание

**Сокращённый вызов** — можно не писать `download`, если первый аргумент — URL или цель:

```powershell
python ym_download.py "https://music.yandex.ru/album/12345"
python ym_download.py likes
```

**Полный синтаксис:**

```powershell
python ym_download.py download [цель ...] [опции]
```

#### Какую ссылку давать?

| Ссылка | Что скачает |
|--------|-------------|
| `.../album/42432434` | **Один альбом** |
| `.../artist/3379147/tracks` | **Треки** со вкладки «Треки» |
| `.../artist/3379147` | Все альбомы — **только с `--all-albums`** |

#### Форматы цели (`targets`)

Можно указать **несколько целей** подряд:

| Формат | Пример |
|--------|--------|
| URL альбома | `https://music.yandex.ru/album/12345` |
| ID альбома | `12345` |
| URL трека | `https://music.yandex.ru/album/123/track/456` |
| ID трека | `track/456` или `track:456` |
| URL треков артиста | `https://music.yandex.ru/artist/3379147/tracks` |
| URL артиста (все альбомы) | `https://music.yandex.ru/artist/3379147` + `--all-albums` |
| URL плейлиста (user/kind) | `https://music.yandex.ru/users/login/playlists/3` |
| Плейлист user/kind | `login/3` |
| URL плейлиста (uuid) | `https://music.yandex.ru/playlists/lk.xxxxxxxx-...` |
| «Мне нравится» | `likes`, `лайки`, `мне нравится` |
| URL likes | `https://music.yandex.ru/users/login/likes` |

#### Примеры

```powershell
# альбом
python ym_download.py download "https://music.yandex.ru/album/12345"

# один трек
python ym_download.py "https://music.yandex.ru/album/123/track/456"

# треки артиста (вкладка «Треки»)
.\ym.ps1 "https://music.yandex.ru/artist/3379147/tracks"

# один альбом
.\ym.ps1 "https://music.yandex.ru/album/12345"

# все альбомы артиста (явно)
python ym_download.py "https://music.yandex.ru/artist/3379147" --all-albums

# плейлист по ссылке
python ym_download.py download "https://music.yandex.ru/playlists/lk.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# «Мне нравится»
python ym_download.py download likes

# несколько целей за один запуск
python ym_download.py download URL1 URL2 likes

# список URL из файла (по одному на строку, # — комментарий)
python ym_download.py download --targets-file urls.txt

# только треки 5–10
python ym_download.py download "URL" --from 5 --to 10

# план без скачивания
python ym_download.py download "URL" --dry-run

# параллельная загрузка
python ym_download.py download "URL" --workers 4

# повторить упавшие треки
python ym_download.py download --retry-failed "D:\Music\Album\.ym_download_failed.json"
```

#### Опции `download`

| Флаг | Описание |
|------|----------|
| `-o`, `--output` | Папка назначения (по умолчанию `%USERPROFILE%\Music\YandexMusic`) |
| `--token` | OAuth access_token или путь к файлу с токеном |
| `--bitrate` | 320, 256, 192, 128, 64 (по умолчанию 320) |
| `--codec` | `mp3` или `aac` (файлы `.mp3` / `.m4a`) |
| `--skip-existing` | Не перекачивать существующие файлы **(включено по умолчанию)** |
| `--force` | Перекачать даже если файл уже есть |
| `--flat` | Не создавать подпапку с названием альбома/плейлиста |
| `--dry-run` | Показать план загрузки без скачивания |
| `--workers` | Число параллельных загрузок (по умолчанию 3) |
| `--template` | Шаблон имени файла (см. ниже) |
| `--no-tags` | Не записывать ID3-теги и обложку |
| `--from N` | Скачать начиная с трека N |
| `--to N` | Скачать по трек N включительно |
| `--retry-failed` | Повторить загрузку из `.ym_download_failed.json` |
| `--targets-file` | Файл со списком URL (по одному на строку) |
| `--artist-scope` | Для URL артиста: `all` (по умолчанию), `discography`, `direct`, `also` |

**Скачивание артиста** (`--artist-scope`):

| Значение | Что скачивает |
|----------|---------------|
| `all` | Все альбомы без дубликатов (по умолчанию) |
| `discography` | Дискография |
| `direct` | Собственные альбомы артиста |
| `also` | Сборники и альбомы с участием артиста |

Если выбранный scope пуст, скрипт автоматически попробует `all`.

Файлы складываются в `{output}/{Имя артиста}/{Название альбома}/`.

**Шаблон имени файла** (`--template`):

Доступные поля: `{n}`, `{artist}`, `{title}`, `{album}`, `{year}`.

```powershell
python ym_download.py download "URL" --template "{artist} - {title}"
python ym_download.py download "URL" --template "{n:02d} - {artist} - {title}"
```

После скачивания в папку альбома/плейлиста записывается `.ym_download_failed.json` — список треков, которые не удалось скачать.

---

### `pick` — интерактивный выбор плейлиста

Показывает пронумерованный список плейлистов, затем спрашивает, что скачать.

```powershell
python ym_download.py pick
python ym_download.py pick -o D:\Music --workers 4
```

При запросе можно ввести:
- номер: `3`
- несколько номеров: `1,3,5`
- все плейлисты: `all` или `*`
- «Мне нравится»: `likes` или `лайки`

Команда `pick` поддерживает **все те же опции**, что и `download` (`-o`, `--workers`, `--template` и т.д.).

---

### `list-playlists` — список плейлистов

```powershell
python ym_download.py list-playlists
python ym_download.py list-playlists --token D:\secrets\ym.token
```

| Флаг | Описание |
|------|----------|
| `--token` | OAuth access_token или путь к файлу |

Выводит пронумерованный список — номера можно использовать в `pick`.

---

## Структура файлов на диске

По умолчанию:

```
%USERPROFILE%\Music\YandexMusic\
  Название альбома — Исполнитель (2020)\
    01 - Artist - Track.mp3
    02 - Artist - Track.mp3
    .ym_download_failed.json   ← только если были ошибки

  Имя артиста\                ← при скачивании по URL артиста
    Альбом 1 — Artist (2019)\
      01 - Artist - Track.mp3
    Альбом 2 — Artist (2021)\
      ...
```

С флагом `--flat` файлы кладутся прямо в `-o` без подпапки.

---

## Архитектура проекта

```
music_dl/
  cli/              # команды и argparse
  core/             # модели, конфиг, общие утилиты
  providers/        # провайдеры стримингов (сейчас: yandex/)
  pipeline/         # загрузка, теги, лог ошибок
ym_download.py      # точка входа (совместимость)
ym.ps1 / ym.cmd     # обёртка «только URL»
.cursor/rules/      # правила для Cursor AI
```

Запуск:
```powershell
python ym_download.py "URL"      # как раньше
python -m music_dl "URL"           # модульный запуск
```

Новый стриминг — новая папка в `providers/` + регистрация в `providers/registry.py`. Подробности в `.cursor/rules/architecture.mdc`.

---

## Публикация на GitHub

### 1. Создай репозиторий на GitHub

1. Открой [github.com/new](https://github.com/new)
2. **Repository name:** `music-dl` (или другое)
3. **Public** / Private — на выбор
4. **Не** ставь галочки «Add README» / «Add .gitignore» — они уже есть локально
5. Create repository

### 2. Первый коммит и push (PowerShell)

Замени `YOUR_USERNAME` на свой логин GitHub (для этого репозитория: `Evgeniy16312`):

```powershell
cd C:\Users\turin\Scripts\yandex-music-download

git add .
git status
git commit -m "Initial release: Yandex Music downloader with extensible provider architecture"

git branch -M main
git remote add origin https://github.com/Evgeniy16312/music-dl.git
git push -u origin main
```

Файл `.token` в коммит **не попадёт** — он в `.gitignore`.

### 3. Оформи репозиторий на GitHub

- **About** (шестерёнка справа): описание `CLI downloader for Yandex Music`, topics: `yandex-music`, `python`, `cli`, `downloader`
- В `pyproject.toml` указан репозиторий `Evgeniy16312/music-dl`
- По желанию: **Releases** → Create release → tag `v2.0.0`

### 4. Клонирование на другом ПК

```powershell
git clone https://github.com/Evgeniy16312/music-dl.git
cd music-dl
pip install -r requirements.txt
python ym_download.py auth
```

---

## Быстрый старт

```powershell
pip install -r requirements.txt
python ym_download.py auth
python ym_download.py init-config
python ym_download.py list-playlists
python ym_download.py pick
```

## Лицензия

MIT — см. [LICENSE](LICENSE).

## Disclaimer

Неофициальный инструмент. Используй только для личного архивирования контента, на который у тебя есть право доступа в сервисе.
