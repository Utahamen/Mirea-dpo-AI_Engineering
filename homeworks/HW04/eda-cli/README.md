# S04 – eda_cli: мини-EDA для CSV + HTTP API

Небольшое CLI-приложение для базового анализа CSV-файлов с HTTP-сервисом для оценки качества датасетов.
Используется в рамках Семинара 04 курса «Инженерия ИИ».

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему

## Инициализация проекта

В корне проекта:

```bash
uv sync
```

Эта команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml`;
- установит сам проект `eda-cli` в окружение.

## Запуск CLI

### Краткий обзор

Команда `overview` выводит краткую информацию о датасете в консоль:

```bash
uv run eda-cli overview data/example.csv
```

Параметры:

- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`).

### Просмотр первых строк

Команда `head` выводит первые n строк CSV-файла (аналог команды `head` в Unix/Linux):

```bash
uv run eda-cli head data/example.csv --n 5
```

Параметры:

- `--n` – количество первых строк для вывода (по умолчанию `5`);
- `--sep` – разделитель в CSV (по умолчанию `,`);
- `--encoding` – кодировка файла (по умолчанию `utf-8`).

**Примеры:**

```bash
# Вывести первые 5 строк (по умолчанию)
uv run eda-cli head data/example.csv

# Вывести первые 10 строк
uv run eda-cli head data/example.csv --n 10

# С указанием разделителя и кодировки
uv run eda-cli head data/example.csv --n 3 --sep ";" --encoding "windows-1251"
```

### Полный EDA-отчёт

Команда `report` генерирует полный EDA-отчёт с таблицами и графиками:

```bash
uv run eda-cli report data/example.csv --out-dir reports
```

**Основные параметры:**

- `path` (обязательный) – путь к CSV-файлу;
- `--out-dir` – каталог для отчёта (по умолчанию `reports`);
- `--sep` – разделитель в CSV (по умолчанию `,`);
- `--encoding` – кодировка файла (по умолчанию `utf-8`).

**Дополнительные параметры:**

- `--max-hist-columns` – максимум числовых колонок для построения гистограмм (по умолчанию `6`);
- `--top-k-categories` – сколько top-значений выводить для категориальных признаков (по умолчанию `5`);
- `--title` – заголовок отчёта в Markdown (по умолчанию `"EDA-отчёт"`);
- `--min-missing-share` – порог доли пропусков (0.0–1.0), выше которого колонка считается проблемной и попадает в отдельный список в отчёте (по умолчанию `0.0`).

**Примеры использования:**

```bash
# Базовый отчёт с настройками по умолчанию
uv run eda-cli report data/example.csv

# Отчёт с кастомными параметрами
uv run eda-cli report data/example.csv \
  --out-dir my_reports \
  --max-hist-columns 10 \
  --top-k-categories 10 \
  --title "Анализ датасета example" \
  --min-missing-share 0.1

# Отчёт с указанием разделителя и кодировки
uv run eda-cli report data/example.csv \
  --sep ";" \
  --encoding "windows-1251" \
  --min-missing-share 0.05
```

В результате в каталоге `reports/` (или указанном в `--out-dir`) появятся:

- `report.md` – основной отчёт в Markdown с указанным заголовком;
- `summary.csv` – таблица по колонкам;
- `missing.csv` – пропуски по колонкам;
- `correlation.csv` – корреляционная матрица (если есть числовые признаки);
- `top_categories/*.csv` – top-k категорий по строковым признакам (k определяется `--top-k-categories`);
- `hist_*.png` – гистограммы числовых колонок (количество определяется `--max-hist-columns`);
- `missing_matrix.png` – визуализация пропусков;
- `correlation_heatmap.png` – тепловая карта корреляций.

В отчёте `report.md` будет раздел "Параметры анализа" с указанием использованных значений параметров, а при `--min-missing-share > 0` также будет добавлен список проблемных колонок с долей пропусков выше порога.

## HTTP API

Проект включает HTTP-сервис на FastAPI для оценки качества датасетов через REST API.

### Запуск сервера

```bash
uv run uvicorn eda_cli.api:app --reload --port 8000
```

После запуска сервер будет доступен по адресу `http://localhost:8000`.

### Интерактивная документация

FastAPI автоматически генерирует интерактивную документацию API:

- **Swagger UI**: http://localhost:8000/docs

### Эндпоинты

#### `GET /health`

Проверка работоспособности сервиса.

**Пример запроса:**

```bash
curl http://localhost:8000/health
```

**Пример ответа:**

```json
{
  "status": "ok",
  "service": "dataset-quality",
  "version": "0.2.0"
}
```

#### `POST /quality`

Оценка качества датасета по агрегированным признакам (без загрузки файла).

**Пример запроса:**

```bash
curl -X POST "http://localhost:8000/quality" \
  -H "Content-Type: application/json" \
  -d '{
    "n_rows": 1000,
    "n_cols": 10,
    "max_missing_share": 0.1,
    "numeric_cols": 5,
    "categorical_cols": 5
  }'
```

**Пример ответа:**

```json
{
  "ok_for_model": true,
  "quality_score": 0.9,
  "message": "Данных достаточно, модель можно обучать (по текущим эвристикам).",
  "latency_ms": 0.5,
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "too_many_missing": false,
    "no_numeric_columns": false,
    "no_categorical_columns": false
  },
  "dataset_shape": {
    "n_rows": 1000,
    "n_cols": 10
  }
}
```

#### `POST /quality-from-csv`

Оценка качества датасета по загруженному CSV-файлу с использованием EDA-ядра.

**Пример запроса:**

```bash
curl -X POST "http://localhost:8000/quality-from-csv" \
  -F "file=@data/example.csv"
```

**Пример ответа:**

```json
{
  "ok_for_model": true,
  "quality_score": 0.85,
  "message": "CSV выглядит достаточно качественным для обучения модели (по текущим эвристикам).",
  "latency_ms": 15.2,
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "too_many_missing": false,
    "has_constant_columns": false,
    "has_many_zero_values": false
  },
  "dataset_shape": {
    "n_rows": 1000,
    "n_cols": 10
  }
}
```

#### `POST /quality-flags-from-csv`

Полный набор флагов качества по загруженному CSV-файлу, включая все эвристики из HW03.

**Пример запроса:**

```bash
curl -X POST "http://localhost:8000/quality-flags-from-csv" \
  -F "file=@data/example.csv"
```

**Пример ответа:**

```json
{
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "max_missing_share": 0.05,
    "too_many_missing": false,
    "has_constant_columns": false,
    "constant_columns": [],
    "has_many_zero_values": false,
    "zero_value_columns": [],
    "has_high_cardinality_categoricals": true,
    "high_cardinality_categorical_columns": ["user_id"],
    "has_suspicious_id_duplicates": false,
    "quality_score": 0.85
  }
}
```

**Описание флагов:**

- `too_few_rows` — слишком мало строк (< 100)
- `too_many_columns` — слишком много колонок (> 100)
- `max_missing_share` — максимальная доля пропусков среди всех колонок
- `too_many_missing` — слишком много пропусков (> 50%)
- `has_constant_columns` — наличие константных колонок (≤ 1 уникальное значение)
- `constant_columns` — список константных колонок
- `has_many_zero_values` — наличие числовых колонок, состоящих только из нулей
- `zero_value_columns` — список колонок с нулевыми значениями
- `has_high_cardinality_categoricals` — наличие категориальных колонок с высокой кардинальностью (> 90% уникальных значений)
- `high_cardinality_categorical_columns` — список колонок с высокой кардинальностью
- `has_suspicious_id_duplicates` — наличие дубликатов в колонках, похожих на ID
- `quality_score` — интегральная оценка качества данных (0.0–1.0)

### Использование через Python

```python
import requests

# Загрузка CSV-файла
with open("data/example.csv", "rb") as f:
    response = requests.post(
        "http://localhost:8000/quality-flags-from-csv",
        files={"file": f}
    )
    print(response.json())
```

## Тесты

```bash
uv run pytest -q
```
