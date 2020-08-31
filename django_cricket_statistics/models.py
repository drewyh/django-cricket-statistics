"""Models for statistics."""

from decimal import Decimal
from typing import Tuple

from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse

BALLS_PER_OVER = 6


class CricketModelBase(models.Model):
    """Base class for all models to be stored in the db."""

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:  # noqa: D106
        abstract = True


class Player(CricketModelBase):
    """Class representing a single player."""

    first_name = models.CharField(max_length=200, blank=True)
    nickname = models.CharField(max_length=200, blank=True)
    middle_names = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200)

    first_XI_number = models.PositiveSmallIntegerField(
        unique=True, blank=True, null=True
    )

    class Meta:  # noqa: D106
        unique_together = ("first_name", "nickname", "middle_names", "last_name")
        ordering = ("last_name", "first_name", "middle_names")

    def get_absolute_url(self) -> str:
        """Get url to a given model."""
        return reverse("player_career", args=(str(self.id),))

    def __str__(self) -> str:
        """Return the name of the player as initials and surname."""

        def initials(names: Tuple[str, ...]) -> str:
            """Return initials of first and middles names."""
            name_split = str(names).split()
            return "".join(s[0].upper() for s in name_split)

        inits = "".join((initials(n) for n in (self.first_name, self.middle_names)))
        inits = inits if inits else "Mr."
        short_name = " ".join((inits, self.last_name))

        return short_name

    @property
    def long_name(self) -> str:
        """Return the full name (including nickname)."""
        names = (
            self.first_name or "Mr.",
            self.middle_names if self.middle_names else None,
            "(" + self.nickname + ")" if self.nickname else None,
            self.last_name,
        )
        return " ".join(n for n in names if n is not None)

    @property
    def short_name(self) -> str:
        """Return the name of the player as initials and surname."""
        return str(self)


class Season(CricketModelBase):
    """Class representing a single season."""

    year = models.PositiveSmallIntegerField(unique=True)

    class Meta:  # noqa: D106
        ordering = ("-year",)

    def __str__(self) -> str:
        """Return the season in YYYY/YY format."""
        year_after = str(self.year_after)
        year_after = year_after[-2:]

        return f"{self.year}/{year_after}"

    @property
    def name(self) -> str:
        """Stringify the year."""
        return str(self)

    @property
    def year_after(self) -> int:
        """Which year follows this one."""
        return int(self.year) + 1


class Grade(CricketModelBase):
    """Class representing a single grade."""

    grade = models.CharField(max_length=50)
    is_senior = models.BooleanField(default=True)

    class Meta:  # noqa: D106
        ordering = ("-is_senior", "grade")

    def __str__(self) -> str:
        """Return the string representation of the grade."""
        return str(self.grade)


class Statistic(CricketModelBase):
    """Class representing a single statistic for a given player/season/grade."""

    player = models.ForeignKey(
        Player, on_delete=models.PROTECT, null=False, blank=False
    )
    season = models.ForeignKey(
        Season, on_delete=models.PROTECT, null=False, blank=False
    )
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, null=False, blank=False)

    # season wide stats
    number_of_matches = models.PositiveSmallIntegerField("mat")

    # batting stats
    batting_innings = models.PositiveSmallIntegerField("inns", default=0)
    batting_aggregate = models.PositiveSmallIntegerField("runs", default=0)
    batting_not_outs = models.PositiveSmallIntegerField("NO", default=0)
    number_batting_milestone_50 = models.PositiveSmallIntegerField("50", default=0)
    number_of_ducks = models.PositiveSmallIntegerField("ducks", default=0)
    batting_high_score_runs = models.PositiveSmallIntegerField(
        "HS runs", default=0, blank=True
    )
    batting_high_score_is_not_out = models.BooleanField(
        "HS NO?", default=False, blank=True
    )
    batting_4s = models.PositiveSmallIntegerField("4s", default=0)
    batting_6s = models.PositiveSmallIntegerField("6s", default=0)

    @property
    def batting_high_score(self) -> str:
        """Return a string of the high score."""
        not_out_string = "*" if self.batting_high_score_is_not_out else ""
        return f"{self.batting_high_score_runs}{not_out_string}"

    batting_high_score.fget.short_description = "HS"  # type: ignore

    # bowling stats
    bowling_wickets = models.PositiveSmallIntegerField("wkts", default=0)
    bowling_maidens = models.PositiveSmallIntegerField("mdns", default=0)
    bowling_runs = models.PositiveSmallIntegerField("runs", default=0)
    best_bowling_wickets = models.PositiveSmallIntegerField(
        "BB wickets", default=0, blank=True
    )
    best_bowling_runs = models.PositiveSmallIntegerField(
        "BB runs", default=0, blank=True
    )
    bowling_balls = models.PositiveSmallIntegerField("balls", default=0, blank=True)

    @property
    def bowling_best_bowling(self) -> str:
        """Return a string of the best bowling."""
        return f"{self.best_bowling_wickets}/{self.best_bowling_runs}"

    bowling_best_bowling.fget.short_description = "BBI"  # type: ignore

    @property
    def bowling_overs(self) -> Decimal:
        """Calculate the overs from the balls bowled."""
        ovs, balls = divmod(self.bowling_balls, BALLS_PER_OVER)
        overs = Decimal(ovs) + Decimal(balls) / Decimal(10)
        return overs

    # fielding stats
    fielding_catches_non_wk = models.PositiveSmallIntegerField("ct", default=0)
    fielding_catches_wk = models.PositiveSmallIntegerField("ct Wk", default=0)
    fielding_run_outs = models.PositiveSmallIntegerField("RO", default=0)
    fielding_throw_outs = models.PositiveSmallIntegerField("TO", default=0)
    fielding_stumpings = models.PositiveSmallIntegerField("st", default=0)

    class Meta:  # noqa: D106
        unique_together = ("player", "season", "grade")
        ordering = (
            "player__last_name",
            "player__first_name",
            "player__middle_names",
            "season",
            "grade",
        )

    def __str__(self) -> str:
        """Return a string for the statistic."""
        return f"{self.player.long_name} - {self.season} - {self.grade}"


class Hundred(CricketModelBase):
    """Class representing a single score of 100."""

    statistic = models.ForeignKey(
        Statistic, on_delete=models.PROTECT, null=False, blank=False
    )

    runs = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(100)]
    )
    is_not_out = models.BooleanField(default=False)
    is_in_final = models.BooleanField(default=False)

    @property
    def score(self) -> str:
        """Return a string of score."""
        not_out_string = "*" if self.is_not_out else ""
        finals_string = "#" if self.is_in_final else ""
        return f"{self.runs}{not_out_string}{finals_string}"

    score.fget.short_description = "score"  # type: ignore

    def __str__(self) -> str:
        """String representation of the hundred."""
        return self.score


class FiveWicketInning(CricketModelBase):
    """Class representing a single five wicket inning."""

    statistic = models.ForeignKey(
        Statistic, on_delete=models.PROTECT, null=False, blank=False
    )

    wickets = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(5)]
    )
    runs = models.PositiveSmallIntegerField(default=0)
    is_in_final = models.BooleanField(default=False)

    @property
    def figures(self) -> str:
        """Return a string of the bowling figures."""
        finals_string = "#" if self.is_in_final else ""
        return f"{self.wickets}/{self.runs}{finals_string}"

    figures.fget.short_description = "figures"  # type: ignore
