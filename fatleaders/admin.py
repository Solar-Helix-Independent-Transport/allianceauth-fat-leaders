from django.contrib import admin
from .models import FatBoardLeadersSetup, LeaderBoardTypeThrough
# Register your models here.

class LeaderBoardTypeThroughAdmin(admin.StackedInline):
    model = LeaderBoardTypeThrough


@admin.register(FatBoardLeadersSetup)
class FATAdmin(admin.ModelAdmin):
    list_display = ("name", "message")
    filter_horizontal = ('alliance',)

    select_related=True

    inlines = [
        LeaderBoardTypeThroughAdmin,
    ]

