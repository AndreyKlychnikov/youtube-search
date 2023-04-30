import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exchangers.models import City, Country, Currency


async def init_currencies(db: AsyncSession) -> None:
    currency = await db.scalars(select(Currency).limit(1))
    if currency.first():
        return
    with open("currencies.json") as f:
        currencies = json.load(f)
    db.add_all(
        (
            Currency(code=currency["code"], name=currency["name"])
            for currency in currencies
        )
    )
    await db.commit()


async def init_countries(db: AsyncSession) -> None:
    country = await db.scalars(select(Country).limit(1))
    if country.first():
        return
    with open("countries.json") as f:
        countries = json.load(f)
    db.add_all(
        (
            Country(name=country["name"], code=country["alpha-3"])
            for country in countries
        )
    )
    await db.commit()


async def init_cities(db: AsyncSession) -> None:
    city = await db.scalars(select(City).limit(1))
    if city.first():
        return
    with open("cities.json") as f:
        cities = json.load(f)
    db.add_all(
        (
            City(
                name=city["name"],
                country_id=city["country_id"],
                name_en=city["name_en"],
            )
            for city in cities
        )
    )
    await db.commit()


async def init_db(db: AsyncSession) -> None:
    await init_currencies(db)
    await init_countries(db)
    await init_cities(db)
