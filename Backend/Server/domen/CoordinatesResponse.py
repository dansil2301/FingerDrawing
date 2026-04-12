from typing import Optional, Union

from pydantic import BaseModel

from Server.Enums.Action import Action
from Server.DTO.Point import Point
from Server.DTO.Rectangle import Rectangle


class CoordinatesResponse(BaseModel):
    action: Optional[str] = None
    coordinates: Optional[Union[Rectangle, Point]] = None
