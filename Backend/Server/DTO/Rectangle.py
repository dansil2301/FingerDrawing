from dataclasses import dataclass

from Server.DTO.Point import Point


@dataclass
class Rectangle:
    # Saves two corners. Enough to create a rectangle
    ru_corner: Point
    ld_corner: Point
