# Лабораторная работа 2. Потоковый анализатор файлов

CLI-утилита для чтения событий из CSV и JSONL, подсчёта статистики и  
формирования JSON-отчёта. Файлы читаются построчно, без загрузки в память  
целиком.  

## **Установка**  
Скопировать репозиторий
```bash
git clone https://github.com/Quilartt/lab_02/
```
Установить виртуальное окружение  
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```
Требуется Python 3.12+.

## Структура проекта
```text
lab_02/
  pyproject.toml
  README.md
  src/
    streamstats/
      __init__.py
      __main__.py     - точка входа CLI (argparse + основной цикл)
      errors.py       - иерархия исключений
      parsers.py      - make_event: валидация и нормализация события
      analysis.py     - zero_stats / update_stat: подсчёт статистики
      report.py       - create_report / write_report: сборка JSON-отчёта
  tests/
    data/
        ...               - примеры входных файлов
    test_parsers.py   
    test_analysis.py  
    test_report.py    
    test_cli.py       
```

## **Использование**  
```bash
python -m streamstats analyze INPUT [INPUT ...] --format csv|jsonl [--output REPORT.json] [--skip-invalid]
```
## **Аргументы**  

INPUT - один или несколько путей к файлам (абсолютных или относительных).  

--format - формат входных данных. Один или несколько значений через  
пробел: --format csv, --format jsonl, --format csv jsonl.  
Если указан один формат, он применяется ко всем файлам. Если несколько -  
их количество должно совпадать с количеством файлов.  

--output - путь к файлу отчёта. Если не указан, отчёт печатается  
в стандартный поток вывода (stdout).  

--skip-invalid - пропускать строки с ошибками. По умолчанию обработка  
останавливается на первой битой строке с кодом возврата 2.  

## **Примеры**
```bash
# Один JSONL, отчёт в консоль
python -m streamstats analyze events.jsonl --format jsonl

# CSV и JSONL вместе, отчёт в файл
python -m streamstats analyze events.csv events.jsonl --format csv jsonl --output report.json

# Пропускать битые строки, отчёт в консоль
python -m streamstats analyze events.jsonl --format jsonl --skip-invalid
```

## **Форматы входных данных**  
**CSV**  
Файл с заголовком. Разделитель - один из стандартных: , или ; или \t.  
Колонки в файле: timestamp, level, source, message.  
через for line in f + json.loads.

**Примеры входных файлов**  

csv  
```
timestamp,level,source,message
2026-10-13T10:00:00,INFO,app,started
2026-10-13T10:01:00,ERROR,db,connection failed JSONL
```
jsonl  
```
{"timestamp":"2026-10-13T10:00:00","level":"INFO","source":"app","message":"started"}
{"timestamp":"2026-10-13T10:01:00","level":"ERROR","source":"db","message":"connection failed"}
```

## **Модель события**  

**timestamp** - строка в формате ISO 8601;  

**level** - один из DEBUG, INFO, WARNING, ERROR, CRITICAL;  

**source** - непустая строка;  

**message** - строка.  

## **Схема отчёта**  
```json
{
  "total_events": 10,
  "by_level": {"DEBUG": 0, "INFO": 5, "WARNING": 1, "ERROR": 3, "CRITICAL": 1},
  "by_source": {"app": 7, "db": 3},
  "top_error_sources": {"db": 3},
  "first_timestamp": "2026-10-13T10:00:00",
  "last_timestamp": "2026-10-13T10:05:00",
  "skipped_invalid": 0
}
```

total_events - общее число учтённых (валидных) событий;  

by_level - количество событий по каждому уровню;  

by_source - количество событий по каждому источнику;  

top_error_sources - до 5 источников с наибольшим числом событий уровня  
ERROR/CRITICAL. При равенстве - алфавитный порядок;  

first_timestamp / last_timestamp - первая и последняя метка времени  
(по ISO 8601) или null, если событий не было;  

skipped_invalid - число пропущенных строк при --skip-invalid.  


## **Поведение при ошибках**

По умолчанию при первой же битой строке программа:  
печатает сообщение об ошибке в stderr с номером файла и строки;  
завершается с кодом возврата 2.  

С --skip-invalid:  
битая строка пропускается;  
в stderr пишется WARNING;  
счётчик skipped_invalid в отчёте увеличивается;  
обработка продолжается.  

Пустой файл - не ошибка. Отчёт будет нулевым.  

**Коды возврата**  
0 - успех;  
2 - ошибка конфигурации, данных или открытия файла.  

## **Потоковость**
Файлы читаются построчно:

CSV - через csv.DictReader;  
JSONL - через for line in f + json.loads.

События не накапливаются в памяти. Хранятся только счётчики.

Тесты
```bash
python -m pytest
```
