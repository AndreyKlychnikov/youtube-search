from typing import Optional

from pydantic import BaseModel


# Shared properties
class ExampleBase(BaseModel):
    title: Optional[str] = None


# Properties to receive on item creation
class ExampleCreate(ExampleBase):
    title: str


# Properties to receive on item update
class ExampleUpdate(ExampleBase):
    pass


# Properties shared by models stored in DB
class ExampleInDBBase(ExampleBase):
    id: int
    title: str

    class Config:
        orm_mode = True


# Properties to return to client
class Example(ExampleInDBBase):
    pass


# Properties stored in DB
class ExampleInDB(ExampleInDBBase):
    pass
