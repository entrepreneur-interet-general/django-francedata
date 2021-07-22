import csv
from typing import Callable
import requests
from zipfile import ZipFile
from io import BytesIO, TextIOWrapper
from importlib import resources


def parse_csv_from_distant_zip(
    zip_url: str,
    get_zip_method: Callable[[str], ZipFile],
    csv_name: str,
    column_names: dict,
    typecheck: dict = False,
) -> list:
    with get_zip_method(zip_url) as zip_file:
        with zip_file.open(csv_name) as csv_file:
            stream = TextIOWrapper(csv_file, encoding="utf-8-sig")
            return parse_csv_from_stream(stream, column_names, typecheck)


def parse_csv_from_stream(
    stream,
    column_names: dict,
    typecheck: dict = False,
):
    reader = csv.DictReader(stream)
    entries = []
    if typecheck:
        tc_col = typecheck["column"]
        tc_val = typecheck["value"]

    for row in reader:
        if typecheck:
            if row[tc_col] != tc_val:
                continue
        entry = {}
        # Parse all the columns
        for key, val in column_names.items():
            entry[key] = row[val]
        entries.append(entry)
    return entries


def add_sirens_and_categories(input_file, model_name, year_entry):
    with resources.open_text("francedata.resources", input_file) as input_csv:
        reader = csv.DictReader(input_csv)
        for row in reader:
            insee = row["Insee"]
            siren = row["Siren"]
            category = row["CATEG"]

            if category != "ML":
                # The Métropole de Lyon is managed only at the EPCI level
                try:
                    collectivity_entry = model_name.objects.get(
                        insee=insee, years=year_entry
                    )
                    collectivity_entry.siren = siren
                    collectivity_entry.category = category
                    collectivity_entry.save()
                except:
                    print(f"{model_name} {insee} not found")


def file_exists_at_url(url: str) -> bool:
    r = requests.head(url)
    return r.status_code == requests.codes.ok


def get_zip_from_url(zip_url: str) -> ZipFile:
    zip_name = requests.get(zip_url).content
    zip_file = ZipFile(BytesIO(zip_name))
    return zip_file
