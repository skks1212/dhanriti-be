from django.db.models import IntegerChoices
from django.utils.translation import gettext_lazy as _  # noqa: F401


class NotificationType(IntegerChoices):
    STORY_VIEWS_MILESTONE = 1
    LEAF_VIEWS_MILESTONE = 2
    CLAP_MILESTONE = 3
    COMMENT = 4
    FOLLOW = 5
    COMMENT_REPLY = 6
    PART_PUBLISH = 7
    CLAP = 8
    COMMENT_LIKE = 9
    REPORT_JUDGEMENT = 10


class ReportType(IntegerChoices):
    STORY = 1
    STORY_COMMENT = 2
    PART = 3
    LEAF = 4
    LEAF_COMMENT = 5
    USER = 6
    SHELF = 7


class GenreType(IntegerChoices):
    SCIENCE_FICTION = 1
    FANTASY = 2
    POETRY = 3
    FANFICTION = 4
    GENERAL_FICTION = 5
    ADVENTURE = 6
    TEEN_FICTION = 7
    HUMOUR = 8
    FOLKTALE = 9
    MYTHOLOGY = 10
    ROMANCE = 11
    MYSTERY_THRILLER = 12
    RANDOM = 13
    HORROR = 14


class VisibilityType(IntegerChoices):
    PRIVATE = 1
    UNLISTED = 2
    PUBLIC = 3


class UploadType(IntegerChoices):
    PROFILE_PICTURE = 1
    BACKDROP = 2
    STORY_COVER = 3
    STORY_CONTENT = 4
    BADGE_ICON = 5
    AWARD_ICON = 6
    LEAF_BACKGROUND = 7
    LEAF = 8
    ASSET = 9


class PresetType(IntegerChoices):
    LEAF_BACKGROUND = 1
    LEAF_FONTS = 2
    THEME = 3
    THEME_FONTS = 4


class RarityType(IntegerChoices):
    COMMON = 1
    RARE = 2
    Prestigious = 3
    LEGENDARY = 4
