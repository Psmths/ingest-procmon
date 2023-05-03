import os
import json
from pipeline import Pipeline
import csv
import dateutil.parser as dparser
import argparse
import sys
import signal
import yaml


def handle_SIGINT(signal_number, frame):
    sys.exit()


def main():
    # Read configuration file
    with open("config.yml") as f:
        config = yaml.safe_load(f)
        es_host = config["elasticsearch"]["host"]
        es_port = config["elasticsearch"]["port"]
        es_user = config["elasticsearch"]["username"]
        es_pass = config["elasticsearch"]["password"]
        default_index = config["elasticsearch"]["defaultindex"]
        mapping_file = config["elasticsearch"]["mapping"]
        bulk_size = config["elasticsearch"]["bulksize"]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file", help="The Procmon CSV logfile to index into elasticsearch", type=str
    )
    parser.add_argument(
        "--index",
        help="The index to index documents into. If not selected, the index specified in configuration will be used.",
        type=str,
    )
    args = parser.parse_args()

    if not args.index:
        print("[~] No index specified, assuming default index: " + default_index)
        args.index = default_index

    if not args.file:
        print("[!] No input file specified! Use --file")
        quit()

    if not os.path.isfile(args.file):
        print("[!] Specified file is not valid")
        quit()

    # Read index mappings
    f = open(mapping_file)
    mapping = json.load(f)

    pipeline = Pipeline(
        args.index, mapping, es_host, es_port, es_user, es_pass, bulk_size
    )

    procmonfile = args.file

    with open(procmonfile, encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row = {k.lower().replace(" ", "_"): v for k, v in row.items()}

            if "date_&_time" in row.keys():
                row["timestamp"] = dparser.parse(
                    row["date_&_time"], fuzzy=True
                ).isoformat()
                row.pop("date_&_time")
            elif "time_of_day" in row.keys():
                row["timestamp"] = dparser.parse(
                    row["time_of_day"], fuzzy=True
                ).isoformat()
                row.pop("time_of_day")

            pipeline.ingest_json(row)

    pipeline.close_queue()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_SIGINT)
    main()
