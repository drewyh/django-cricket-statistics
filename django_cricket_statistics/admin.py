"""Admin for statistics."""

import re
from typing import Dict, Optional, Tuple

from django.forms import (
    BaseInlineFormSet,
    CharField,
    Form,
    NumberInput,
    ModelForm,
    TextInput,
)
from django.contrib import admin
from django.forms.fields import validators
from django.db import models
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest

from django_cricket_statistics.models import (
    Player,
    Grade,
    Season,
    Statistic,
    FirstElevenNumber,
    Hundred,
    FiveWicketInning,
    BALLS_PER_OVER,
)


BOWLING_OVERS_RE = re.compile(r"^(?P<overs>\d+)(?:\.(?P<balls>\d?))?$")
BOWLING_BEST_BOWLING_RE = re.compile(r"^(?P<wickets>10|[0-9])\/(?P<runs>\d+)$")
BATTING_HIGH_SCORE_RE = re.compile(r"^(?P<runs>\d+)(?P<notout>\*?)$")


class StatisticInlineFormSet(BaseInlineFormSet):
    """Inline form set for statistics."""

    class Meta:  # noqa: D106 # pylint: disable=missing-class-docstring
        model = Statistic
        fields = "__all__"

    def __init__(self, *args: Tuple, **kwargs: Dict) -> None:
        """Select additional linked models."""
        super().__init__(*args, **kwargs)
        self.queryset: models.QuerySet = self.queryset.select_related(
            "player", "season", "grade"
        )

    def add_fields(self, form: Form, index: int) -> None:
        """Add custom fields for fields with compound input."""
        super().add_fields(form, index)

        # bowling overs are used instead of bowling balls input
        form.fields["bowling_overs_input"] = CharField(
            label="ovs.",
            max_length=6,
            required=False,
            validators=(validators.RegexValidator(regex=BOWLING_OVERS_RE),),
        )
        form.fields["bowling_overs_input"].widget.attrs.update(size="4ch")

        # combine best bowling figures into a single input
        form.fields["best_bowling_input"] = CharField(
            label="BB",
            max_length=6,
            required=False,
            validators=(validators.RegexValidator(regex=BOWLING_BEST_BOWLING_RE),),
        )
        form.fields["best_bowling_input"].widget.attrs.update(
            size="4ch", title="e.g. 4/77"
        )

        # combine batting high score into a single input
        form.fields["batting_high_score_input"] = CharField(
            label="HS",
            max_length=4,
            required=False,
            validators=(validators.RegexValidator(regex=BATTING_HIGH_SCORE_RE),),
        )
        form.fields["batting_high_score_input"].widget.attrs.update(
            size="4ch", title="Use * for not out, e.g. 143*"
        )


class StatisticForm(ModelForm):
    """Form for statistics."""

    batting_high_score_input = CharField(max_length=4, required=False)
    bowling_overs_input = CharField(max_length=4, required=False)
    best_bowling_input = CharField(max_length=6, required=False)

    def __init__(self, *args: str, **kwargs: models.Model) -> None:
        """Initialise the model form for compound fields."""
        super().__init__(*args, **kwargs)

        instance = kwargs.get("instance", None)

        if instance is not None:
            self.initial["bowling_overs_input"] = instance.bowling_overs
            self.initial["best_bowling_input"] = instance.bowling_best_bowling
            self.initial["batting_high_score_input"] = instance.batting_high_score
        else:
            self.initial["bowling_overs_input"] = "0.0"
            self.initial["best_bowling_input"] = "0/0"
            self.initial["batting_high_score_input"] = "0"

    def clean_batting_high_score_input(self) -> str:
        """Process the batting score to split it into runs and notout."""
        data = self.cleaned_data.get("batting_high_score_input")
        match = BATTING_HIGH_SCORE_RE.match(data)

        # catch blank default
        if not match:
            return data

        runs = int(match.group("runs"))
        not_out = bool(match.group("notout"))
        self.cleaned_data["batting_high_score_runs_input"] = runs
        self.cleaned_data["batting_high_score_is_not_out_input"] = not_out

        return data

    def clean_bowling_overs_input(self) -> str:
        """Process the bowling overs to compute total balls bowled."""
        data = self.cleaned_data.get("bowling_overs_input")
        match = BOWLING_OVERS_RE.match(data)

        # catch blank default
        if not match:
            return data

        overs = int(match.group("overs"))
        balls = int(match.group("balls"))
        self.cleaned_data["bowling_balls_input"] = overs * BALLS_PER_OVER + balls

        return data

    def clean_best_bowling_input(self) -> str:
        """Process the best bowling to determine the wickets and runs."""
        data = self.cleaned_data.get("best_bowling_input")
        match = BOWLING_BEST_BOWLING_RE.match(data)

        # catch blank default
        if not match:
            return data

        wickets = int(match.group("wickets"))
        runs = int(match.group("runs"))
        self.cleaned_data["best_bowling_wickets_input"] = wickets
        self.cleaned_data["best_bowling_runs_input"] = runs

        return data

    def save(self, commit: bool = True) -> models.Model:
        """Save the compound fields onto the instance."""
        instance = super().save(commit=commit)

        for attr in (
            "bowling_balls",
            "best_bowling_wickets",
            "best_bowling_runs",
            "batting_high_score_runs",
            "batting_high_score_is_not_out",
        ):
            input_name = attr + "__input"
            setattr(instance, input_name, self.cleaned_data.get(input_name))

        if commit:
            instance.save()

        return instance

    class Meta:  # noqa: D106
        model = Statistic
        fields = "__all__"


class StatisticInline(admin.TabularInline):
    """Inline for statistics."""

    model = Statistic
    verbose_name = None
    extra = 0
    show_change_link = True
    fields = (
        "season",
        "grade",
        "matches",
        "batting_innings",
        "batting_not_outs",
        "batting_high_score_input",
        "batting_runs",
        "number_of_ducks",
        "fielding_catches_non_wk",
        "fielding_catches_wk",
        "fielding_run_outs",
        "fielding_throw_outs",
        "fielding_stumpings",
        "bowling_overs_input",
        "best_bowling_input",
        "bowling_maidens",
        "bowling_runs",
        "bowling_wickets",
    )
    formset = StatisticInlineFormSet
    form = StatisticForm
    formfield_overrides = {
        models.PositiveSmallIntegerField: {
            "widget": NumberInput(attrs={"style": "width:5ch"})
        }
    }


class HundredInline(admin.TabularInline):
    """Inline for hundreds."""

    model = Hundred
    verbose_name = None
    extra = 0
    fields = ("runs", "is_not_out", "is_in_final")


class FiveWicketInningInline(admin.TabularInline):
    """Inline for five wicket innings."""

    model = FiveWicketInning
    verbose_name = None
    extra = 0
    fields = ("wickets", "runs", "is_in_final")


class GlobalModelPermsModelAdmin(admin.ModelAdmin):
    """Class setting model permissions."""

    # pylint: disable=no-self-use
    def global_get_model_perms(self, request: HttpRequest) -> Dict:
        """Global function to allow only superuser's permission."""
        if not request.user.is_superuser:
            return {}

        return super().get_model_perms(request)


class SuperuserModelPermsModelAdmin(GlobalModelPermsModelAdmin):
    """Class setting model permissions allowing only superuser modifications."""

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Only permit superusers to add."""
        return request.user.is_superuser

    def has_change_permission(
        self, request: HttpRequest, obj: Optional[models.Model] = None
    ) -> bool:
        """Only permit superusers to change."""
        return request.user.is_superuser

    def has_delete_permission(
        self, request: HttpRequest, obj: Optional[models.Model] = None
    ) -> bool:
        """Only permit superusers to delete."""
        return request.user.is_superuser


@admin.register(Player)
class PlayerAdmin(GlobalModelPermsModelAdmin):
    """Admin settings for players."""

    actions = None
    list_display = (
        "__str__",
        "first_name",
        "last_name",
        "middle_names",
        "nickname",
        "first_eleven_number",
    )
    search_fields = list_display[1:-1]
    fieldsets = (
        ("Edit Details", {"classes": ("collapse",), "fields": list_display[1:]}),
    )
    inlines = (StatisticInline,)
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "20ch"})}
    }

    def has_delete_permission(
        self, request: HttpRequest, obj: Optional[models.Model] = None
    ) -> bool:
        """Only permit superusers to delete."""
        return request.user.is_superuser


@admin.register(Statistic)
class StatisticAdmin(GlobalModelPermsModelAdmin):
    """Admin settings for statistics."""

    actions = None
    list_display = ("player", "season", "grade", "matches")
    fields = (("statistic_display",),)
    readonly_fields = tuple(f for fg in fields for f in fg)
    inlines = (HundredInline, FiveWicketInningInline)

    # pylint: disable=no-self-use
    def statistic_display(self, instance: Statistic) -> str:
        """Show player, season, and grade for statistic display."""
        return f"{instance.player.long_name} - {instance.season} - {instance.grade}"

    statistic_display.short_description = "Editing"  # type: ignore

    def response_post_save_change(
        self, request: HttpRequest, obj: models.Model
    ) -> HttpResponse:
        """Determine where to redirect after the 'Save' button has been pressed.

        Modify this to redirect to the parent player of the statistic.
        """
        opts = self.model._meta
        per = Player._meta

        if self.has_change_permission(request, None):
            post_url = reverse(
                "admin:%s_%s_change" % (opts.app_label, per.model_name),
                args=[obj.player.pk],
                current_app=self.admin_site.name,
            )
        else:
            post_url = reverse("admin:index", current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)


@admin.register(Grade)
class GradeAdmin(SuperuserModelPermsModelAdmin):
    """Admin settings for grades."""


@admin.register(Season)
class SeasonAdmin(SuperuserModelPermsModelAdmin):
    """Admin settings for seasons."""


@admin.register(FirstElevenNumber)
class FirstElevenNumberAdmin(GlobalModelPermsModelAdmin):
    """Admin settings for first eleven numbers."""

    list_display = ("pk", "player")
    actions = None


@admin.register(Hundred)
class HundredAdmin(GlobalModelPermsModelAdmin):
    """Admin settings for hundreds."""

    list_display = ("statistic", "runs", "is_not_out", "is_in_final")
    actions = None
    fields = (("statistic", "runs", "is_not_out", "is_in_final"),)
    ordering = ("-statistic__season__year", "statistic__grade")


@admin.register(FiveWicketInning)
class FiveWicketInningAdmin(GlobalModelPermsModelAdmin):
    """Admin settings for five wicket innings."""

    list_display = ("statistic", "wickets", "runs", "is_in_final")
    actions = None
    fields = (("statistic", "wickets", "runs", "is_in_final"),)
    ordering = ("-statistic__season__year", "statistic__grade")
