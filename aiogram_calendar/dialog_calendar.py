import calendar
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from .schemas import DialogCalendarCallback, DialogCalAct, highlight, superscript
from .common import GenericCalendar


class DialogCalendar(GenericCalendar):

    ignore_callback = DialogCalendarCallback(act=DialogCalAct.ignore).pack()  # placeholder for no answer buttons

    async def _get_month_kb(self, year: int):
        """Creates an inline keyboard with months for specified year"""
        today = datetime.now()
        now_month, now_year = today.month, today.year
        min_year, max_year = now_year, now_year + 1  # Restrict to current and next year

        kb = []
        # First row with year navigation
        nav_row = []
        if year > min_year:
            nav_row.append(InlineKeyboardButton(
                text="<<",
                callback_data=DialogCalendarCallback(act=DialogCalAct.prev_y, year=year, month=-1, day=-1).pack()
            ))
        else:
            nav_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        
        nav_row.append(InlineKeyboardButton(
            text=str(year) if year != now_year else highlight(year),
            callback_data=DialogCalendarCallback(act=DialogCalAct.start, year=year, month=-1, day=-1).pack()
        ))
        
        if year < max_year:
            nav_row.append(InlineKeyboardButton(
                text=">>",
                callback_data=DialogCalendarCallback(act=DialogCalAct.next_y, year=year, month=-1, day=-1).pack()
            ))
        else:
            nav_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        
        kb.append(nav_row)

        # Two rows with 6 months buttons
        month6_row = []
        def highlight_month(month):
            month_str = self._labels.months[month - 1]
            if now_month == month and now_year == year:
                return highlight(month_str)
            return month_str

        for month in range(1, 7):
            month6_row.append(InlineKeyboardButton(
                text=highlight_month(month),
                callback_data=DialogCalendarCallback(
                    act=DialogCalAct.set_m, year=year, month=month, day=-1
                ).pack()
            ))
        kb.append(month6_row)

        month12_row = []
        for month in range(7, 13):
            month12_row.append(InlineKeyboardButton(
                text=highlight_month(month),
                callback_data=DialogCalendarCallback(
                    act=DialogCalAct.set_m, year=year, month=month, day=-1
                ).pack()
            ))
        kb.append(month12_row)

        # Last row with cancel button only
        cancel_row = [
            InlineKeyboardButton(
                text=self._labels.cancel_caption,
                callback_data=DialogCalendarCallback(act=DialogCalAct.cancel, year=year, month=1, day=1).pack()
            )
        ]
        kb.append(cancel_row)

        return InlineKeyboardMarkup(row_width=6, inline_keyboard=kb)

    async def _get_days_kb(self, year: int, month: int):
        """Creates an inline keyboard with calendar days of month for specified year and month"""
        today = datetime.now()
        now_weekday = self._labels.days_of_week[today.weekday()]
        now_month, now_year, now_day = today.month, today.year, today.day
        min_year, max_year = now_year, now_year + 1  # Restrict to current and next year

        def highlight_month():
            month_str = self._labels.months[month - 1]
            if now_month == month and now_year == year:
                return highlight(month_str)
            return month_str

        def highlight_weekday():
            if now_month == month and now_year == year and now_weekday == weekday:
                return highlight(weekday)
            return weekday

        def format_day_string():
            date_to_check = datetime(year, month, day)
            if self.min_date and date_to_check < self.min_date:
                return superscript(str(day))
            elif self.max_date and date_to_check > self.max_date:
                return superscript(str(day))
            return str(day)

        def highlight_day():
            day_string = format_day_string()
            if now_month == month and now_year == year and now_day == day:
                return highlight(day_string)
            return day_string

        kb = []
        # First row - Year navigation
        year_row = []
        if year > min_year:
            year_row.append(InlineKeyboardButton(
                text="<<",
                callback_data=DialogCalendarCallback(act=DialogCalAct.prev_y, year=year, month=month, day=1).pack()
            ))
        else:
            year_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        
        year_row.append(InlineKeyboardButton(
            text=str(year) if year != now_year else highlight(year),
            callback_data=DialogCalendarCallback(act=DialogCalAct.start, year=year, month=-1, day=-1).pack()
        ))
        
        if year < max_year:
            year_row.append(InlineKeyboardButton(
                text=">>",
                callback_data=DialogCalendarCallback(act=DialogCalAct.next_y, year=year, month=month, day=1).pack()
            ))
        else:
            year_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        
        kb.append(year_row)

        # Second row - Month navigation
        month_row = []
        month_row.append(InlineKeyboardButton(
            text="<",
            callback_data=DialogCalendarCallback(act=DialogCalAct.prev_m, year=year, month=month, day=1).pack()
        ))
        month_row.append(InlineKeyboardButton(
            text=highlight_month(),
            callback_data=DialogCalendarCallback(act=DialogCalAct.set_y, year=year, month=-1, day=-1).pack()
        ))
        month_row.append(InlineKeyboardButton(
            text=">",
            callback_data=DialogCalendarCallback(act=DialogCalAct.next_m, year=year, month=month, day=1).pack()
        ))
        kb.append(month_row)

        # Third row - Weekday labels
        week_days_labels_row = []
        for weekday in self._labels.days_of_week:
            week_days_labels_row.append(InlineKeyboardButton(
                text=highlight_weekday(), callback_data=self.ignore_callback))
        kb.append(week_days_labels_row)

        # Calendar days
        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            days_row = []
            for day in week:
                if day == 0:
                    days_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
                    continue
                days_row.append(InlineKeyboardButton(
                    text=highlight_day(),
                    callback_data=DialogCalendarCallback(act=DialogCalAct.day, year=year, month=month, day=day).pack()
                ))
            kb.append(days_row)

        # Last row with cancel button only
        cancel_row = [
            InlineKeyboardButton(
                text=self._labels.cancel_caption,
                callback_data=DialogCalendarCallback(act=DialogCalAct.cancel, year=year, month=month, day=1).pack()
            )
        ]
        kb.append(cancel_row)

        return InlineKeyboardMarkup(row_width=7, inline_keyboard=kb)

    async def start_calendar(
        self,
        year: int = datetime.now().year,
        month: int = None
    ) -> InlineKeyboardMarkup:
        today = datetime.now()
        now_year = today.year

        if month:
            return await self._get_days_kb(year, month)

        kb = []
        # Year selection (current year and next year only)
        years_row = []
        for value in range(now_year, now_year + 2):  # Only current year and next year
            years_row.append(InlineKeyboardButton(
                text=str(value) if value != now_year else highlight(value),
                callback_data=DialogCalendarCallback(act=DialogCalAct.set_y, year=value, month=-1, day=-1).pack()
            ))
        kb.append(years_row)

        # Last row with cancel button only
        cancel_row = [
            InlineKeyboardButton(
                text=self._labels.cancel_caption,
                callback_data=DialogCalendarCallback(act=DialogCalAct.cancel, year=year, month=1, day=1).pack()
            )
        ]
        kb.append(cancel_row)

        return InlineKeyboardMarkup(row_width=2, inline_keyboard=kb)

    async def process_selection(self, query: CallbackQuery, data: DialogCalendarCallback) -> tuple:
        return_data = (False, None)
        today = datetime.now()
        min_year, max_year = today.year, today.year + 1  # Restrict to current and next year

        if data.act == DialogCalAct.ignore:
            await query.answer(cache_time=60)
        elif data.act == DialogCalAct.set_y:
            await query.message.edit_reply_markup(reply_markup=await self._get_month_kb(int(data.year)))
        elif data.act == DialogCalAct.start:
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(int(data.year)))
        elif data.act == DialogCalAct.set_m:
            await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(int(data.year), int(data.month)))
        elif data.act == DialogCalAct.day:
            return await self.process_day_select(data, query)
        elif data.act == DialogCalAct.cancel:
            await query.message.delete_reply_markup()
        elif data.act == DialogCalAct.prev_y:
            if data.month == -1:
                # From month keyboard: change year and show months
                new_year = max(int(data.year) - 1, min_year)
                await query.message.edit_reply_markup(reply_markup=await self._get_month_kb(new_year))
            else:
                # From days keyboard: change year, keep month, show days
                new_year = max(int(data.year) - 1, min_year)
                await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(new_year, int(data.month)))
        elif data.act == DialogCalAct.next_y:
            if data.month == -1:
                # From month keyboard: change year and show months
                new_year = min(int(data.year) + 1, max_year)
                await query.message.edit_reply_markup(reply_markup=await self._get_month_kb(new_year))
            else:
                # From days keyboard: change year, keep month, show days
                new_year = min(int(data.year) + 1, max_year)
                await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(new_year, int(data.month)))
        elif data.act == DialogCalAct.prev_m:
            temp_date = datetime(int(data.year), int(data.month), 1) - timedelta(days=1)
            new_year = temp_date.year
            new_month = temp_date.month
            if new_year < min_year:
                new_year = min_year
                new_month = 1  # Stay at January of min_year
            await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(new_year, new_month))
        elif data.act == DialogCalAct.next_m:
            temp_date = datetime(int(data.year), int(data.month), 1) + timedelta(days=31)
            new_year = temp_date.year
            new_month = temp_date.month
            if new_year > max_year:
                new_year = max_year
                new_month = 12  # Stay at December of max_year
            await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(new_year, new_month))
        return return_data
