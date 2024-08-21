from pydantic import BaseModel
from typing import Union


class OCRResult(BaseModel):
    filename: str
    pnr: Union[str, None]
    ser: Union[str, None]
    dmf: Union[str, None]
    image_data: Union[str, None] = None
    yellow_caps: Union[int, None] = None
    screws: Union[int, None] = None
    label_present: Union[bool, None] = None