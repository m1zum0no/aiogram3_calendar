import calendar
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from .schemas import CalendarCallback, CalendarActions, highlight
from .common import GenericCalendar


class Calendar(GenericCalendar):

    ignore_callback = CalendarCallback(act=CalendarActions.ignore).pack()  # placeholder for no answer buttons

    async def _get_month_kb(self, year: int):
        """Creates an inline keyboard with months for specified year"""
        today = datetime(2025, 4, 7) # datetime.now()
        now_month, now_year = today.month, today.year
        min_year, max_year = now_year, now_year + 1  # Restrict to current and next year
        min_month = now_month if year == min_year else 1  # Minimum month is current month in min_year

        kb = []
        # First row with year navigation
        nav_row = []
        if year > min_year:
            nav_row.append(InlineKeyboardButton(
                text="<<",
                callback_data=CalendarCallback(act=CalendarActions.prev_y, year=year, month=-1, day=-1).pack()
            ))
        else:
            nav_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        
        nav_row.append(InlineKeyboardButton(
            text=str(year) if year != now_year else highlight(year),
            callback_data=CalendarCallback(act=CalendarActions.start, year=year, month=-1, day=-1).pack()
        ))
        
        if year < max_year:
            nav_row.append(InlineKeyboardButton(
                text=">>",
                callback_data=CalendarCallback(act=CalendarActions.next_y, year=year, month=-1, day=-1).pack()
            ))
        else:
            nav_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        
        kb.append(nav_row)

        # Two rows with 6 months buttons
        month6_row = []
        def highlight_month(month):
            month_str = self._labels.months[month - 1]
            # Strikethrough months before min_month in min_year
            if year == min_year and month < min_month:
                return ''.join(c + '\u0336' for c in month_str)
            elif now_month == month and now_year == year:
                return highlight(month_str)
            return month_str

        for month in range(1, 7):
            if year == min_year and month < min_month:
                month6_row.append(InlineKeyboardButton(
                    text=highlight_month(month),
                    callback_data=self.ignore_callback
                ))
            else:
                month6_row.append(InlineKeyboardButton(
                    text=highlight_month(month),
                    callback_data=CalendarCallback(
                        act=CalendarActions.set_m, year=year, month=month, day=-1
                    ).pack()
                ))
        kb.append(month6_row)

        month12_row = []
        for month in range(7, 13):
            if year == min_year and month < min_month:
                month12_row.append(InlineKeyboardButton(
                    text=highlight_month(month),
                    callback_data=self.ignore_callback
                ))
            else:
                month12_row.append(InlineKeyboardButton(
                    text=highlight_month(month),
                    callback_data=CalendarCallback(
                        act=CalendarActions.set_m, year=year, month=month, day=-1
                    ).pack()
                ))
        kb.append(month12_row)

        # Last row with cancel button only
        cancel_row = [
            InlineKeyboardButton(
                text=self._labels.cancel_caption,
                callback_data=CalendarCallback(act=CalendarActions.cancel, year=year, month=1, day=1).pack()
            )
        ]
        kb.append(cancel_row)

        return InlineKeyboardMarkup(row_width=6, inline_keyboard=kb)

    async def _get_days_kb(self, year: int, month: int):
        """Creates an inline keyboard with calendar days of month for specified year and month"""
        today = datetime(2025, 4, 7)
        now_weekday = self._labels.days_of_week[today.weekday()]
        now_month, now_year, now_day = today.month, today.year, today.day
        min_year, max_year = now_year, now_year + 1  # Restrict to current and next year
        min_month = now_month if year == min_year else 1  # Minimum month in min_year
        max_month = 12  # Maximum month in max_year

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
            # For edge case (last week with empty Sunday), don't pad days in last row
            if is_edge_case and week_idx == len(month_calendar) - 1:
                print("EDGE CASE FROM DAY STRING")
                return f"{day}"  # No padding in edge case row
            return f" {day:2} "  # Normal padding for other row

        def highlight_day():
            day_string = format_day_string()
            # Strikethrough days before today in the current month and year
            if year == now_year and month == now_month and day < now_day:
                return ''.join(c + '\u0335' for c in day_string)  # Short stroke overlay
            elif now_month == month and now_year == year and now_day == day:
                return highlight(day_string.strip() if len(day_string.strip()) == 2 else day_string)
            return day_string

        kb = []
        # First row - Year navigation
        year_row = []
        if year > min_year:
            year_row.append(InlineKeyboardButton(
                text="<<",
                callback_data=CalendarCallback(act=CalendarActions.prev_y, year=year, month=month, day=1).pack()
            ))
        else:
            year_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        
        year_row.append(InlineKeyboardButton(
            text=str(year) if year != now_year else highlight(year),
            callback_data=CalendarCallback(act=CalendarActions.start, year=year, month=-1, day=-1).pack()
        ))
        
        if year < max_year:
            year_row.append(InlineKeyboardButton(
                text=">>",
                callback_data=CalendarCallback(act=CalendarActions.next_y, year=year, month=month, day=1).pack()
            ))
        else:
            year_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        
        kb.append(year_row)

        # Second row - Month navigation
        month_row = []
        # Show "<" only if not at min boundary (min_month of min_year)
        if not (year == min_year and month <= min_month):
            month_row.append(InlineKeyboardButton(
                text="<",
                callback_data=CalendarCallback(act=CalendarActions.prev_m, year=year, month=month, day=1).pack()
            ))
        else:
            month_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        
        month_row.append(InlineKeyboardButton(
            text=highlight_month(),
            callback_data=CalendarCallback(act=CalendarActions.set_y, year=year, month=-1, day=-1).pack()
        ))
        
        # Show ">" only if not at max boundary (max_month of max_year)
        if not (year == max_year and month >= max_month):
            month_row.append(InlineKeyboardButton(
                text=">",
                callback_data=CalendarCallback(act=CalendarActions.next_m, year=year, month=month, day=1).pack()
            ))
        else:
            month_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        
        kb.append(month_row)

        # Third row - Weekday labels
        week_days_labels_row = []
        for weekday in self._labels.days_of_week:
            week_days_labels_row.append(InlineKeyboardButton(
                text=highlight_weekday(), callback_data=self.ignore_callback))
        kb.append(week_days_labels_row)

        # Calendar days
        month_calendar = calendar.monthcalendar(year, month)
        for week_idx, week in enumerate(month_calendar):
            days_row = []
            
            # Check if this is the last week with only first cell empty (month ends on Sunday)
            is_edge_case = (week_idx == len(month_calendar) - 1 and  # Last week
                week[6] == 0 and  # Sunday is empty
                all(d > 0 for d in week[:6]))  # Monday-Saturday are non-empty
            if is_edge_case:
                print(f"EDGE CASE DETECTED: {week}")  # Debugging
            
            for day_idx, day in enumerate(week):
                if day == 0:
                    if is_edge_case and day_idx == 6:
                        # Use a special invisible character that maintains width
                        display_text = " ⠀ "  # U+202F (narrow no-break space)
                    else:
                        display_text = "    "  # Normal empty cell
                    callback = self.ignore_callback
                else:
                    display_text = highlight_day()
                    if year == now_year and month == now_month and day < now_day:
                        callback = self.ignore_callback
                    else:
                        callback = CalendarCallback(
                            act=CalendarActions.day, 
                            year=year, 
                            month=month, 
                            day=day
                        ).pack()
                
                days_row.append(InlineKeyboardButton(
                    text=display_text,
                    callback_data=callback
                ))
            kb.append(days_row)

        # Last row with cancel button only
        cancel_row = [
            InlineKeyboardButton(
                text=self._labels.cancel_caption,
                callback_data=CalendarCallback(act=CalendarActions.cancel, year=year, month=month, day=1).pack()
            )
        ]
        kb.append(cancel_row)

        return InlineKeyboardMarkup(row_width=7, inline_keyboard=kb, resize_keyboard=True)

    async def start_calendar(
        self,
        year: int = datetime(2025, 4, 7).year,
        month: int = None
    ) -> InlineKeyboardMarkup:
        today = datetime(2025, 4, 7)
        now_year = today.year

        if month:
            return await self._get_days_kb(year, month)

        kb = []
        # Year selection (current year and next year only)
        years_row = []
        for value in range(now_year, now_year + 2):  # Only current year and next year
            years_row.append(InlineKeyboardButton(
                text=str(value) if value != now_year else highlight(value),
                callback_data=CalendarCallback(act=CalendarActions.set_y, year=value, month=-1, day=-1).pack()
            ))
        kb.append(years_row)

        # Last row with cancel button only
        cancel_row = [
            InlineKeyboardButton(
                text=self._labels.cancel_caption,
                callback_data=CalendarCallback(act=CalendarActions.cancel, year=year, month=1, day=1).pack()
            )
        ]
        kb.append(cancel_row)

        return InlineKeyboardMarkup(row_width=2, inline_keyboard=kb)

    async def process_selection(self, query: CallbackQuery, data: CalendarCallback) -> tuple:
        return_data = (False, None)
        today = datetime(2025, 4, 7)
        min_year, max_year = today.year, today.year + 1  # Restrict to current and next year
        min_month = today.month  # Minimum month in min_year is current month

        if data.act == CalendarActions.ignore:
            await query.answer(cache_time=60)
        elif data.act == CalendarActions.set_y:
            await query.message.edit_reply_markup(reply_markup=await self._get_month_kb(int(data.year)))
        elif data.act == CalendarActions.start:
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(int(data.year)))
        elif data.act == CalendarActions.set_m:
            await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(int(data.year), int(data.month)))
        elif data.act == CalendarActions.day:
            return await self.process_day_select(data, query)
        elif data.act == CalendarActions.cancel:
            await query.message.delete_reply_markup()
        elif data.act == CalendarActions.prev_y:
            if data.month == -1:
                # From month keyboard: change year and show months
                new_year = max(int(data.year) - 1, min_year)
                await query.message.edit_reply_markup(reply_markup=await self._get_month_kb(new_year))
            else:
                # From days keyboard: change year, keep month, show days
                new_year = max(int(data.year) - 1, min_year)
                new_month = min(data.month, 12) if new_year > min_year else max(data.month, min_month)
                await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(new_year, new_month))
        elif data.act == CalendarActions.next_y:
            if data.month == -1:
                # From month keyboard: change year and show months
                new_year = min(int(data.year) + 1, max_year)
                await query.message.edit_reply_markup(reply_markup=await self._get_month_kb(new_year))
            else:
                # From days keyboard: change year, keep month, show days
                new_year = min(int(data.year) + 1, max_year)
                new_month = min(data.month, 12) if new_year > min_year else max(data.month, min_month)
                await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(new_year, new_month))
        elif data.act == CalendarActions.prev_m:
            temp_date = datetime(int(data.year), int(data.month), 1) - timedelta(days=1)
            new_year = temp_date.year
            new_month = temp_date.month
            if new_year < min_year or (new_year == min_year and new_month < min_month):
                new_year = min_year
                new_month = min_month  # Stay at min_month of min_year
            await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(new_year, new_month))
        elif data.act == CalendarActions.next_m:
            temp_date = datetime(int(data.year), int(data.month), 1) + timedelta(days=31)
            new_year = temp_date.year
            new_month = temp_date.month
            if new_year > max_year:
                new_year = max_year
                new_month = 12  # Stay at December of max_year
            await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(new_year, new_month))
        return return_data
