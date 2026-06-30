# Music Downloader (Yandex Music)

[![GitHub](https://img.shields.io/github/stars/Evgeniy16312/music-dl?style=social)](https://github.com/Evgeniy16312/music-dl)

CLI для скачивания альбомов, плейлистов и треков из **Яндекс.Музыки** в MP3/AAC.

- **Репозиторий:** [github.com/Evgeniy16312/music-dl](https://github.com/Evgeniy16312/music-dl)
- **API:** [yandex-music](https://github.com/MarshalX/yandex-music-api)
- **Лицензия:** MIT

Архитектура с провайдерами — сейчас Яндекс.Музыка, позже можно добавить другие стриминги.

---

## Содержание

- [Возможности](#возможности)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Быстро: только ссылка (ym.ps1)](#быстро-только-ссылка-ymps1)
- [Авторизация](#авторизация)
- [Какую ссылку давать](#какую-ссылку-давать)
- [Команды](#команды)
- [Качество звука](#качество-звука)
- [Остановка скачивания](#остановка-скачивания)
- [Структура файлов](#структура-файлов-на-диске)
- [Архитектура](#архитектура-проекта)
- [GitHub и разработка](#github-и-разработка)
- [Disclaimer](#disclaimer)

---

## Возможности

- Скачивание по URL: альбом, трек, плейлист, «Мне нравится», треки артиста
- OAuth через Device Flow (`auth`)
- Параллельная загрузка (`--workers`), ID3-теги, прогресс-бар (Rich)
- Конфиг `%APPDATA%\ym_download\config.json`
- Пропуск уже скачанного (`--skip-existing` по умолчанию)
- Повтор упавших треков (`--retry-failed`)
- `--dry-run` — план без скачивания
- Обёртка `ym.ps1` — вставил ссылку из буфера и Enter

---

## Установка

### С GitHub

```powershell
git clone https://github.com/Evgeniy16312/music-dl.git
cd music-dl
pip install -r requirements.txt
```

### Установка как пакета (команда `music-dl`)

```powershell
pip install -e .
music-dl --help
```

Файлы по умолчанию: `%USERPROFILE%\Music\YandexMusic\`

---

## Быстрый старт

```powershell
cd music-dl
pip install -r requirements.txt

# 1. Авторизация (один раз)
python ym_download.py auth

# 2. Настройки (опционально)
python ym_download.py init-config

# 3. Скачать
python ym_download.py "https://music.yandex.ru/album/12345"
```

---

## Быстро: только ссылка (ym.ps1)

**Важно:** нельзя просто вставить URL в терминал — PowerShell воспримет его как команду. Нужна обёртка:

```powershell
# ссылка уже в буфере обмена (Ctrl+C в браузере)
.\ym.ps1

# или с URL сразу
.\ym.ps1 "https://music.yandex.ru/album/36306494/track/138401238"
.\ym.cmd "https://music.yandex.ru/artist/3379147/tracks"
```

Если `ym.ps1` блокируется политикой:

```powershell
powershell -ExecutionPolicy Bypass -File .\ym.ps1
```

Вызов из любой папки (добавь в профиль PowerShell):

```powershell
Set-Alias ym "C:\path\to\music-dl\ym.ps1"
ym
```

То же через Python (можно не писать `download`):

```powershell
python ym_download.py "https://music.yandex.ru/album/12345"
python -m music_dl "https://music.yandex.ru/album/12345"
```

---

## Авторизация

```powershell
python ym_download.py auth
```

1. Открой ссылку из терминала и введи код.
2. **Не закрывай терминал** — дождись `Авторизация OK`.
3. Токен сохранится в `.token` (файл в `.gitignore`, **не попадает в Git**).

Другие способы передать токен:

| Способ | Пример |
|--------|--------|
| Файл | `.token` в корне проекта |
| Переменная окружения | `YANDEX_MUSIC_TOKEN` |
| Флаг | `--token путь\к\файлу` или `--token "строка"` |

---

## Какую ссылку давать

| Ссылка | Что скачает |
|--------|-------------|
| `.../album/42432434` | **Один альбом** (или сингл) |
| `.../album/123/track/456` | **Один трек** |
| `.../artist/3379147/tracks` | **Треки** со вкладки «Треки» |
| `.../artist/3379147` | Все альбомы — **только с `--all-albums`** |
| `likes` | «Мне нравится» |

Если нашёл альбом на странице артиста — **кликни по обложке** и скопируй URL с `/album/`, а не `/artist/`.

---

## Команды

| Команда | Описание |
|---------|----------|
| `auth` | OAuth-токен через Device Flow |
| `init-config` | Пример `config.json` |
| `download` | Скачать альбом / плейлист / трек |
| `pick` | Интерактивный выбор плейлиста |
| `list-playlists` | Список своих плейлистов |

```powershell
python ym_download.py --help
python ym_download.py download --help
```

### `init-config`

Создаёт `%APPDATA%\ym_download\config.json`:

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

### Форматы цели (`targets`)

| Формат | Пример |
|--------|--------|
| URL альбома | `https://music.yandex.ru/album/12345` |
| ID альбома | `12345` |
| URL трека | `https://music.yandex.ru/album/123/track/456` |
| URL треков артиста | `https://music.yandex.ru/artist/3379147/tracks` |
| URL артиста (все альбомы) | `.../artist/3379147` + `--all-albums` |
| Плейлист user/kind | `login/3` |
| «Мне нравится» | `likes`, `лайки` |

### Примеры

```powershell
# альбом
python ym_download.py "https://music.yandex.ru/album/12345"

# треки артиста
.\ym.ps1 "https://music.yandex.ru/artist/3379147/tracks"

# все альбомы артиста (явно!)
python ym_download.py "https://music.yandex.ru/artist/3379147" --all-albums

# несколько целей
python ym_download.py download URL1 URL2 likes

# из файла (по одному URL на строку)
python ym_download.py download --targets-file urls.txt

# план без скачивания
python ym_download.py "URL" --dry-run

# повтор упавших
python ym_download.py download --retry-failed "D:\Music\Album\.ym_download_failed.json"
```

### Опции `download` / `pick`

| Флаг | Описание |
|------|----------|
| `-o`, `--output` | Папка назначения |
| `--token` | OAuth-токен или путь к файлу |
| `--bitrate` | 320, 256, 192, 128, 64 (по умолчанию 320) |
| `--codec` | `mp3` или `aac` (`.mp3` / `.m4a`) |
| `--skip-existing` | Не перекачивать (**включено по умолчанию**) |
| `--force` | Перекачать всё заново |
| `--flat` | Без подпапки альбома |
| `--dry-run` | Только план |
| `--workers` | Параллельных загрузок (по умолчанию 3) |
| `--template` | Шаблон имени: `{n}`, `{artist}`, `{title}`, `{album}`, `{year}` |
| `--no-tags` | Без ID3-тегов и обложки |
| `--from N` / `--to N` | Диапазон треков |
| `--all-albums` | Для `/artist/` без `/tracks` |
| `--artist-scope` | `all`, `discography`, `direct`, `also` |
| `--retry-failed` | Повтор из `.ym_download_failed.json` |
| `--targets-file` | Файл со списком URL |

### `pick`

```powershell
python ym_download.py pick
```

Ввод: `3`, `1,3,5`, `all`, `likes`.

---

## Качество звука

По умолчанию: **MP3 320 kbps** — максимум, который отдаёт Яндекс.Музыка через API.

- **FLAC / lossless** — недоступен через этот API
- Нужна **подписка** Яндекс.Музыки для высокого качества
- AAC: `--codec aac`
- Перекачать в лучшем качестве: `--force --bitrate 320`

---

## Остановка скачивания

| Действие | Результат |
|----------|-----------|
| **Ctrl+C** | Остановка (дождётся текущих 1–3 треков) |
| **Ctrl+C дважды** | Выход сразу |
| Закрыть терминал | Принудительная остановка |

Уже скачанные файлы при повторном запуске **пропускаются** (`--skip-existing`).

Для более быстрой отмены:

```powershell
python ym_download.py "URL" --workers 1
```

---

## Структура файлов на диске

```
%USERPROFILE%\Music\YandexMusic\
  Название альбома — Исполнитель (2020)\
    01 - Artist - Track.mp3
    .ym_download_failed.json   ← если были ошибки

  Имя артиста — треки\       ← /artist/.../tracks
    01 - Artist - Track.mp3
```

---

## Архитектура проекта

```
music_dl/
  cli/              # команды и argparse
  core/             # модели, конфиг, общие утилиты
  providers/        # провайдеры стримингов (yandex/)
  pipeline/         # загрузка, теги, лог ошибок
ym_download.py      # точка входа
ym.ps1 / ym.cmd     # обёртка «только URL»
.cursor/rules/      # правила для Cursor AI
```

Новый стриминг → папка `providers/<name>/` + регистрация в `providers/registry.py`.  
Подробности: `.cursor/rules/architecture.mdc`

---

## GitHub и разработка

**Репозиторий:** [https://github.com/Evgeniy16312/music-dl](https://github.com/Evgeniy16312/music-dl)

### Клонирование

```powershell
git clone https://github.com/Evgeniy16312/music-dl.git
cd music-dl
pip install -r requirements.txt
python ym_download.py auth
```

### Внесение изменений

```powershell
git add .
git commit -m "описание изменений"
git push
```

Файлы, которые **не попадают** в Git (`.gitignore`):

- `.token` — OAuth-токен
- `__pycache__/`, `.venv/`
- `.env`

### Оформление репозитория на GitHub

На странице репозитория → **About** (шестерёнка):

- **Description:** `CLI downloader for Yandex Music (MP3/AAC), extensible architecture`
- **Topics:** `yandex-music`, `python`, `cli`, `downloader`, `music`

**Releases** (опционально): tag `v2.0.0`, описание из раздела «Возможности».

### Структура репозитория

| Файл / папка | Назначение |
|--------------|------------|
| `music_dl/` | Основной код |
| `ym_download.py` | Точка входа |
| `ym.ps1`, `ym.cmd` | Обёртки для Windows |
| `requirements.txt` | Зависимости |
| `pyproject.toml` | Метаданные пакета, `pip install -e .` |
| `LICENSE` | MIT |
| `.cursor/rules/` | Правила архитектуры для Cursor |

---

## Disclaimer

Неофициальный инструмент. Используй только для **личного архивирования** контента, на который у тебя есть право доступа в сервисе.

## Лицензия

MIT — см. [LICENSE](LICENSE).
