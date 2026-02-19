# intertime.py is a datetime utility for sql_cap.py
from dateutil import parser
import datetime
from zoneinfo import ZoneInfo

class INTERTIME():
    def __init__(self, region):
        """

        Utility methods for working with time strings, datetime objects and decimal year. Set for NZ time zone
        with awareness of daylight saving. More methods could be added but stringing together a few will likely
        achieve the conversion you need.
        :param region: string, normally "Pacific/Auckland"
        """
        self.loc_zone = region

    def date_to_sec(self, string):
        """

        converts a string like 22 June, 2024, 1:30 PM into seconds since epoch
        :param string:
        :return: seconds since epoch
        """
        parsed_date = parser.parse(string)
        local_dt = parsed_date.replace(tzinfo=ZoneInfo(self.loc_zone))  # add time zone
        secs = int(local_dt.timestamp())
        return secs


    def sec_to_date(self, epoch_seconds):
        """

        :param seconds: since epoch time
        :return: a structured local datetime
        """
        # Convert to UTC datetime
        utc_dt = datetime.datetime.fromtimestamp(epoch_seconds, tz=ZoneInfo("UTC"))
        local_dt = utc_dt.astimezone(ZoneInfo(self.loc_zone))
        return local_dt

    @staticmethod
    def datetime_to_decimal_year(dt):
        """

        :param dt: a datetime object
        :return: a decimal year, e.g. 2025.321 in local time?
        """
        # Ensure dt is timezone-naive by converting to UTC if it's aware
        if dt.tzinfo is not None:
            dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        year_start = datetime.datetime(dt.year, 1, 1)
        year_end = datetime.datetime(dt.year + 1, 1, 1)
        year_length = (year_end - year_start).total_seconds()
        seconds_into_year = (dt - year_start).total_seconds()
        decimal_year = dt.year + seconds_into_year / year_length
        return decimal_year

    @staticmethod
    def decimal_year_to_datetime(decimal_year):
        """

        :param decimal_year:
        :return: structured datetime local
        """
        tz_str = 'Pacific/Auckland'
        # Extract the integer year and the fractional part
        year = int(decimal_year)
        fraction = decimal_year - year

        # Define start and end of the year in UTC
        start_of_year = datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc)
        start_of_next_year = datetime.datetime(year + 1, 1, 1, tzinfo=datetime.timezone.utc)
        # Total seconds in the year
        year_duration = (start_of_next_year - start_of_year).total_seconds()
        # Seconds into the year
        seconds_into_year = fraction * year_duration
        # Final UTC datetime
        utc_dt = start_of_year + datetime.timedelta(seconds=seconds_into_year)
        # Convert to target timezone
        local_dt = utc_dt.astimezone(ZoneInfo("Pacific/Auckland"))

        return local_dt

    @staticmethod
    def local_to_UTC(local_dt):
        """

        :param local_dt: assumed timezone aware, as out of sec_to_date
        :return:
        """
        utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
        return utc_dt

    def local_to_sql_UTC(self, local):
        """

        :param local: date string, not yet a datetime object
        :return: string in UTC
        """
        b = parser.parse(local)  # convert to a datetime
        c = self.local_to_UTC(b)  # convert to a UTC datetime
        d = c.replace(tzinfo=None)  # remove timezone
        e = d.strftime("%Y-%m-%d %H:%M:%S")
        return e
