"""Queries for calculating standard statistics."""

from django.db.models import (
    Case,
    CharField,
    Count,
    ExpressionWrapper,
    F,
    FloatField,
    IntegerField,
    Max,
    Min,
    OuterRef,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Cast, Concat

from django_cricket_statistics.models import Hundred, FiveWicketInning, BALLS_PER_OVER

# overall
MATCHES = {"number_of_matches__sum": Sum("number_of_matches")}
SEASON_RANGE = {
    "start_year": Min("season__year"),
    "end_year": Max("season__year") + 1,
    "season_range": Concat(
        F("start_year"), Value("-"), F("end_year"), output_field=CharField()
    ),
}

# batting statistics
BATTING_RUNS = {"batting_aggregate__sum": Sum("batting_aggregate")}
BATTING_INNINGS = {"batting_innings__sum": Sum("batting_innings")}
BATTING_NOT_OUTS = {"batting_not_outs__sum": Sum("batting_not_outs")}
BATTING_OUTS = {
    **BATTING_INNINGS,
    **BATTING_NOT_OUTS,
    "batting_outs__sum": F("batting_innings__sum") - F("batting_not_outs__sum"),
}
BATTING_AVERAGE = {
    **BATTING_RUNS,
    **BATTING_OUTS,
    "batting_average": ExpressionWrapper(
        Case(
            When(
                batting_outs__sum__gt=0,
                then=Cast(F("batting_aggregate__sum"), FloatField())
                / Cast(F("batting_outs__sum"), FloatField()),
            ),
            default=None,
        ),
        output_field=FloatField(),
    ),
}
# BATTING_BEST_INNINGS = {}
HUNDREDS_SUBQUERY = (
    Hundred.objects.filter(statistic=OuterRef("pk"))
    .order_by()
    .values("statistic")
    .annotate(hund=Count("*"))
    .values("hund")
)
HUNDREDS = {"hundreds": Sum(Subquery(HUNDREDS_SUBQUERY, output_field=IntegerField()))}


# bowling statistics
BOWLING_BALLS = {"bowling_balls__sum": Sum("bowling_balls")}
BOWLING_RUNS = {"bowling_runs__sum": Sum("bowling_runs")}
BOWLING_WICKETS = {"bowling_wickets__sum": Sum("bowling_wickets")}
BOWLING_AVERAGE = {
    **BOWLING_RUNS,
    **BOWLING_WICKETS,
    "bowling_average": ExpressionWrapper(
        Case(
            When(
                bowling_wickets__sum__gt=0,
                then=Cast(F("bowling_runs__sum"), FloatField())
                / Cast(F("bowling_wickets__sum"), FloatField()),
            ),
            default=None,
        ),
        output_field=FloatField(),
    ),
}
BOWLING_ECONOMY_RATE = {
    **BOWLING_RUNS,
    **BOWLING_BALLS,
    "bowling_economy_rate": ExpressionWrapper(
        Case(
            When(
                bowling_balls__sum__gt=0,
                then=Cast(F("bowling_runs__sum"), FloatField())
                / Cast(F("bowling_balls__sum"), FloatField())
                * BALLS_PER_OVER,
            ),
            default=None,
        ),
        output_field=FloatField(),
    ),
}
BOWLING_STRIKE_RATE = {
    **BOWLING_WICKETS,
    **BOWLING_BALLS,
    "bowling_strike_rate": ExpressionWrapper(
        Case(
            When(
                bowling_balls__sum__gt=0,
                then=Cast(F("bowling_balls__sum"), FloatField())
                / Cast(F("bowling_wickets__sum"), FloatField()),
            ),
            default=None,
        ),
        output_field=FloatField(),
    ),
}
# BOWLING_BEST_INNINGS = {}
FIVE_WICKET_INNINGS_SUBQUERY = (
    FiveWicketInning.objects.filter(statistic=OuterRef("pk"))
    .values("statistic")
    .annotate(five=Count("*"))
    .values("five")
)
FIVE_WICKET_INNINGS = {
    "five_wicket_innings": Sum(
        Subquery(FIVE_WICKET_INNINGS_SUBQUERY, output_field=IntegerField())
    )
}
# WICKETKEEPING_CATCHES = {}
# WICKETKEEPING_STUMPINGS = {}
# FIELDING_CATCHES = {}

# helper to get all statistics for a given queryset
ALL_STATISTICS = {
    **MATCHES,
    **BATTING_INNINGS,
    **BATTING_RUNS,
    **BATTING_NOT_OUTS,
    **BATTING_AVERAGE,
    # **BATTING_BEST_INNINGS,
    # **HUNDREDS,
    **BOWLING_BALLS,
    **BOWLING_RUNS,
    **BOWLING_WICKETS,
    **BOWLING_AVERAGE,
    **BOWLING_ECONOMY_RATE,
    **BOWLING_STRIKE_RATE,
    # **BOWLING_BEST_INNINGS,
    # **FIVE_WICKET_INNINGS,
    # **WICKETKEEPING_CATCHES,
    # **WICKETKEEPING_STUMPINGS,
    # **FIELDING_CATCHES,
}
ALL_STATISTIC_NAMES = {
    "number_of_matches__sum": "Mat",
    "batting_innings__sum": "Inns",
    "batting_aggregate__sum": "Runs",
    "batting_not_outs__sum": "NO",
    "batting_average": "Ave",
    # "batting_best_innings": "HS",
    # "hundreds": "100",
    "bowling_balls__sum": "Balls",
    "bowling_runs__sum": "Runs",
    "bowling_wickets__sum": "Wkts",
    "bowling_average": "Ave",
    "bowling_economy_rate": "Econ",
    "bowling_strike_rate": "SR",
    # "bowling_best_innings": "BB",
    # "five_wicket_innings": "5WI",
    # "wicketkeeping_catches__sum": "WK Ct",
    # "wicketkeeping_stumpings__sum": "WK St",
    # "fielding_catches__sum": "Ct",
}
ALL_STATISTIC_FLOATS = {
    "batting_average",
    "bowling_average",
    "bowling_economy_rate",
    "bowling_strike_rate",
}
