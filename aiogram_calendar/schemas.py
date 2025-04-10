from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field

from aiogram.filters.callback_data import CallbackData

class CalendarActions(str, Enum):
    ignore = 'IGNORE'
    set_y = 'SET-YEAR'
    set_m = 'SET-MONTH'
    prev_y = 'PREV-YEAR'
    next_y = 'NEXT-YEAR'
    cancel = 'CANCEL'
    start = 'START'
    day = 'SET-DAY'
    prev_m = 'PREV-MONTH'
    next_m = 'NEXT-MONTH'


class CalendarCallback(CallbackData, prefix="calendar"):
    act: CalendarActions
    act: str
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None


class CalendarLabels(BaseModel):
    "Schema to pass labels for calendar. Can be used to put in different languages"
    days_of_week: List[str] = Field(default=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], 
                                   min_items=7, max_items=7)
    months: List[str] = Field(default=[
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ], min_items=12, max_items=12)
    cancel_caption: str = Field(default='Cancel', description='Caprion for Cancel button')
    today_caption: str = Field(default='Today', description='Caprion for Cancel button')


HIGHLIGHT_FORMAT = "[{}]"


def highlight(text):
    return HIGHLIGHT_FORMAT.format(text)
