from io import StringIO
from django.test import TestCase
from unittest import mock

from francedata.services.utils import (
    file_exists_at_url,
    get_zip_from_url,
    parse_csv_from_distant_zip,
    parse_csv_from_stream,
)


class FileExistsAtUrlTestCase(TestCase):
    def test_url_to_valid_file_returns_true(self) -> None:
        valid_url = "https://open-collectivites.fr/mentions-legales"
        result = file_exists_at_url(valid_url)
        self.assertTrue(result)

    def test_url_to_non_existing_file_returns_false(self) -> None:
        valid_url = "https://open-collectivites.fr/no-file-here"
        result = file_exists_at_url(valid_url)
        self.assertFalse(result)


class ParseCsvFromDistantZipTestCase(TestCase):
    def test_parse_actual_csv(self) -> None:
        column_names = {
            "insee": "dep",
            "name": "libelle",
            "region": "reg",
            "seat_insee": "cheflieu",
        }

        test_result = parse_csv_from_distant_zip(
            "https://www.insee.fr/fr/statistiques/fichier/4316069/departement2020-csv.zip",
            get_zip_from_url,
            f"departement2020.csv",
            column_names,
        )
        self.assertEqual(
            test_result[0],
            {"insee": "01", "name": "Ain", "region": "84", "seat_insee": "01053"},
        )


class ParseCsvFromStreamTestCase(TestCase):
    SAMPLE_CSV_DEPT = StringIO(
        """\
dep,reg,cheflieu,tncc,ncc,nccenr,libelle
01,84,01053,5,AIN,Ain,Ain
02,32,02408,5,AISNE,Aisne,Aisne"""
    )

    COLUMN_NAMES_DEPT = {
        "insee": "dep",
        "name": "libelle",
        "region": "reg",
        "seat_insee": "cheflieu",
    }

    SAMPLE_CSV_COM = StringIO(
        """\
typecom,com,reg,dep,arr,tncc,ncc,nccenr,libelle,can,comparent
COM,01001,84,01,012,5,ABERGEMENT CLEMENCIAT,Abergement-Clémenciat,L'Abergement-Clémenciat,0108,
COMD,01015,,,,1,ARBIGNIEU,Arbignieu,Arbignieu,,01015"""
    )

    COLUMN_NAMES_COM = {"insee": "com", "name": "libelle", "dept": "dep"}

    def test_parse_csv_from_stream_without_typecheck(self) -> None:
        test_result = parse_csv_from_stream(
            self.SAMPLE_CSV_DEPT, self.COLUMN_NAMES_DEPT
        )
        self.assertEqual(len(test_result), 2)

        self.assertEqual(
            test_result[0],
            {"insee": "01", "name": "Ain", "region": "84", "seat_insee": "01053"},
        )

        self.assertEqual(
            test_result[1],
            {"insee": "02", "name": "Aisne", "region": "32", "seat_insee": "02408"},
        )

    def test_parse_csv_from_stream_with_typecheck(self) -> None:
        typecheck = {"column": "typecom", "value": "COM"}

        test_result = parse_csv_from_stream(
            self.SAMPLE_CSV_COM, self.COLUMN_NAMES_COM, typecheck
        )
        self.assertEqual(len(test_result), 1)

        self.assertEqual(
            test_result[0],
            {"insee": "01001", "name": "L'Abergement-Clémenciat", "dept": "01"},
        )
