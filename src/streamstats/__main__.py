import argparse
import csv
import json
import sys

from streamstats.errors import StreamStatsError, CliConfigError, UnsupportedFormatError, InvalidEventError
from streamstats.parsers import make_event
from streamstats.analysis import update_stat

stats = {
    "total_events": 0,
    "by_level": {"CRITICAL": 0, 
                 "DEBUG": 0, 
                 "ERROR": 0, 
                 "INFO": 0, 
                 "WARNING": 0},
    "by_source": {
        "db": {"total": 0, 
               "error": 0}},
}


def command_parser():
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
    return analyze_parser


def main():
    parser = command_parser()
    args = parser.parse_args()
    if len(args.format) == 1:
        args.format *= len(args.input_files)
    elif len(args.format) == len(args.input_files):
        for path, file_number in enumerate(args.input_files, start=0):
            
            if path[-6:] == ".jsonl" and args.format[file_number] == "jsonl":
                with open(path, encoding="utf-8") as f:
                    for line_number, line in enumerate(f, start=1):
                        try:
                            row = json.loads(line)
                            event = make_event(row, line_number)
                            update_stat(event, stats)
                        except json.JSONDecodeError:
                            raise InvalidEventError("Некорректный jsonl", line_number)
                        
            elif path[-4:] == ".csv" and args.format[file_number] == "csv":
                with open(path, encoding="utf-8", newline="") as f:
                    headline = f.readline()
                    for csv_delimeter in [",", ";", "\t"]:
                        if csv_delimeter in headline:
                            break
                    else:
                        raise UnsupportedFormatError(f"Неверный разделитель в файле по адресу {path}")

                    f.seek(0)
                    file = csv.DictReader(f, delimiter=csv_delimeter)
                    for line_number, line in enumerate(file, start=2) :
                        event = make_event(line, line_number)
                        update_stat(event, stats)
            else:
                raise UnsupportedFormatError(f"Неверный формат файла по адресу {path}")
    else:
        raise CliConfigError("Некорректное кол-во файлов")


if __name__ == "__main__":
    try:
        main()
    except StreamStatsError as e:
        print(e.__class__, e, file=sys.stderr)
        sys.exit(2)
