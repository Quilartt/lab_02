import argparse
import csv
import json
import logging
import sys

from streamstats.analysis import update_stat, zero_stats
from streamstats.errors import (
    CliConfigError,
    InvalidEventError,
    StreamStatsError,
    UnsupportedFormatError,
)
from streamstats.parsers import make_event
from streamstats.report import create_report, write_report

logger = logging.getLogger("streamstats")


def command_parser() -> argparse.ArgumentParser:
    """Парсит аргументы командной строки"""

    parser = argparse.ArgumentParser(
        description="Потоковый анализатор файлов", prog="streamstats"
    )
    subparser = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparser.add_parser("analyze")

    analyze_parser.add_argument(
        "input_files",
        metavar="INPUT",
        nargs="+",
        help=("Путь к входящему файлу/файлам"),
    )
    analyze_parser.add_argument(
        "--format",
        nargs="+",
        choices=["csv", "jsonl"],
        required=True,
        type=str,
        help="Формат файла/файлов (csv или jsonl)",
    )
    analyze_parser.add_argument(
        "--output",
        metavar="OUTPUT",
        type=str,
        help="Путь к файлу для сохранения отчета",
    )
    analyze_parser.add_argument(
        "--skip-invalid",
        action="store_true",
        help="Пропускать строки с ошибками",
    )
    return parser


def main() -> None:
    """Основная функция для запуска программы"""
    stats = zero_stats()
    parser = command_parser()
    args = parser.parse_args()
    if len(args.format) == 1:
        formats = args.format * len(args.input_files)
    elif len(args.format) == len(args.input_files):
        formats = args.format
    else:
        raise CliConfigError("Некорректное кол-во файлов")

    for file_number, path in enumerate(args.input_files, start=1):

        if path[-6:] == ".jsonl" and formats[file_number - 1] == "jsonl":
            try:
                with open(path, encoding="utf-8-sig") as f:
                    for line_number, line in enumerate(f, start=1):
                        try:
                            try:
                                row = json.loads(line)
                            except json.JSONDecodeError as e:
                                raise InvalidEventError(
                                    f"Некорректная строка {line_number} в файле {file_number}"
                                ) from e

                            event = make_event(row, line_number, file_number)
                            update_stat(event, stats)
                        except StreamStatsError as e:
                            # --skip-invalid: битые строки пропускаем, но пишем WARNING
                            if args.skip_invalid:
                                logger.warning("file %s: %s", path, e)
                                stats["skipped_invalid"] += 1
                                continue
                            raise
            except (OSError, UnicodeDecodeError) as e:
                raise StreamStatsError(
                    f"Не удалось прочитать файл {file_number}: {path}: {e}"
                ) from e
        elif path[-4:] == ".csv" and formats[file_number - 1] == "csv":
            try:
                with open(path, encoding="utf-8-sig", newline="") as f:
                    headline = f.readline()
                    if not headline:
                        continue
                    for csv_delimiter in [",", ";", "\t"]:
                        if csv_delimiter in headline:
                            break
                    else:
                        raise UnsupportedFormatError(
                            f"Неверный разделитель в файле {file_number}"
                        )

                    f.seek(0)
                    file = csv.DictReader(f, delimiter=csv_delimiter)
                    for line_number, line in enumerate(file, start=2):
                        try:
                            event = make_event(line, line_number, file_number)
                            update_stat(event, stats)
                        except StreamStatsError as e:
                            # --skip-invalid: битые строки пропускаем, но пишем WARNING
                            if args.skip_invalid:
                                logger.warning("file %s: %s", path, e)
                                stats["skipped_invalid"] += 1
                                continue
                            raise
            except (OSError, UnicodeDecodeError) as e:
                raise StreamStatsError(
                    f"Не удалось прочитать файл {file_number}: {path}: {e}"
                ) from e
    report = create_report(stats)
    write_report(report, args.output)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.WARNING, 
        format="%(levelname)s: %(message)s")
    try:
        main()
    except StreamStatsError as e:
        print(f"streamstats: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)
    