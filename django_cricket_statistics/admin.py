"""Admin for statistics."""

from decimal import Decimal
import re

from django import forms
from django.forms import NumberInput, TextInput
from django.contrib import admin
from django.forms.fields import validators
from django.db import models
from django.urls import reverse
from django.http import HttpResponseRedirect

from django_cricket_statistics.models import (
    Player,
    Grade,
    Season,
    Statistic,
    Hundred,
    FiveWicketInning,
    BALLS_PER_OVER,
)


class StatisticInlineFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.queryset.select_related("player", "season", "grade")

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["bowling_overs_input"] = forms.CharField(
            label="ovs.",
            max_length=6,
            required=False,
            validators=(
                validators.RegexValidator(regex=r"^(([1-9]\d*)|[0])((\.[0-5])?)$"),
            ),
        )
        form.fields["best_bowling_input"] = forms.CharField(
            label="BB",
            max_length=6,
            required=False,
            validators=(validators.RegexValidator(regex=r"^(10|[0-9])(/)(\d+)$"),),
        )
        form.fields["batting_high_score_input"] = forms.CharField(
            label="HS",
            max_length=4,
            required=False,
            validators=(validators.RegexValidator(regex=r"^(\d+)(\*?)$"),),
        )

        form.fields["bowling_overs_input"].widget.attrs.update(size="4ch")
        form.fields["best_bowling_input"].widget.attrs.update(size="4ch")
        form.fields["batting_high_score_input"].widget.attrs.update(title="e.g. 4/77")
        form.fields["batting_high_score_input"].widget.attrs.update(size="4ch")
        form.fields["batting_high_score_input"].widget.attrs.update(
            title="Use * for not out, e.g. 143*"
        )

    class Meta:
        model = Statistic
        fields = "__all__"


class StatisticForm(forms.ModelForm):
    batting_high_score_input = forms.CharField(max_length=4, required=False)
    bowling_overs_input = forms.CharField(max_length=4, required=False)
    best_bowling_input = forms.CharField(max_length=6, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get("instance", None)

        if instance is not None:
            self.initial["bowling_overs_input"] = Decimal(instance.bowling_overs)
            self.initial["best_bowling_input"] = instance.bowling_best_bowling
            self.initial["batting_high_score_input"] = instance.batting_high_score
        else:
            self.initial["bowling_overs_input"] = Decimal(0)
            self.initial["best_bowling_input"] = "0/0"
            self.initial["batting_high_score_input"] = "0"

    def clean_batting_high_score_input(self):
        data = self.cleaned_data.get("batting_high_score_input")

        # catch blank default
        if data == "":
            return data

        is_not_out = data.endswith("*")
        runs = int(data.strip("*"))
        self.cleaned_data["batting_high_score_runs_inp"] = runs
        self.cleaned_data["batting_high_score_is_not_out_inp"] = is_not_out

        return data

    def clean_bowling_overs_input(self):
        cleaned_data = self.cleaned_data
        data = cleaned_data.get("bowling_overs_input")

        # catch blank default
        if data == "":
            return data

        data = Decimal(cleaned_data.get("bowling_overs_input"))
        ovs, balls = divmod(data, 1)
        total_balls = ovs * BALLS_PER_OVER + 10 * balls
        cleaned_data["balls_bowled"] = total_balls

        return total_balls

    def clean_best_bowling_input(self):
        data = self.cleaned_data.get("best_bowling_input")

        # catch blank default
        if data == "":
            return data

        wickets, runs = re.split(r"/", data, maxsplit=1)
        self.cleaned_data["best_bowling_wickets_inp"] = int(wickets)
        self.cleaned_data["best_bowling_runs_inp"] = int(runs)

        return data

    def save(self, commit=True):
        instance = super().save(commit=commit)

        instance.bowling_balls = self.cleaned_data.get("balls_bowled")

        instance.best_bowling_wickets = self.cleaned_data.get(
            "best_bowling_wickets_inp"
        )
        instance.best_bowling_runs = self.cleaned_data.get("best_bowling_runs_inp")

        instance.batting_high_score_runs = self.cleaned_data.get(
            "batting_high_score_runs_inp"
        )
        instance.batting_high_score_is_not_out = self.cleaned_data.get(
            "batting_high_score_is_not_out_inp"
        )

        if commit:
            instance.save()

        return instance

    class Meta:
        model = Statistic
        fields = "__all__"


class GeneralStatisticInline(admin.TabularInline):
    model = Statistic
    verbose_name = None
    extra = 0
    show_change_link = True
    fields = (
        "season",
        "grade",
        "edit",
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
    readonly_fields = ("edit",)
    formset = StatisticInlineFormSet
    form = StatisticForm
    formfield_overrides = {
        models.PositiveSmallIntegerField: {
            "widget": NumberInput(attrs={"style": "width:5ch"})
        }
    }
    template = "admin/tabular.html"

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        stat_id = request.GET.get("id", default=None)

        if stat_id is not None:
            qs = qs.filter(id=stat_id)

        return qs

    def edit(self, instance):
        return "100s / 5WIs"


class HundredInline(admin.TabularInline):
    model = Hundred
    verbose_name = None
    extra = 0
    fields = ("runs", "is_not_out", "is_in_final")
    template = "admin/tabular.html"


class FiveWicketInningInline(admin.TabularInline):
    model = FiveWicketInning
    verbose_name = None
    extra = 0
    fields = ("wickets", "runs", "is_in_final")
    template = "admin/tabular.html"


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    actions = None
    list_display = (
        "__str__",
        "first_name",
        "last_name",
        "middle_names",
        "nickname",
        "first_XI_number",
    )
    search_fields = list_display[1:]
    fieldsets = (("Edit Details", {"classes": ("collapse",), "fields": search_fields}),)
    inlines = (GeneralStatisticInline,)
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "20ch"})}
    }

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("player", "season", "grade", "matches")
    fields = (("statistic_display",),)
    readonly_fields = tuple(f for fg in fields for f in fg)
    inlines = (HundredInline, FiveWicketInningInline)

    def statistic_display(self, instance):
        return "{0} - {1} - {2}".format(
            instance.player.long_name, str(instance.season), str(instance.grade)
        )

    statistic_display.short_description = "Editing"

    def get_model_perms(self, request):
        if not request.user.is_superuser:
            return {}

        return super().get_model_perms(request)

    def response_post_save_change(self, request, obj):
        """
        Figure out where to redirect after the 'Save' button has been pressed
        when editing an existing object.

        Modify this to redirect to the parent player of the statistic
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
class GradeAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        if not request.user.is_superuser:
            return {}

        return super().get_model_perms(request)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        if not request.user.is_superuser:
            return {}

        return super().get_model_perms(request)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Hundred)
class HundredAdmin(admin.ModelAdmin):
    list_display = ("statistic", "runs", "is_not_out", "is_in_final")
    actions = None
    fields = (("statistic", "runs", "is_not_out", "is_in_final"),)
    ordering = ("-statistic__season__year", "statistic__grade")

    def get_model_perms(self, request):
        if not request.user.is_superuser:
            return {}

        return super().get_model_perms(request)


@admin.register(FiveWicketInning)
class FiveWicketInningAdmin(admin.ModelAdmin):
    list_display = ("statistic", "wickets", "runs", "is_in_final")
    actions = None
    fields = (("statistic", "wickets", "runs", "is_in_final"),)
    ordering = ("-statistic__season__year", "statistic__grade")

    def get_model_perms(self, request):
        if not request.user.is_superuser:
            return {}

        return super().get_model_perms(request)
