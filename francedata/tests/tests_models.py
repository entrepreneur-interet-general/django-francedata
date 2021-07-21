from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from francedata.models import (
    Commune,
    CommuneData,
    DepartementData,
    Epci,
    DataSource,
    DataYear,
    Departement,
    EpciData,
    Metadata,
    Region,
    RegionData,
)


class MetadataTestCase(TestCase):
    def setUp(self) -> None:
        Metadata.objects.create(prop="Test", value="first")
        Metadata.objects.create(prop="Test", value="second")

    def test_metadata_is_created(self) -> None:
        test_item = Metadata.objects.get(prop="Test", value="first")
        self.assertEqual(test_item.value, "first")

    def test_metadata_prop_can_have_several_values(self) -> None:
        test_items = Metadata.objects.filter(prop="Test")
        self.assertEqual(test_items.count(), 2)


class DataYearTestCase(TestCase):
    def setUp(self) -> None:
        DataYear.objects.create(year=2020)

    def test_datayear_is_created(self) -> None:
        test_item = DataYear.objects.get(year=2020)
        self.assertEqual(test_item.year, 2020)

    def test_datayear_has_no_duplicate(self) -> None:
        with self.assertRaises(IntegrityError):
            DataYear.objects.create(year=2020)


class DataSourceTestCase(TestCase):
    def setUp(self) -> None:
        year = DataYear.objects.create(year=2020)
        DataSource.objects.create(
            title="Test title", url="http://test-url.com", year=year
        )

    def test_datasource_is_created(self) -> None:
        test_item = DataSource.objects.get(year__year=2020)
        self.assertEqual(test_item.title, "Test title")
        self.assertEqual(test_item.url, "http://test-url.com")

    def test_datasource_has_no_duplicate(self) -> None:
        with self.assertRaises(IntegrityError):
            year = DataYear.objects.create(year=2020)
            DataSource.objects.create(
                title="Test title", url="http://test-url.com", year=year
            )


class RegionTestCase(TestCase):
    def setUp(self) -> None:
        test_item = Region.objects.create(insee=11, name="Test region")
        year1 = DataYear.objects.create(year=2020)
        year2 = DataYear.objects.create(year=2021)
        test_item.years.add(year1, year2)
        test_item.save()

        dept01 = Departement.objects.create(name="Dept 1", insee="01", region=test_item)
        dept02 = Departement.objects.create(name="Dept 2", insee="02", region=test_item)
        dept03 = Departement.objects.create(name="Dept 3", insee="03")

        Commune.objects.create(name="Commune 11", insee="01001", departement=dept01)
        Commune.objects.create(name="Commune 12", insee="01002", departement=dept01)
        Commune.objects.create(name="Commune 21", insee="02001", departement=dept02)
        Commune.objects.create(name="Commune 31", insee="03001", departement=dept03)

    def test_region_is_created(self) -> None:
        test_item = Region.objects.get(insee=11)
        self.assertEqual(test_item.name, "Test region")

    def test_region_has_years(self) -> None:
        test_item = Region.objects.get(insee=11)
        self.assertQuerysetEqual(
            test_item.years.values_list("year", flat=True), [2020, 2021], ordered=False
        )

    def test_region_has_no_duplicate(self) -> None:
        with self.assertRaises(ValidationError):
            Region.objects.create(insee=11, name="Test region")

    def test_region_cant_be_created_without_name(self) -> None:
        with self.assertRaises(ValidationError):
            Region.objects.create(insee=11, name="")

        with self.assertRaises(ValidationError):
            Region.objects.create(insee=11)

    def test_region_cant_be_created_without_insee(self) -> None:
        with self.assertRaises(ValidationError):
            Region.objects.create(name="Test region")

    def test_region_cant_be_created_with_invalid_insee(self) -> None:
        with self.assertRaises(ValidationError):
            Region.objects.create(name="Test region", insee="1")

        with self.assertRaises(ValidationError):
            Region.objects.create(name="Test region", insee="1A")

    def test_region_has_departements(self) -> None:
        test_region = Region.objects.get(insee=11)

        self.assertEqual(test_region.subdivisions_count()["departements"], 2)

    def test_region_has_communes(self) -> None:
        test_region = Region.objects.get(insee=11)

        self.assertEqual(test_region.subdivisions_count()["communes"], 3)

    def test_region_cant_have_invalid_siren(self) -> None:
        with self.assertRaises(ValidationError):
            test_region = Region.objects.get(insee=11)
            test_region.siren = "42"
            test_region.save()


class DepartementTestCase(TestCase):
    def setUp(self) -> None:
        region = Region.objects.create(insee="11", name="Test region")
        year1 = DataYear.objects.create(year=2020)
        year2 = DataYear.objects.create(year=2021)
        region.years.add(year1, year2)
        region.save()

        test_departement = Departement.objects.create(
            name="Test département", insee="01", region=region
        )
        test_departement.years.add(year1, year2)
        test_departement.save()

        epci1 = Epci.objects.create(name="EPCI 1", siren="200068989")

        epci2 = Epci.objects.create(name="EPCI 2", siren="200068989")

        Commune.objects.create(
            name="Commune 11", insee="01001", departement=test_departement, epci=epci1
        )
        Commune.objects.create(
            name="Commune 12", insee="01002", departement=test_departement, epci=epci2
        )

    def test_departement_is_created(self) -> None:
        test_item = Departement.objects.get(insee="01")
        self.assertEqual(test_item.name, "Test département")

    def test_departement_has_years(self) -> None:
        test_item = Departement.objects.get(insee="01")
        self.assertQuerysetEqual(
            test_item.years.values_list("year", flat=True), [2020, 2021], ordered=False
        )

    def test_departement_cant_be_created_without_name(self) -> None:
        with self.assertRaises(ValidationError):
            Departement.objects.create(insee="02", name="")

        with self.assertRaises(ValidationError):
            Departement.objects.create(insee="03")

    def test_departement_cant_be_created_without_insee(self) -> None:
        with self.assertRaises(ValidationError):
            Departement.objects.create(name="Test departement")

    def test_departement_cant_be_created_with_invalid_insee(self) -> None:
        with self.assertRaises(ValidationError):
            Departement.objects.create(name="Test departement", insee="1")

        with self.assertRaises(ValidationError):
            Departement.objects.create(name="Test departement", insee="20")

        with self.assertRaises(ValidationError):
            Departement.objects.create(name="Test departement", insee="113")

    def test_departement_has_communes(self) -> None:
        test_item = Departement.objects.get(insee="01")

        self.assertEqual(test_item.commune_set.count(), 2)

    def test_departement_has_epcis(self) -> None:
        test_item = Departement.objects.get(insee="01")
        self.assertEqual(test_item.list_epcis().count(), 2)

    def test_departement_cant_have_invalid_siren(self) -> None:
        with self.assertRaises(ValidationError):
            test_item = Departement.objects.get(insee="01")
            test_item.siren = "42"
            test_item.save()


class EpciTestCase(TestCase):
    def setUp(self) -> None:
        year1 = DataYear.objects.create(year=2020)
        year2 = DataYear.objects.create(year=2021)

        test_epci = Epci.objects.create(name="Test EPCI", siren="200068989")
        test_epci.years.add(year1, year2)
        test_epci.save()

        dept1 = Departement.objects.create(name="dept 1", insee="01")
        dept2 = Departement.objects.create(name="dept 2", insee="01")

        Commune.objects.create(
            name="Commune 11", insee="01001", departement=dept1, epci=test_epci
        )
        Commune.objects.create(
            name="Commune 12", insee="01002", departement=dept1, epci=test_epci
        )
        Commune.objects.create(
            name="Commune 21", insee="02001", departement=dept2, epci=test_epci
        )

    def test_epci_is_created(self) -> None:
        test_item = Epci.objects.get(siren="200068989")
        self.assertEqual(test_item.name, "Test EPCI")

    def test_epci_cant_be_created_without_name(self) -> None:
        with self.assertRaises(ValidationError):
            Epci.objects.create(siren="200068989")

    def test_epci_cant_be_created_without_siren(self) -> None:
        with self.assertRaises(ValidationError):
            Epci.objects.create(name="Test EPCI")

    def test_epci_cant_be_created_with_invalid_siren(self) -> None:
        with self.assertRaises(ValidationError):
            Epci.objects.create(name="Test EPCI", siren="42")

    def test_epci_has_years(self) -> None:
        test_item = Epci.objects.get(siren="200068989")
        self.assertQuerysetEqual(
            test_item.years.values_list("year", flat=True), [2020, 2021], ordered=False
        )

    def test_epci_has_communes(self) -> None:
        test_item = Epci.objects.get(siren="200068989")

        self.assertEqual(test_item.commune_set.count(), 3)


class CommuneTestCase(TestCase):
    def setUp(self) -> None:
        year1 = DataYear.objects.create(year=2020)
        year2 = DataYear.objects.create(year=2021)

        epci = Epci.objects.create(name="Test EPCI", siren="200068989")

        dept = Departement.objects.create(name="dept 1", insee="01")

        test_item = Commune.objects.create(
            name="Test commune", insee="01001", departement=dept, epci=epci
        )
        test_item.years.add(year1, year2)
        test_item.save()

    def test_commune_is_created(self) -> None:
        test_item = Commune.objects.get(insee="01001")
        self.assertEqual(test_item.name, "Test commune")

    def test_commune_cant_be_created_without_name(self) -> None:
        dept = Departement.objects.get(insee="01")

        with self.assertRaises(ValidationError):
            Commune.objects.create(insee="01001", departement=dept)

    def test_commune_cant_be_created_without_insee(self) -> None:
        dept = Departement.objects.get(insee="01")

        with self.assertRaises(ValidationError):
            Commune.objects.create(name="Test commune", departement=dept)

        with self.assertRaises(ValidationError):
            Commune.objects.create(name="Test commune", insee="", departement=dept)

    def test_commune_cant_be_created_with_invalid_insee(self) -> None:
        dept = Departement.objects.get(insee="01")

        with self.assertRaises(ValidationError):
            Commune.objects.create(name="Test commune", insee="1001", departement=dept)

        with self.assertRaises(ValidationError):
            Commune.objects.create(name="Test commune", insee="2C001", departement=dept)

    def test_commune_cant_be_created_without_departement(self) -> None:
        with self.assertRaises(ValidationError):
            Commune.objects.create(insee="01001")

    def test_commune_cant_have_invalid_siren(self) -> None:
        with self.assertRaises(ValidationError):
            test_item = Commune.objects.get(insee="01001")
            test_item.siren = "42"
            test_item.save()


class RegionDataTestCase(TestCase):
    def setUp(self) -> None:
        region = Region.objects.create(insee="11", name="Test region")
        year = DataYear.objects.create(year=2020)
        source = DataSource.objects.create(
            title="Test title", url="http://test-url.com", year=year
        )

        RegionData.objects.create(
            region=region,
            year=year,
            datacode="property",
            value="Test data item",
            source=source,
        )

    def test_region_data_is_created(self) -> None:
        test_item = RegionData.objects.get(
            region__insee="11", year__year=2020, datacode="property"
        )
        self.assertEqual(test_item.value, "Test data item")

    def test_region_data_is_unique_per_year(self) -> None:
        region = Region.objects.get(insee="11", name="Test region")
        year = DataYear.objects.get(year=2020)
        source = DataSource.objects.get(
            title="Test title", url="http://test-url.com", year=year
        )

        with self.assertRaises(IntegrityError):
            RegionData.objects.create(
                region=region,
                year=year,
                datacode="property",
                value="Test data duplicate",
                source=source,
            )


class DepartementDataTestCase(TestCase):
    def setUp(self) -> None:
        dept = Departement.objects.create(insee="11", name="Test departement")
        year = DataYear.objects.create(year=2020)
        source = DataSource.objects.create(
            title="Test title", url="http://test-url.com", year=year
        )

        DepartementData.objects.create(
            departement=dept,
            year=year,
            datacode="property",
            value="Test data item",
            source=source,
        )

    def test_departement_data_is_created(self) -> None:
        test_item = DepartementData.objects.get(
            departement__insee="11", year__year=2020, datacode="property"
        )
        self.assertEqual(test_item.value, "Test data item")

    def test_departement_data_is_unique_per_year(self) -> None:
        dept = Departement.objects.get(insee="11")
        year = DataYear.objects.get(year=2020)
        source = DataSource.objects.get(
            title="Test title", url="http://test-url.com", year=year
        )

        with self.assertRaises(IntegrityError):
            DepartementData.objects.create(
                departement=dept,
                year=year,
                datacode="property",
                value="Test data duplicate",
                source=source,
            )


class EpciDataTestCase(TestCase):
    def setUp(self) -> None:
        epci = Epci.objects.create(name="Test EPCI", siren="200068989")
        year = DataYear.objects.create(year=2020)
        source = DataSource.objects.create(
            title="Test title", url="http://test-url.com", year=year
        )

        EpciData.objects.create(
            epci=epci,
            year=year,
            datacode="property",
            value="Test data item",
            source=source,
        )

    def test_epci_data_is_created(self) -> None:
        test_item = EpciData.objects.get(
            epci__siren="200068989", year__year=2020, datacode="property"
        )
        self.assertEqual(test_item.value, "Test data item")

    def test_epci_data_is_unique_per_year(self) -> None:
        epci = Epci.objects.get(siren="200068989")
        year = DataYear.objects.get(year=2020)
        source = DataSource.objects.get(
            title="Test title", url="http://test-url.com", year=year
        )

        with self.assertRaises(IntegrityError):
            EpciData.objects.create(
                epci=epci,
                year=year,
                datacode="property",
                value="Test data duplicate",
                source=source,
            )


class DepartementDataTestCase(TestCase):
    def setUp(self) -> None:
        dept = Departement.objects.create(insee="11", name="Test departement")
        year = DataYear.objects.create(year=2020)
        source = DataSource.objects.create(
            title="Test title", url="http://test-url.com", year=year
        )
        commune = Commune.objects.create(
            name="Commune 11", insee="01001", departement=dept
        )

        CommuneData.objects.create(
            commune=commune,
            year=year,
            datacode="property",
            value="Test data item",
            source=source,
        )

    def test_commune_data_is_created(self) -> None:
        test_item = CommuneData.objects.get(
            commune__insee="01001", year__year=2020, datacode="property"
        )
        self.assertEqual(test_item.value, "Test data item")

    def test_commune_data_is_unique_per_year(self) -> None:
        commune = Commune.objects.get(insee="01001")
        year = DataYear.objects.get(year=2020)
        source = DataSource.objects.get(
            title="Test title", url="http://test-url.com", year=year
        )

        with self.assertRaises(IntegrityError):
            CommuneData.objects.create(
                commune=commune,
                year=year,
                datacode="property",
                value="Test data duplicate",
                source=source,
            )
