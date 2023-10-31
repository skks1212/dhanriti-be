import datetime
import json
import math

import requests
from celery import shared_task
from django.db import models
from django.http import HttpResponse, HttpResponseForbidden

from ..models import Follow, Leaf, Search, Story, StoryRead, User


def send_stats(payload):
    webhook_url = (
        "https://discord.com/api/webhooks/1154357598880026707"
        "/1bVRCGGoQtS2fZfPB2CWTe1L0zF3VbaL0dM9hacIA9dtSHSf1AD0KFSxxyLdvSbRmmiH"
    )

    response = requests.post(
        webhook_url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    print(response.status_code)


@shared_task
def discord_webhook_daily(request=None, cron_key=None):
    if cron_key and cron_key != "3z1OxJQuzkvKKw9ZJDWnZE8R8SuysN7ghdFzwk870UzLXB84ww":
        return HttpResponseForbidden("Incorrect password")

    if cron_key is None:
        pass

    daily_new_users = User.objects.filter(
        date_joined__date=datetime.date.today()
    ).count()
    try:
        percent_increase_users = round(
            (
                daily_new_users
                - User.objects.filter(
                    date_joined__date=datetime.date.today() - datetime.timedelta(days=1)
                ).count()
            )
            / User.objects.filter(
                date_joined__date=datetime.date.today() - datetime.timedelta(days=1)
            ).count()
            * 100,
            2,
        )
    except ZeroDivisionError:
        percent_increase_users = 0
    str_percent_increase_users = (
        str(percent_increase_users)
        if percent_increase_users < 0
        else "+" + str(percent_increase_users)
    )
    new_users_data = {
        "new_users": daily_new_users,
        "percent_increase": str_percent_increase_users,
    }

    daily_new_stories = Story.objects.filter(
        created_at__date=datetime.date.today()
    ).count()
    try:
        percent_increase_stories = round(
            (
                daily_new_stories
                - Story.objects.filter(
                    created_at__date=datetime.date.today() - datetime.timedelta(days=1)
                ).count()
            )
            / Story.objects.filter(
                created_at__date=datetime.date.today() - datetime.timedelta(days=1)
            ).count()
            * 100,
            2,
        )
    except ZeroDivisionError:
        percent_increase_stories = 0
    str_daily_new_stories_percent = (
        str(percent_increase_stories)
        if percent_increase_stories < 0
        else "+" + str(percent_increase_stories)
    )
    new_stories_data = {
        "new_stories": daily_new_stories,
        "percent_increase": str_daily_new_stories_percent,
    }

    daily_new_leaves = Leaf.objects.filter(
        created_at__date=datetime.date.today()
    ).count()
    try:
        percent_increase_leaves = round(
            (
                daily_new_leaves
                - Leaf.objects.filter(
                    created_at__date=datetime.date.today() - datetime.timedelta(days=1)
                ).count()
            )
            / Leaf.objects.filter(
                created_at__date=datetime.date.today() - datetime.timedelta(days=1)
            ).count()
            * 100,
            2,
        )
    except ZeroDivisionError:
        percent_increase_leaves = 0

    str_daily_new_leaves_percent = (
        str(percent_increase_leaves)
        if percent_increase_leaves < 0
        else "+" + str(percent_increase_leaves)
    )
    new_leaves_data = {
        "new_leaves": daily_new_leaves,
        "percent_increase": str_daily_new_leaves_percent,
    }

    daily_new_countries = (
        User.objects.filter(date_joined__date=datetime.date.today())
        .values_list("ip_country", flat=True)
        .distinct()
        .count()
    )
    country_with_most_users = (
        User.objects.values("ip_country")
        .annotate(country_count=models.Count("ip_country"))
        .order_by("-country_count")
        .first()
    )

    daily_active_users = User.objects.filter(
        last_online__date=datetime.date.today()
    ).count()
    increased_active_users = (
        daily_active_users
        - User.objects.filter(
            last_online__date=datetime.date.today() - datetime.timedelta(days=1)
        ).count()
    )
    try:
        percent_increase_active_users = round(
            (
                daily_active_users
                - User.objects.filter(
                    last_online__date=datetime.date.today() - datetime.timedelta(days=1)
                ).count()
            )
            / User.objects.filter(
                last_online__date=datetime.date.today() - datetime.timedelta(days=1)
            ).count()
            * 100,
            2,
        )
    except ZeroDivisionError:
        percent_increase_active_users = 0
    str_percent_increase_active_users = (
        str(percent_increase_active_users)
        if percent_increase_active_users < 0
        else "+" + str(percent_increase_active_users)
    )
    active_users_data = {
        "active_users": daily_active_users,
        "increased_active_users": increased_active_users,
        "percent_increase": str_percent_increase_active_users,
    }

    daily_most_read_story = (
        StoryRead.objects.filter(created_at__date=datetime.date.today())
        .values("part__story")
        .annotate(story_count=models.Count("part__story"))
        .order_by("-story_count")
        .first()
    )
    story = (
        Story.objects.get(id=daily_most_read_story["part__story"])
        if daily_most_read_story
        else None
    )
    trending_story_details = {
        "title": story.title if story else "[No story read today]",
        "new_reads": StoryRead.objects.filter(
            part__story=story, created_at__date=datetime.date.today()
        ).count()
        if story
        else "NAN",
        "total_reads": story.reads if story else "NA",
    }
    print(trending_story_details)

    most_searched_query_daily = (
        Search.objects.filter(created_at__date=datetime.date.today())
        .values("query")
        .annotate(query_count=models.Count("query"))
        .order_by("-query_count")
        .first()
    )
    most_searched_query = {
        "query": most_searched_query_daily["query"]
        if most_searched_query_daily
        else "[No searches today]",
        "query_count": most_searched_query_daily["query_count"]
        if most_searched_query_daily
        else 0,
    }

    daily_most_followed_user = (
        Follow.objects.filter(created_at__date=datetime.date.today())
        .values("followed")
        .annotate(followed_count=models.Count("followed"))
        .order_by("-followed_count")
        .first()
    )
    user = (
        User.objects.get(id=daily_most_followed_user["followed"])
        if daily_most_followed_user
        else None
    )
    user_details = {
        "username": user.username if user else "[No users followed today]",
        "new_followers": Follow.objects.filter(
            followed=user, created_at__date=datetime.date.today()
        ).count()
        if user
        else "NA",
        "followers": user.followers.count() if user else "NA",
    }

    payload = {
        "content": f"📢 **Daily Statistics Report** *{datetime.datetime.now().strftime('%d/%m/%Y')}*\n\n👥   **{User.objects.count()}** total users\n         {'🔴 ' if new_users_data['percent_increase'][0]=='-' else '🟢'} "
        f"*{new_users_data['new_users']} ({new_users_data['percent_increase']}%) from yesterday*\n\n📚    **{Story.objects.count()}** stories \n          {'🔴 ' if new_stories_data['percent_increase'][0]=='-' else '🟢'}️ *{new_stories_data['new_stories']} ({new_stories_data['percent_increase']}%) from "
        f"yesterday*\n\n🍃    **{Leaf.objects.count()}** leaves\n         {'🔴 ' if new_leaves_data['percent_increase'][0]=='-' else '🟢'} *{new_leaves_data['new_leaves']} ({new_leaves_data['percent_increase']}%) from yesterday*\n\n🌏    **{daily_new_countries}** countries conquered\n          ***{country_with_most_users['ip_country']}** in the lead with "
        f"**{country_with_most_users['country_count']}** users*\n\n👨‍💻   **{active_users_data['active_users']}** users active yesterday\n          {'🔴 ' if active_users_data['percent_increase'][0]=='-' else '🟢'}️ *{active_users_data['increased_active_users']} ({active_users_data['percent_increase']}%) from day before "
        f"yesterday*\n\n🔥   **{trending_story_details['title']}** is the most read story for the day\n         "
        f"*Gained **{trending_story_details['new_reads']}** reads, totaling to **{trending_story_details['total_reads']}** reads*\n\n🔎   **{most_searched_query['query']}** was the most "
        f"searched term for the day\n         *Was searched **{most_searched_query['query_count']}** times*\n\n👤   **{user_details['username']}** was the most "
        f"followed user yesterday.\n         *Gained **{user_details['new_followers']}** users, totalling to **{user_details['followers']}***",
        "embeds": None,
        "username": "Statistics",
        "avatar_url": "https://cdn.dhanriti.net/media/a784cbbf-98e9-4c23-be1c-20a106f3efeb_200.png",
        "attachments": [],
    }

    send_stats(
        payload,
    )

    return HttpResponse("Executed")


@shared_task
def discord_webhook_weekly(request=None, cron_key=None):
    if cron_key and cron_key != "3z1OxJQuzkvKKw9ZJDWnZE8R8SuysN7ghdFzwk870UzLXB84ww":
        return HttpResponseForbidden("Incorrect password")

    if cron_key is None:
        pass

    weekly_new_users = User.objects.filter(
        date_joined__gte=datetime.date.today() - datetime.timedelta(days=7)
    ).count()
    try:
        percent_increase_users = round(
            (
                weekly_new_users
                - User.objects.filter(
                    date_joined__gte=datetime.date.today() - datetime.timedelta(days=14)
                ).count()
            )
            / User.objects.filter(
                date_joined__gte=datetime.date.today() - datetime.timedelta(days=14)
            ).count()
            * 100,
            2,
        )
    except ZeroDivisionError:
        percent_increase_users = 0
    str_percent_increase_users = (
        str(percent_increase_users)
        if percent_increase_users < 0
        else "+" + str(percent_increase_users)
    )
    new_users_data = {
        "new_users": weekly_new_users,
        "percent_increase": str_percent_increase_users,
    }

    weekly_new_stories = Story.objects.filter(
        created_at__gte=datetime.date.today() - datetime.timedelta(days=7)
    ).count()
    try:
        percent_increase_stories = round(
            (
                weekly_new_stories
                - Story.objects.filter(
                    created_at__gte=datetime.date.today() - datetime.timedelta(days=14)
                ).count()
            )
            / Story.objects.filter(
                created_at__gte=datetime.date.today() - datetime.timedelta(days=14)
            ).count()
            * 100,
            2,
        )
    except ZeroDivisionError:
        percent_increase_stories = 0
    str_percent_increase_stories = (
        str(percent_increase_stories)
        if percent_increase_stories < 0
        else "+" + str(percent_increase_stories)
    )
    new_stories_data = {
        "new_stories": weekly_new_stories,
        "percent_increase": str_percent_increase_stories,
    }

    weekly_new_leaves = Leaf.objects.filter(
        created_at__gte=datetime.date.today() - datetime.timedelta(days=7)
    ).count()
    try:
        percent_increase_leaves = round(
            (
                weekly_new_leaves
                - Leaf.objects.filter(
                    created_at__gte=datetime.date.today() - datetime.timedelta(days=14)
                ).count()
            )
            / Leaf.objects.filter(
                created_at__gte=datetime.date.today() - datetime.timedelta(days=14)
            ).count()
            * 100,
            2,
        )
    except ZeroDivisionError:
        percent_increase_leaves = 0

    str_percent_increase_leaves = (
        str(percent_increase_leaves)
        if percent_increase_leaves < 0
        else "+" + str(percent_increase_leaves)
    )
    new_leaves_data = {
        "new_leaves": weekly_new_leaves,
        "percent_increase": str_percent_increase_leaves,
    }

    weekly_new_countries = (
        User.objects.filter(
            date_joined__gte=datetime.date.today() - datetime.timedelta(days=7)
        )
        .values_list("ip_country", flat=True)
        .distinct()
        .count()
    )
    country_with_most_users = (
        User.objects.values("ip_country")
        .annotate(country_count=models.Count("ip_country"))
        .order_by("-country_count")
        .first()
    )

    weekly_active_users = User.objects.filter(
        last_online__gte=datetime.date.today() - datetime.timedelta(days=7)
    ).count()
    increased_active_users = (
        weekly_active_users
        - User.objects.filter(
            last_online__gte=datetime.date.today() - datetime.timedelta(days=14)
        ).count()
    )
    try:
        percent_increase_active_users = round(
            (
                weekly_active_users
                - User.objects.filter(
                    last_online__gte=datetime.date.today() - datetime.timedelta(days=14)
                ).count()
            )
            / User.objects.filter(
                last_online__gte=datetime.date.today() - datetime.timedelta(days=14)
            ).count()
            * 100,
            2,
        )
    except ZeroDivisionError:
        percent_increase_active_users = 0
    str_percent_increase_active_users = (
        str(percent_increase_active_users)
        if percent_increase_active_users < 0
        else "+" + str(percent_increase_active_users)
    )
    active_users_data = {
        "active_users": weekly_active_users,
        "increased_active_users": increased_active_users,
        "percent_increase": str_percent_increase_active_users,
    }

    weekly_most_read_story = (
        StoryRead.objects.filter(
            created_at__gte=datetime.date.today() - datetime.timedelta(days=7)
        )
        .values("part__story")
        .annotate(story_count=models.Count("part__story"))
        .order_by("-story_count")
        .first()
    )
    story = (
        Story.objects.get(id=weekly_most_read_story["part__story"])
        if weekly_most_read_story
        else None
    )
    trending_story_details = {
        "title": story.title if story else "[No story read this week]",
        "new_reads": StoryRead.objects.filter(
            part__story=story,
            created_at__gte=datetime.date.today() - datetime.timedelta(days=7),
        ).count()
        if story
        else "NA",
        "total_reads": story.reads if story else "NA",
    }
    print(trending_story_details)

    most_searched_query_weekly = (
        Search.objects.filter(
            created_at__gte=datetime.date.today() - datetime.timedelta(days=7)
        )
        .values("query")
        .annotate(query_count=models.Count("query"))
        .order_by("-query_count")
        .first()
    )
    most_searched_query = {
        "query": most_searched_query_weekly["query"]
        if most_searched_query_weekly
        else "[No searches this week]",
        "query_count": most_searched_query_weekly["query_count"]
        if most_searched_query_weekly
        else 0,
    }

    weekly_most_followed_user = (
        Follow.objects.filter(
            created_at__gte=datetime.date.today() - datetime.timedelta(days=7)
        )
        .values("followed")
        .annotate(followed_count=models.Count("followed"))
        .order_by("-followed_count")
        .first()
    )
    user = (
        User.objects.get(id=weekly_most_followed_user["followed"])
        if weekly_most_followed_user
        else None
    )
    user_details = {
        "username": user.username if user else "[No users followed this week]",
        "new_followers": Follow.objects.filter(
            followed=user,
            created_at__gte=datetime.date.today() - datetime.timedelta(days=7),
        ).count()
        if user
        else "NA",
        "followers": user.followers.count() if user else "NA",
    }

    payload = {
        "content": f"📢 **Weekly Statistics Report** *{datetime.datetime.now().strftime('%d/%m/%Y')}*\n\n👥   **{User.objects.count()}** total users\n         {'🔴 ' if new_users_data['percent_increase'][0]=='-' else '🟢'} "
        f"*{new_users_data['new_users']} ({new_users_data['percent_increase']}%) from last week*\n\n📚    **{Story.objects.count()}** stories \n          {'🔴 ' if new_stories_data['percent_increase'][0]=='-' else '🟢'} *{new_stories_data['new_stories']} ({new_stories_data['percent_increase']}%) from "
        f"last week*\n\n🍃    **{Leaf.objects.count()}** leaves\n         {'🔴 ' if new_leaves_data['percent_increase'][0]=='-' else '🟢'} *{new_leaves_data['new_leaves']} ({new_leaves_data['percent_increase']}%) from last week*\n\n🌏    **{weekly_new_countries}** countries conquered\n          ***{country_with_most_users['ip_country']}** in the lead with "
        f"**{country_with_most_users['country_count']}** users*\n\n👨‍💻   **{active_users_data['active_users']}** users active this week\n          {'🔴 ' if active_users_data['percent_increase'][0]=='-' else '🟢'} *{active_users_data['increased_active_users']} ({active_users_data['percent_increase']}%) from last "
        f"week\n\n🔥   **{trending_story_details['title']}** is the most read story for the week\n         "
        f"*Gained **{trending_story_details['new_reads']}** reads, totaling to **{trending_story_details['total_reads']}** reads*\n\n🔎   **{most_searched_query['query']}** was the most "
        f"searched term for the week\n         *Was searched **{most_searched_query['query_count']}** times*\n\n👤   **{user_details['username']}** was the most "
        f"followed user this week.\n         *Gained **{user_details['new_followers']}** users, totalling to **{user_details['followers']}***",
        "embeds": None,
        "username": "Statistics",
        "avatar_url": "https://cdn.dhanriti.net/media/a784cbbf-98e9-4c23-be1c-20a106f3efeb_200.png",
        "attachments": [],
    }

    send_stats(payload)

    return HttpResponse("Executed")


@shared_task
def discord_webhook_monthly(request=None, cron_key=None):
    if cron_key and cron_key != "3z1OxJQuzkvKKw9ZJDWnZE8R8SuysN7ghdFzwk870UzLXB84ww":
        return HttpResponseForbidden("Incorrect password")

    if cron_key is None:
        pass

    monthly_new_users = User.objects.filter(
        date_joined__gte=datetime.date.today() - datetime.timedelta(days=30)
    ).count()
    try:
        percent_increase_users = round(
            (
                monthly_new_users
                - User.objects.filter(
                    date_joined__gte=datetime.date.today() - datetime.timedelta(days=60)
                ).count()
            )
            / User.objects.filter(
                date_joined__gte=datetime.date.today() - datetime.timedelta(days=60)
            ).count()
            * 100,
            2,
        )
    except ZeroDivisionError:
        percent_increase_users = 0
    str_percent_increase_users = (
        str(percent_increase_users)
        if percent_increase_users < 0
        else "+" + str(percent_increase_users)
    )
    new_users_data = {
        "new_users": monthly_new_users,
        "percent_increase": str_percent_increase_users,
    }

    monthly_new_stories = Story.objects.filter(
        created_at__gte=datetime.date.today() - datetime.timedelta(days=30)
    ).count()
    try:
        percent_increase_stories = round(
            (
                monthly_new_stories
                - Story.objects.filter(
                    created_at__gte=datetime.date.today() - datetime.timedelta(days=60)
                ).count()
            )
            / Story.objects.filter(
                created_at__gte=datetime.date.today() - datetime.timedelta(days=60)
            ).count()
            * 100,
            2,
        )
    except ZeroDivisionError:
        percent_increase_stories = 0
    str_percent_increase_stories = (
        str(percent_increase_stories)
        if percent_increase_stories < 0
        else "+" + str(percent_increase_stories)
    )
    new_stories_data = {
        "new_stories": monthly_new_stories,
        "percent_increase": str_percent_increase_stories,
    }

    monthly_new_leaves = Leaf.objects.filter(
        created_at__gte=datetime.date.today() - datetime.timedelta(days=30)
    ).count()
    try:
        percent_increase_leaves = round(
            (
                monthly_new_leaves
                - Leaf.objects.filter(
                    created_at__gte=datetime.date.today() - datetime.timedelta(days=60)
                ).count()
            )
            / Leaf.objects.filter(
                created_at__gte=datetime.date.today() - datetime.timedelta(days=60)
            ).count()
            * 100,
            2,
        )
    except ZeroDivisionError:
        percent_increase_leaves = 0
    str_percent_increase_leaves = (
        str(percent_increase_leaves)
        if percent_increase_leaves < 0
        else "+" + str(percent_increase_leaves)
    )
    new_leaves_data = {
        "new_leaves": monthly_new_leaves,
        "percent_increase": str_percent_increase_leaves,
    }

    monthly_new_countries = (
        User.objects.filter(
            date_joined__gte=datetime.date.today() - datetime.timedelta(days=30)
        )
        .values_list("ip_country", flat=True)
        .distinct()
        .count()
    )
    country_with_most_users = (
        User.objects.values("ip_country")
        .annotate(country_count=models.Count("ip_country"))
        .order_by("-country_count")
        .first()
    )

    monthly_active_users = User.objects.filter(
        last_online__gte=datetime.date.today() - datetime.timedelta(days=30)
    ).count()
    increased_active_users = (
        monthly_active_users
        - User.objects.filter(
            last_online__gte=datetime.date.today() - datetime.timedelta(days=60)
        ).count()
    )
    try:
        percent_increase_active_users = round(
            (
                monthly_active_users
                - User.objects.filter(
                    last_online__gte=datetime.date.today() - datetime.timedelta(days=60)
                ).count()
            )
            / User.objects.filter(
                last_online__gte=datetime.date.today() - datetime.timedelta(days=60)
            ).count()
            * 100,
            2,
        )
    except ZeroDivisionError:
        percent_increase_active_users = 0
    str_percent_increase_active_users = (
        str(percent_increase_active_users)
        if percent_increase_active_users < 0
        else "+" + str(percent_increase_active_users)
    )
    active_users_data = {
        "active_users": monthly_active_users,
        "increased_active_users": increased_active_users,
        "percent_increase": str_percent_increase_active_users,
    }

    monthly_most_read_story = (
        StoryRead.objects.filter(
            created_at__gte=datetime.date.today() - datetime.timedelta(days=30)
        )
        .values("part__story")
        .annotate(story_count=models.Count("part__story"))
        .order_by("-story_count")
        .first()
    )
    story = (
        Story.objects.get(id=monthly_most_read_story["part__story"])
        if monthly_most_read_story
        else None
    )
    trending_story_details = {
        "title": story.title if story else "[No story read this month]",
        "new_reads": StoryRead.objects.filter(
            part__story=story,
            created_at__gte=datetime.date.today() - datetime.timedelta(days=30),
        ).count()
        if story
        else "NA",
        "total_reads": story.reads if story else "NA",
    }

    most_searched_query_monthly = (
        Search.objects.filter(
            created_at__gte=datetime.date.today() - datetime.timedelta(days=30)
        )
        .values("query")
        .annotate(query_count=models.Count("query"))
        .order_by("-query_count")
        .first()
    )
    most_searched_query = {
        "query": most_searched_query_monthly["query"]
        if most_searched_query_monthly
        else "[No searches this month]",
        "query_count": most_searched_query_monthly["query_count"]
        if most_searched_query_monthly
        else 0,
    }

    monthly_most_followed_user = (
        Follow.objects.filter(
            created_at__gte=datetime.date.today() - datetime.timedelta(days=30)
        )
        .values("followed")
        .annotate(followed_count=models.Count("followed"))
        .order_by("-followed_count")
        .first()
    )
    user = (
        User.objects.get(id=monthly_most_followed_user["followed"])
        if monthly_most_followed_user
        else None
    )
    user_details = {
        "username": user.username if user else "[No users followed this month]",
        "new_followers": Follow.objects.filter(
            followed=user,
            created_at__gte=datetime.date.today() - datetime.timedelta(days=30),
        ).count()
        if user
        else "NA",
        "followers": user.followers.count() if user else "NA",
    }

    payload = {
        "content": f"📢 **Monthly Statistics Report** *{datetime.datetime.now().strftime('%d/%m/%Y')}*\n\n👥   **{User.objects.count()}** total users\n         {'🔴 ' if new_users_data['percent_increase'][0]=='-' else '🟢'}️ "
        f"*{new_users_data['new_users']} ({new_users_data['percent_increase']}%) from last month*\n\n📚    **{Story.objects.count()}** stories \n          {'🔴 ' if new_stories_data['percent_increase'][0]=='-' else '🟢'} *{new_stories_data['new_stories']} ({new_stories_data['percent_increase']}%) from "
        f"last month*\n\n{'🔴 ' if new_leaves_data['percent_increase'][0]=='-' else '🟢'}    **{Leaf.objects.count()}** leaves\n         ⬆️ *{new_leaves_data['new_leaves']} ({new_leaves_data['percent_increase']}%) from last month*\n\n🌏    **{monthly_new_countries}** countries conquered\n          ***{country_with_most_users['ip_country']}** in the lead with "
        f"**{country_with_most_users['country_count']}** users*\n\n👨‍💻   **{active_users_data['active_users']}** users active this month\n          {'🔴 ' if active_users_data['percent_increase'][0]=='-' else '🟢'} *{active_users_data['increased_active_users']} ({active_users_data['percent_increase']}%) from last "
        f"month\n\n🔥   **{trending_story_details['title']}** is the most read story for the month\n         "
        f"*Gained **{trending_story_details['new_reads']}** reads, totaling to **{trending_story_details['total_reads']}** reads*\n\n🔎   **{most_searched_query['query']}** was the most "
        f"searched term for the month\n         *Was searched **{most_searched_query['query_count']}** times*\n\n👤   **{user_details['username']}** was the most "
        f"followed user this month.\n         *Gained **{user_details['new_followers']}** users, totalling to **{user_details['followers']}***",
        "embeds": None,
        "username": "Statistics",
        "avatar_url": "https://cdn.dhanriti.net/media/a784cbbf-98e9-4c23-be1c-20a106f3efeb_200.png",
        "attachments": [],
    }

    send_stats(payload)

    return HttpResponse("Executed")


@shared_task
def user_milestone_hit(request=None, cron_key=None):
    if cron_key and cron_key != "3z1OxJQuzkvKKw9ZJDWnZE8R8SuysN7ghdFzwk870UzLXB84ww":
        return HttpResponseForbidden("Incorrect password")

    if cron_key is None:
        pass

    count = User.objects.count()
    if math.log10(count).is_integer():
        payload = {
            "content": f"📢 **User Milestone Hit** *{datetime.datetime.now().strftime('%d/%m/%Y')}*\n\n👥   **{count}** users",
            "embeds": None,
            "username": "Statistics",
            "avatar_url": "https://cdn.dhanriti.net/media/a784cbbf-98e9-4c23-be1c-20a106f3efeb_200.png",
            "attachments": [],
        }

        send_stats(payload)
