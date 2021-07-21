from ninja import Schema
from typing import List


class DataYearSchema(Schema):
    year: int


class RegionSchema(Schema):
    id: int
    name: str = None
    insee: str = None
    siren: str = None
    years: List[DataYearSchema]


class DepartementSchema(Schema):
    id: int
    name: str = None
    insee: str = None
    siren: str = None
    region: RegionSchema = None
    years: List[DataYearSchema] = None


class EpciSchema(Schema):
    id: int
    name: str = None
    siren: str = None
    years: List[DataYearSchema] = None


class CommuneSchema(Schema):
    id: int
    name: str = None
    insee: str = None
    siren: str = None
    epci: EpciSchema = None
    departement: DepartementSchema = None
    population: int = None
    years: List[DataYearSchema] = None
