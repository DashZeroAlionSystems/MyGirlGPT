from pydantic import BaseModel
from typing import Union


class generate_web(BaseModel):
    text: Union[str, None] = None
    voice_preset: Union[str, None] = None
    text_temp: Union[float, None] = None
    waveform_temp: Union[float, None] = None

    class Config:
        orm_mode = True
