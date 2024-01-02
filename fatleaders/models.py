from django.db import models
from afat.models import AFatLinkType
from allianceauth.eveonline.models import EveAllianceInfo

class FatBoardLeadersSetup(models.Model):
    alliance = models.ManyToManyField(EveAllianceInfo, blank=True)
    
    name = models.CharField(max_length=500)
    message = models.CharField(max_length=500)
    
    time_to_look_back = models.IntegerField(default=30)
    types_in_ratio = models.ManyToManyField(AFatLinkType, blank=True, related_name="ratio_types")
    types_to_breakout = models.ManyToManyField(AFatLinkType, through="LeaderBoardTypeThrough", blank=True)


class LeaderBoardTypeThrough(models.Model):
    # through fields
    LeaderBoard = models.ForeignKey(FatBoardLeadersSetup, on_delete=models.CASCADE)
    
    fatLinkType = models.ForeignKey(
        AFatLinkType, on_delete=models.CASCADE)

    # report fields
    rank = models.IntegerField(
        default=5, help_text="Order the field will be show in. Lowest First.")
    
    header = models.CharField(
        max_length=250,
        help_text="Column header line one, show to the user.")
    
    header_line_two = models.CharField(
        max_length=250,
        default= "",
        blank=True,
        help_text="Column header line two, show to the user.")

    class Meta:
        verbose_name = "AFAT Type Field"
        verbose_name_plural = verbose_name + "s"

    def __str__(self):
        return f"{self.header}"

