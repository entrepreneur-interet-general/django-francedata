from ninja import Router, Schema
from unidecode import unidecode
from typing import List
from django.shortcuts import get_object_or_404

from django.db.models import Max

from francedata.models import (
    Metadata,
    Region,
    Departement,
    Epci,
    Commune,
    DataYear,
)

from francedata.schemas import (
    DataYearSchema,
    RegionSchema,
    DepartementSchema,
    EpciSchema,
    CommuneSchema,
)

router = Router()


@router.get("/subdivisions/{query}", tags=["subdivisions"])
def search_subdivisions(request, query: str, category: str = None, year: int = None):
    """
    Search within all categories

    Allowed values for category parameter : all, communes, epcis, departements, regions
    """
    query = unidecode(query).lower()

    # Check type optional parameter:
    if category in ["communes", "epcis", "departements", "regions"]:
        return_all_categories = False
    else:
        # If any other value is specified, we'll treat it the same as "all"
        return_all_categories = True

    # Initiate the lists
    communes_raw = []
    epcis_raw = []
    departements_raw = []
    regions_raw = []
    response = []

    # year filter
    if not year:
        if category == "regions" or return_all_categories:
            regions_year_entry = DataYear.objects.get(
                year=Metadata.objects.filter(prop="cog_regions_year").aggregate(
                    Max("value")
                )["value__max"]
            )

        if category == "departements" or return_all_categories:
            departements_year_entry = DataYear.objects.get(
                year=Metadata.objects.filter(prop="cog_depts_year").aggregate(
                    Max("value")
                )["value__max"]
            )

        if category == "epcis" or return_all_categories:
            epcis_year_entry = DataYear.objects.get(
                year=Metadata.objects.filter(prop="banatic_epci_year").aggregate(
                    Max("value")
                )["value__max"]
            )

        if category == "communes" or return_all_categories:
            communes_year_entry = DataYear.objects.get(
                year=Metadata.objects.filter(prop="cog_communes_year").aggregate(
                    Max("value")
                )["value__max"]
            )
    else:
        regions_year_entry = DataYear.objects.get(year=year)
        departements_year_entry = regions_year_entry
        epcis_year_entry = regions_year_entry
        communes_year_entry = regions_year_entry

    if len(query) < 3 and (category == "communes" or return_all_categories):
        shortnamed_communes = [
            "by",
            "bu",
            "eu",
            "gy",
            "oz",
            "oo",
            "py",
            "ri",
            "ry",
            "sy",
            "ur",
            "us",
            "uz",
            "y",
        ]
        if query in shortnamed_communes:
            communes_raw = Commune.objects.filter(
                name__unaccent__iexact=query, years__exact=communes_year_entry
            )
    else:
        if category == "regions" or return_all_categories:
            regions_raw = Region.objects.filter(
                name__unaccent__istartswith=query, years__exact=regions_year_entry
            ).exclude(
                siren__exact=""
            )  # Exclude Mayotte that has no region-level Siren
        if category == "departements" or return_all_categories:
            departements_raw = Departement.objects.filter(
                name__unaccent__istartswith=query, years__exact=departements_year_entry
            ).exclude(
                siren__exact=""
            )  # Exclude Haute-Corse, Corse-du-Sud, Martinique and Guyane that have no departement-level Siren
        if category == "epcis" or return_all_categories:
            epcis_raw = Epci.objects.filter(
                name__unaccent__icontains=query, years__exact=epcis_year_entry
            )
        if category == "communes" or return_all_categories:
            communes_raw = Commune.objects.filter(
                name__unaccent__istartswith=query, years__exact=communes_year_entry
            )

    if len(regions_raw):
        regions = []
        for r in regions_raw:
            regions.append(
                {"value": r.siren, "text": r.name, "type": "region", "slug": r.slug}
            )

        response.append({"groupName": f"Régions ({len(regions)})", "items": regions})

    if len(departements_raw):
        departements = []
        for d in departements_raw:
            departements.append(
                {
                    "value": d.siren,
                    "text": d.name,
                    "type": "departement",
                    "slug": d.slug,
                }
            )

        response.append(
            {"groupName": f"Départements ({len(departements)})", "items": departements}
        )

    if len(epcis_raw):
        epcis = []
        for e in epcis_raw:
            epcis.append(
                {"value": e.siren, "text": e.name, "type": "epci", "slug": e.slug}
            )

        response.append(
            {"groupName": f"Intercommunalités ({len(epcis)})", "items": epcis}
        )

    if len(communes_raw):
        communes = []
        for c in communes_raw:
            communes.append(
                {
                    "value": c.siren,
                    "text": f"{c.name} ({c.insee})",
                    "name": c.name,
                    "insee": c.insee,
                    "type": "commune",
                    "slug": c.slug,
                }
            )

        response.append({"groupName": f"Communes ({len(communes)})", "items": communes})

    return response


@router.get("/regions", response=List[RegionSchema], tags=["subdivisions"])
def list_regions(request):
    queryset = Region.objects.all()
    return queryset


@router.get("/regions/{siren_id}", response=RegionSchema, tags=["subdivisions"])
def get_region(request, siren_id):
    item = get_object_or_404(Region, siren=siren_id)
    return item


@router.get("/departements", response=List[DepartementSchema], tags=["subdivisions"])
def list_departements(request):
    queryset = Departement.objects.all()
    return queryset


@router.get(
    "/departements/{siren_id}", response=DepartementSchema, tags=["subdivisions"]
)
def get_departement(request, siren_id):
    item = get_object_or_404(Departement, siren=siren_id)
    return item


@router.get("/epcis", response=List[EpciSchema], tags=["subdivisions"])
def list_epcis(request):
    queryset = Epci.objects.all()
    return queryset


@router.get("/epcis/{siren_id}", response=EpciSchema, tags=["subdivisions"])
def get_epci(request, siren_id):
    item = get_object_or_404(Epci, siren=siren_id)
    return item


@router.get("/communes", response=List[CommuneSchema], tags=["subdivisions"])
def list_communes(request):
    queryset = Epci.objects.all()
    return queryset


@router.get(
    "/communes/{commune_id}",
    response={200: CommuneSchema, 404: dict},
    tags=["subdivisions"],
)
def get_commune(request, commune_id):
    """
    Depending if commune_id is 5 or 9 characters long, retrieves the commune by Insee or Siren id.
    """
    if len(commune_id) == 9:
        item = get_object_or_404(Commune, siren=commune_id)
    elif len(commune_id) == 5:
        item = get_object_or_404(Commune, insee=commune_id)
    else:
        return 404, {"message": "value is not a siren or insee id"}
    return 200, item


@router.get("/communes/siren/{siren_id}", response=CommuneSchema, tags=["subdivisions"])
def get_commune_by_siren(request, siren_id):
    item = get_object_or_404(Commune, siren=siren_id)
    return item


@router.get("/communes/insee/{insee_id}", response=CommuneSchema, tags=["subdivisions"])
def get_commune_by_insee(request, insee_id):
    item = get_object_or_404(Commune, insee=insee_id)
    return item
