from pydantic import BaseModel

from Server.DTO.Point import Point


class Rectangle(BaseModel):
    # Saves two corners. Enough to create a rectangle
    ru_corner: Point
    ld_corner: Point
