from babel import Locale
from babel.core import UnknownLocaleError
from aiogram.types import User
from datetime import datetime

from .schemas import CalendarLabels


async def get_user_locale(from_user: User) -> str:
    """Returns user locale in format en_US, accepts User instance from Message, CallbackData etc"""
    loc = from_user.language_code or "en"
    try:
        Locale.parse(loc)
        return loc
    except UnknownLocaleError:
        # Fallback to a constructed locale or "en_US" for invalid codes
        return f"{loc}_{loc.upper()}" if len(loc) == 2 else "en_US"


class GenericCalendar:
    def __init__(
        self,
        locale: str = None,
        cancel_btn: str = None,
        today_btn: str = None,
        show_alerts: bool = False
    ) -> None:
        """Pass labels if you need to have alternative language of buttons

        Parameters:
        locale (str): Locale calendar must have captions in (e.g., 'en', 'uk_UA'), if None - default English will be used
        cancel_btn (str): label for button Cancel to cancel date input
        today_btn (str): label for button Today to set calendar back to today's date
        show_alerts (bool): defines how the date range error would be shown (defaults to False)
        """
        self._labels = CalendarLabels()
        default_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        default_months = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]

        if locale:
            try:
                babel_locale = Locale.parse(locale, sep="_")
                # Get day names with fallback (0-based indexing: 0 = Mon, 6 = Sun)
                days = babel_locale.days["format"]["abbreviated"]
                self._labels.days_of_week = [
                    days.get(i, default_days[i]) for i in range(0, 7)
                ]
                # Get full month names (1-based indexing: 1 = Jan, 12 = Dec)
                months = babel_locale.months["stand-alone"]["abbreviated"]
                self._labels.months = [
                    months.get(i, default_months[i-1]) for i in range(1, 13)
                ]
            except UnknownLocaleError:
                # Fallback to English if locale is unrecognized
                self._labels.days_of_week = default_days
                self._labels.months = default_months
        else:
            # Default to English if no locale provided
            self._labels.days_of_week = default_days
            self._labels.months = default_months

        if cancel_btn:
            self._labels.cancel_caption = cancel_btn
        if today_btn:
            self._labels.today_caption = today_btn

        self.min_date = None
        self.max_date = None
        self.show_alerts = show_alerts

    def set_dates_range(self, min_date: datetime, max_date: datetime):
        """Sets range of minimum & maximum dates"""
        self.min_date = min_date
        self.max_date = max_date

    async def process_day_select(self, data, query):
        """Checks selected date is in allowed range of dates"""
        date = datetime(int(data.year), int(data.month), int(data.day))
        if self.min_date and self.min_date > date:
            await query.answer(
                f'The date has to be later than {self.min_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        elif self.max_date and self.max_date < date:
            await query.answer(
                f'The date has to be earlier than {self.max_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        await query.message.delete_reply_markup()
        return True, date


# To run test: make `from .schemas import CalendarLabels` use absolute path: `from schemas ...` 
# class MockUser:
#     def __init__(self, language_code):
#         self.language_code = language_code


# async def test_locale():
#     for code in ["en", "uk", "ru", "fr", "zh", "xx"]:  # "xx" is invalid
#         user = MockUser(code)
#         loc = await get_user_locale(user)
#         cal = GenericCalendar(locale=loc)
#         print(f"Locale: {loc}")
#         print(f"Days: {cal._labels.days_of_week}")
#         print(f"Months: {cal._labels.months}")
#         print("---")


# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(test_locale())
