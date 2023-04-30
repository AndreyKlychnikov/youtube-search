from fastapi import APIRouter

from app.schemas.example import ExampleInDBBase

router = APIRouter()


@router.get("/example")
def read_example() -> ExampleInDBBase:
    return ExampleInDBBase(
        id=1,
        title="example"
    )

