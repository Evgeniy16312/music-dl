# План развития music-dl

Дорожная карта: десктоп-приложение (Windows + macOS), провайдер VK Music, расширяемая архитектура.

---

## Текущее состояние (v2.0)

- CLI + обёртки `ym.ps1` / `ym.cmd`
- Провайдер **Яндекс.Музыка** (`music_dl/providers/yandex/`)
- Модульная архитектура: `core` → `providers` → `pipeline` → `cli`
- Репозиторий: [Evgeniy16312/music-dl](https://github.com/Evgeniy16312/music-dl)

---

## Фаза 1 — Провайдер VK Music (CLI)

**Цель:** скачивание из VK по URL, тот же UX что у Яндекса.

### 1.1 Исследование

- [ ] Найти/выбрать API-библиотеку (официальный VK API, неофициальные обёртки для музыки)
- [ ] Авторизация: OAuth VK / токен пользователя
- [ ] Форматы URL: трек, альбом, плейлист, аудиозаписи пользователя
- [ ] Ограничения: битрейт, подписка VK Музыка, geo

### 1.2 Структура кода

```
music_dl/providers/vk/
  patterns.py      # URL regex
  auth.py          # токен, OAuth
  targets.py       # parse URL → ParsedTarget
  loaders.py       # загрузка списка треков
  track_download.py
  provider.py      # class VkMusicProvider(MusicProvider)
```

- [ ] Регистрация в `providers/registry.py`
- [ ] `parse_url()` — определение провайдера по домену (`music.yandex` vs `vk.com` / `vk.ru`)

### 1.3 CLI

- [ ] `auth vk` или отдельный `vk-auth` (уточнить UX)
- [ ] Переменная `VK_TOKEN` / файл `.vk_token`
- [ ] Тесты на реальных URL (dry-run)

### 1.4 Документация

- [ ] README: раздел VK, примеры URL
- [ ] Обновить `.cursor/rules/architecture.mdc`

**Оценка:** 1–2 недели (зависит от API и авторизации VK).

---

## Фаза 2 — Общий слой для нескольких сервисов

**Цель:** один интерфейс для Yandex + VK + будущих провайдеров.

### 2.1 Рефакторинг (при необходимости)

- [ ] Единый `AuthManager` — несколько токенов по провайдеру
- [ ] `TrackCollection` — абстракция метаданных (не только yandex `Track`)
- [ ] `pipeline/jobs.py` — фабрика job builder по провайдеру
- [ ] Конфиг: секции `yandex`, `vk` в `config.json`

### 2.2 Команды

```powershell
python ym_download.py "https://music.yandex.ru/album/123"
python ym_download.py "https://vk.com/..."   # авто-выбор провайдера
music-dl auth --provider yandex
music-dl auth --provider vk
```

**Оценка:** 3–5 дней после VK.

---

## Фаза 3 — Десктоп-приложение с UI

**Цель:** Win + macOS, без терминала для обычных пользователей.

### 3.1 Выбор стека

| Компонент | Рекомендация |
|-----------|--------------|
| UI | **Flet** (Python, Win/Mac, современный вид) |
| Бэкенд | существующий `music_dl` (без дублирования логики) |
| Сборка Win | **PyInstaller** → `.exe` |
| Сборка Mac | **PyInstaller** на macOS или GitHub Actions → `.app` / DMG |

Альтернатива UI: CustomTkinter (проще, менее «app-like»).

### 3.2 Структура

```
music_dl/
  gui/
    app.py           # точка входа Flet
    views/
      home.py        # URL + скачать
      auth.py        # вход Yandex / VK
      settings.py    # папка, качество, workers
      progress.py    # прогресс, лог, стоп
    bridge.py        # вызов pipeline в фоновом потоке
```

- [ ] Скачивание в **отдельном потоке** — UI не блокируется
- [ ] Callback прогресса из `pipeline/runner.py` (сейчас Rich → GUI events)
- [ ] Ctrl+C заменить кнопкой «Стоп»

### 3.3 Экраны (MVP)

1. **Главная** — поле URL, «Вставить из буфера», выбор провайдера (авто), «Скачать»
2. **Авторизация** — вкладки Yandex / VK, статус «вошёл / нет»
3. **Настройки** — папка, MP3/AAC, битрейт, workers
4. **Прогресс** — список треков, общий %, кнопка «Остановить»

### 3.4 Упаковка

- [ ] `pyproject.toml` — optional `[gui]` dependencies: `flet`
- [ ] `build/windows.spec` / `build/macos.spec` для PyInstaller
- [ ] GitHub Actions: сборка артефактов на push tag `v*`
- [ ] Releases: `.exe` (Win), `.dmg` или `.zip` (Mac)

### 3.5 macOS нюансы

- Подпись кода (Apple Developer) — для комфортной установки у других
- Без подписи — инструкция «ПКМ → Открыть» в README

**Оценка MVP GUI:** 2–3 недели.  
**Оценка сборки + CI:** 3–5 дней.

---

## Фаза 4 — Полировка и рост

- [ ] История загрузок
- [ ] Очередь URL
- [ ] Синхронизация «Мне нравится» / плейлистов по расписанию
- [ ] Spotify / YouTube Music (отдельные провайдеры по тому же шаблону)
- [ ] Автообновление приложения (опционально)

---

## Порядок работ (рекомендуемый)

```
Сейчас     →  CLI Yandex ✅
     ↓
Фаза 1     →  VK Music (CLI)
     ↓
Фаза 2     →  Мульти-провайдер auth + config
     ↓
Фаза 3     →  GUI (Flet) + PyInstaller Win
     ↓
Фаза 3b    →  Сборка macOS + GitHub Releases
     ↓
Фаза 4     →  Новые сервисы, фичи
```

---

## Риски

| Риск | Митигация |
|------|-----------|
| VK API меняется / закрывается | Абстракция провайдера, версионирование |
| Блокировка неофициального API | Документировать лимиты, только личное использование |
| Большой размер .exe (~100 MB) | Норма для Python; UPX / one-folder build |
| Mac без подписи | Инструкция в README + позже подпись |

---

## Следующий шаг

**Начать Фазу 1:** исследование VK Music API и прототип `providers/vk/` с парсингом одного URL трека.
