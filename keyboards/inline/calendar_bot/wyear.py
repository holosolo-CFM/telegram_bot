from keyboards.inline.calendar_bot.base import MONTH
from keyboards.inline.calendar_bot.detailed import DetailedTelegramCalendar


class WYearTelegramCalendar(DetailedTelegramCalendar):
    first_step = MONTH