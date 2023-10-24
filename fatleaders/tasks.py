from datetime import timedelta
from aadiscordbot.tasks import send_channel_message_by_discord_id
from django.utils import timezone
from discord import File
from django.db.models import Count
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from .models import FatBoardLeadersSetup, LeaderBoardTypeThrough
from PIL import Image, ImageDraw, ImageFont

import io
from afat.models import AFat

from celery import shared_task
from importlib import resources
from . import fonts, images


@shared_task
def post_all_corporate_leader_boards(current_month=False, channel_id=0, fun=False):
    for lb in FatBoardLeadersSetup.objects.all():
        start_time = timezone.now()
        if not current_month:
            start_time = start_time - timedelta(days=timezone.now().day)

        start_time = start_time.replace(day=1, hour=0, minute=0)

        character_list = EveCharacter.objects.filter(
            character_ownership__user__profile__main_character__alliance_id__in=lb.alliance.all().values_list("alliance_id"))

        corporations = []
        corporation_lists = AFat.objects.filter(
            character__in=character_list,
            afatlink__afattime__gte=start_time
        ).values(
            'character__character_ownership__user__profile__main_character__corporation_ticker'
        ).annotate(
            count=Count("id")
        ).order_by("-count")
        for _c in corporation_lists:
            corporations.append((_c['character__character_ownership__user__profile__main_character__corporation_ticker']))
        types_list = LeaderBoardTypeThrough.objects.filter(
            LeaderBoard=lb).order_by("rank")
        type_widths = {}

        for t in types_list:
            type_widths[t.id] = {"h": t.header, "w": 0}

        font_name = "OpenSans.ttf"
        if fun:
            font_name = "Brookeshappell.ttf"
        test_string = "ApygZ12"
        line_padding = 2
        coll_padding = 30
        font_size = 36
        line_y = 10
        line_x = 10
        # blue text = 0, 15, 85
        # red text = 139, 0, 0

        font_colour_title = (255, 255, 255)
        font_colour_rest = (200, 200, 200)

        if fun:
            font_colour_title = (0, 15, 85)
            font_colour_rest = (139, 0, 0)

        with resources.path(fonts, font_name) as font_path:
            with open(font_path, "rb") as f:
                font = ImageFont.truetype(f, font_size)

        _measured_test_string = font.getbbox(test_string)
        line_height = _measured_test_string[3] + line_padding
        ticker_width = _measured_test_string[2] + coll_padding

        type_width = 0
        for id, t in type_widths.items():
            t["w"] = font.getbbox(t["h"])[2]
            type_width += coll_padding + t["w"]

        total_height = line_y*2 + \
            (line_height)*(len(corporations)+4)
        total_width = (ticker_width*2)+(type_width)

        img = Image.new(
            'RGB', (total_width, total_height), color=(66, 69, 73))
        d = ImageDraw.Draw(img)
        if fun:
            with resources.path(images, "crinkle_paper.jpg") as bg_path:
                with open(bg_path, "rb") as f:
                    img_tile = Image.open(f)
                    w, h = img.size
                    bg_w, bg_h = img_tile.size
                    img_tile = img_tile.resize((int(bg_w/10), int(bg_h/10)))
                    bg_w, bg_h = img_tile.size

                    for i in range(0, w, bg_w):
                        for j in range(0, h, bg_h):
                            # paste the image at location i, j:
                            fl_img = img_tile
                            if (i % 2) == 0:
                                fl_img = fl_img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                            if (j % 2) == 0:
                                fl_img = fl_img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                            img.paste(fl_img, (i, j))

        _, _, _w, _ = font.getbbox(lb.name)
        d.text(((total_width-_w)/2, line_y),
               lb.name, font=font, fill=font_colour_title)
        line_y += line_height

        _, _, _w, _ = font.getbbox(lb.message)
        d.text(((total_width-_w)/2, line_y),
               lb.message, font=font, fill=font_colour_title)
        line_y += line_height

        #d.text((line_x-(coll_padding), line_y), "|", font=font, fill=font_colour)

        #d.text((line_x, line_y), "Corp", font=font, fill=font_colour)
        line_x += ticker_width
        #d.text((line_x-(coll_padding), line_y), "|", font=font, fill=font_colour)

        _, _, _w, _ = font.getbbox("Total")
        d.text((line_x+((ticker_width-_w)/2), line_y),
               "Total", font=font, fill=font_colour_title)
        line_x += ticker_width
        #d.text((line_x-(coll_padding), line_y), "|", font=font, fill=font_colour)

        for t in LeaderBoardTypeThrough.objects.filter(LeaderBoard=lb).order_by("rank"):
            d.text((line_x, line_y), t.header,
                   font=font, fill=font_colour_title)
            line_x += type_widths[t.id]["w"] + coll_padding
            #d.text((line_x-(coll_padding), line_y), "|", font=font, fill=font_colour)

        line_x = 10
        line_y += line_height

        for corp in corporations:
            #d.text((line_x-(coll_padding), line_y), "|", font=font, fill=font_colour)

            d.text((line_x, line_y), corp, font=font, fill=font_colour_rest)
            line_x += ticker_width
            #d.text((line_x-(coll_padding), line_y), "|", font=font, fill=font_colour)

            fats = AFat.objects.filter(
                character__in=character_list.filter(
                    character_ownership__user__profile__main_character__corporation_ticker=corp),
                afatlink__afattime__gte=start_time
            ).count()
            _, _, _w, _ = font.getbbox(str(fats))

            d.text(
                (line_x+((ticker_width-_w)/2), line_y),
                str(fats),
                font=font,
                fill=font_colour_rest)
            line_x += ticker_width
            #d.text((line_x-(coll_padding), line_y), "|", font=font, fill=font_colour)

            for t in LeaderBoardTypeThrough.objects.filter(LeaderBoard=lb).order_by("rank"):
                fats = AFat.objects.filter(
                    character__in=character_list.filter(
                        character_ownership__user__profile__main_character__corporation_ticker=corp),
                    afatlink__afattime__gte=start_time,
                    afatlink__link_type=t.fatLinkType
                ).count()
                _, _, _w, _ = font.getbbox(str(fats))
                d.text((line_x+((type_widths[t.id]["w"]-_w)/2), line_y),
                       str(fats), font=font, fill=font_colour_rest)
                line_x += type_widths[t.id]["w"] + coll_padding
                #d.text((line_x-(coll_padding), line_y), "|", font=font, fill=font_colour)

            line_y += line_height
            line_x = 10
        s_date = start_time.strftime("%Y/%m/%d")
        e_date = timezone.now().strftime("%Y/%m/%d")
        stime_str = f"{s_date} - {e_date}"

        _, _, _w, _ = font.getbbox(stime_str)
        d.text(((total_width-_w)/2, line_y),
               stime_str, font=font, fill=font_colour_title)

        buf = io.BytesIO()
        img.save(buf, format='png')

        send_channel_message_by_discord_id.delay(
            channel_id, "", file=(buf.getvalue(), "test.png"))
