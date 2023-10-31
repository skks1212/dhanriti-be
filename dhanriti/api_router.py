from django.conf import settings
from django.http import JsonResponse
from django.urls import include, path
from rest_framework_nested import routers

from core.settings.base import AUTH_MODE
from dhanriti.tasks import discord_stats, email_tasks, update_count_tasks
from dhanriti.views.notes import NoteViewSet

from .views.auth import APICheckLoginView, APILoginView, APILogoutView
from .views.awards import AwardedViewSet, AwardViewSet
from .views.badges import AssignedBadgeViewSet, BadgeViewSet
from .views.comments import CommentViewSet
from .views.leaves import LeafViewSet
from .views.misc import (
    AssetViewSet,
    BetaInviteViewSet,
    EmailPresetViewSet,
    GeneratedStoryPartViewset,
    InviteViewSet,
    MotdViewSet,
    PresetViewSet,
)
from .views.notifications import NotificationViewSet
from .views.push_notifications import PushNotificationTokenViewSet
from .views.reports import ReportViewSet
from .views.searches import SearchHistoryViewSet, SearchViewSet
from .views.stories import StoryPartViewSet, StoryViewSet
from .views.upload import UploadViewSet
from .views.users import ShelfViewSet, UserViewSet

app_name = "api"

router = routers.SimpleRouter(trailing_slash=False)
NestedRouter = routers.NestedSimpleRouter
if settings.DEBUG:
    router = routers.DefaultRouter(trailing_slash=False)
    NestedRouter = routers.NestedDefaultRouter

router.register(r"users", UserViewSet)
router.register(r"notifications", NotificationViewSet)
router.register(r"reports", ReportViewSet)
router.register(r"stories", StoryViewSet)
router.register(r"leaves", LeafViewSet, basename="leaves")
router.register(r"notes", NoteViewSet)
router.register(r"upload", UploadViewSet, basename="upload")
router.register(
    r"pushnotificationtokens", PushNotificationTokenViewSet, basename="pushnotification"
)
router.register(r"search", SearchViewSet, basename="search")
router.register(r"badges", BadgeViewSet)
router.register(r"awards", AwardViewSet)
router.register(r"presets", PresetViewSet)
router.register(r"motd", MotdViewSet)
router.register(r"invites", InviteViewSet)
router.register(r"emailpresets", EmailPresetViewSet)
router.register(r"assets", AssetViewSet)
router.register(r"botstory", GeneratedStoryPartViewset, basename="botstory")

story_router = NestedRouter(router, r"stories", lookup="story")
story_router.register(r"parts", StoryPartViewSet, basename="story_parts")
story_router.register(r"awards", AwardedViewSet, basename="total_awards_in_story")

search_router = routers.SimpleRouter(trailing_slash=False)
search_router.register(
    r"search/history", SearchHistoryViewSet, basename="search-history"
)

story_part_router = NestedRouter(story_router, r"parts", lookup="story_part")
story_part_router.register(r"comments", CommentViewSet, basename="story_part_comments")

leaf_router = NestedRouter(router, r"leaves", lookup="leaf")
leaf_router.register(r"comments", CommentViewSet, basename="leaf_comments")

user_router = NestedRouter(router, r"users", lookup="user")
user_router.register(r"shelves", ShelfViewSet, basename="user_shelves")

auth_urls = [
    path("login", APILoginView.as_view(), name="login"),
    path("logout", APILogoutView.as_view(), name="logout"),
    path(
        "mode",
        lambda request: JsonResponse({"mode": AUTH_MODE}),
        name="hello",
    ),
]
router.register(r"auth/check", APICheckLoginView, basename="check")

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(search_router.urls)),
    path(
        "users/<str:username>/badges",
        AssignedBadgeViewSet.as_view({"get": "user_badges"}),
        name="user_badges",
    ),
    path(
        "parts/<str:part_url>/awards",
        AwardedViewSet.as_view({"get": "list"}),
        name="part_awards",
    ),
    path(
        "crons/updatecount/<str:cron_key>/",
        update_count_tasks.update_reads_claps_comments,
        name="updatecount",
    ),
    path(
        "crons/emailnotifications/<str:cron_key>/",
        email_tasks.email_notification,
        name="emailnotifications",
    ),
    path(
        "crons/resendmails/<str:cron_key>/",
        email_tasks.send_unsent_mails,
        name="resend_mails",
    ),
    path(
        "crons/dailydiscordstats/<str:cron_key>/",
        discord_stats.discord_webhook_daily,
        name="daily_discord_stats",
    ),
    path(
        "crons/weeklydiscordstats/<str:cron_key>/",
        discord_stats.discord_webhook_weekly,
        name="weekly_discord_stats",
    ),
    path(
        "crons/monthlydiscordstats/<str:cron_key>/",
        discord_stats.discord_webhook_monthly,
        name="monthly_discord_stats",
    ),
    path(
        "crons/usermilestone/<str:cron_key>/",
        discord_stats.user_milestone_hit,
        name="user_milestone",
    ),
    path(
        "beta/invite", BetaInviteViewSet.as_view({"post": "create"}), name="beta_invite"
    ),
    path(r"", include(story_router.urls)),
    path(r"", include(story_part_router.urls)),
    path(r"", include(user_router.urls)),
    path(r"", include(leaf_router.urls)),
    path("auth/", include(auth_urls)),
]
