
from datetime import datetime

from django.utils import timezone
from stocks.dataclasses import TimeSeriesData
from stocks.dtos.dtos import TimeSeriesDTO



class TimeSeriesDTOMapper:
    """
    Convierte datos crudos (DataFrame o QuerySet) en objetos TimeSeriesDTO.
    """

    @staticmethod
    def timedata_to_dto(time_series_data: list[TimeSeriesData]) -> list[TimeSeriesDTO]:
        """
        Converts a list of TimeSeriesData objects into a list of TimeSeriesDTOs.
        Keeps only ticker (symbol), timestamp (date), and close price.
        """
        return [
            TimeSeriesDTO(
                ticker=item.symbol,
                timestamp=item.date,
                close_price=float(item.close_price)
            )
            for item in time_series_data
        ]

    @staticmethod
    def from_queryset(queryset) -> list[TimeSeriesDTO]:
        """
        Converts a Django QuerySet of TimeSeries objects into DTOs.
        Ensures timestamps are timezone-aware datetimes.
        """
        return [
            TimeSeriesDTO(
                ticker=item.asset.ticker,
                timestamp=timezone.make_aware(
                    datetime.combine(item.date, datetime.min.time())
                ),
                close_price=float(item.close_price)
            )
            for item in queryset
        ]
