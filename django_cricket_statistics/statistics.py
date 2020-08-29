"""Queries for calculating standard statistics."""

from django.db.models import Case, Count, F, IntegerField, OuterRef, Subquery, Sum, When

from django_cricket_statistics.models import Hundred, FiveWicketInning, BALLS_PER_OVER

# batting statistics
BATTING_RUNS = {"batting_runs__sum": Sum("batting_runs")}
BATTING_INNINGS = {"batting_innings__sum": Sum("batting_innings")}
BATTING_NOT_OUTS = {"batting_not_outs__sum": Sum("batting_not_outs")}
BATTING_OUTS = {
    **BATTING_INNINGS,
    **BATTING_NOT_OUTS,
    "batting_outs__sum": F("batting_innings__sum") - F("batting_outs__sum"),
}
BATTING_AVERAGE = {
    **BATTING_RUNS,
    **BATTING_OUTS,
    "batting_average": (
        Case(
            When(
                batting_outs__sum__gt=0,
                then=F("batting_runs__sum") / F("batting_outs__sum"),
            ),
            default=None,
        ),
    ),
}
HUNDREDS_SUBQUERY = (
    Hundred.objects.filter(statistic=OuterRef("pk"))
    .order_by()
    .values("statistic")
    .annotate(hund=Count("*"))
    .values("hund")
)
HUNDREDS = {"hundreds": Sum(Subquery(HUNDREDS_SUBQUERY, output_field=IntegerField()))}


# bowling statistics
BOWLING_RUNS = {"bowling_runs__sum": Sum("bowling_runs")}
BOWLING_WICKETS = {"bowling_wickets__sum": Sum("bowling_wickets")}
BOWLING_AVERAGE = {
    **BOWLING_RUNS,
    **BOWLING_WICKETS,
    "bowling_average": (
        Case(
            When(
                bowling_wickets__sum__gt=0,
                then=F("bowling_runs__sum") / F("bowling_wickets__sum"),
            ),
            default=None,
        ),
    ),
}
BOWLING_BALLS = {"bowling_balls__sum": Sum("bowling_balls")}
BOWLING_ECONOMY_RATE = {
    **BOWLING_RUNS,
    **BOWLING_BALLS,
    "bowling_economy_rate": (
        Case(
            When(
                bowling_balls__sum__gt=0,
                then=F("bowling_runs__sum") / F("bowling_balls__sum") * BALLS_PER_OVER,
            ),
            default=None,
        ),
    ),
}
BOWLING_STRIKE_RATE = {
    **BOWLING_WICKETS,
    **BOWLING_BALLS,
    "bowling_strike_rate": (
        Case(
            When(
                bowling_wickets__sum__gt=0,
                then=F("bowling_wickets__sum")
                / F("bowling_balls__sum")
                * BALLS_PER_OVER,
            ),
            default=None,
        ),
    ),
}
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
