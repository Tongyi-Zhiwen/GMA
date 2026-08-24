from __future__ import annotations

from datetime import UTC, datetime

from gma.apps.xiaoshiliu import XIAOSHILIU_DEFAULT_AVATAR
from gma.assets import (
    CalendarEventAsset,
    ContactAsset,
    ElementXMessageAsset,
    ElementXPollAsset,
    ElementXPollResponse,
    ElementXRoomAsset,
    ElementXUserAsset,
    SmsMessageAsset,
    TempusPlaylistAsset,
    XiaoShiLiuPostAsset,
    XiaoShiLiuUserAsset,
)
from gma.evaluation import AssetExists
from gma.tasks.base import BaseTask


def dt_ms(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


ROOM_ALIAS = "v2-11-study-group"
PLAYLIST_NAME = "Quiet Exam Focus"
TRACKS = ["The End of Asia", "Lights Go Out", "Tangerine Dreams"]
TRACK_ALBUMS = {"The End of Asia": "The End of Asia", "Lights Go Out": "Ego", "Tangerine Dreams": "Ego"}
FINAL_MESSAGE = (
    "Study plan is set: Biology review on October 2 from 4:00 PM to 5:30 PM, "
    "Calculus practice on October 4 from 10:00 AM to 11:30 AM, and Tempus playlist Quiet Exam Focus is ready."
)

MEMBERS = (
    ElementXUserAsset(username="v2-11-avery", password="password", display_name="Avery"),
    ElementXUserAsset(username="v2-11-blair", password="password", display_name="Blair"),
    ElementXUserAsset(username="v2-11-casey", password="password", display_name="Casey"),
)
ROOM = ElementXRoomAsset(
    name="Exam Study Group",
    room_type="group",
    creator_username="testuser",
    creator_password="testpass123",
    members=[member.username for member in MEMBERS],
    alias_localpart=ROOM_ALIAS,
    topic="Exam planning and focus playlist.",
)
PRIORITY_POLL = ElementXPollAsset(
    room=ROOM_ALIAS,
    sender_username="v2-11-avery",
    sender_password="password",
    question="Which subjects need group sessions before exams?",
    options=["Biology", "Calculus", "Literature"],
    responses=[
        ElementXPollResponse(username="v2-11-avery", option="Biology"),
        ElementXPollResponse(username="v2-11-blair", option="Calculus"),
        ElementXPollResponse(username="v2-11-casey", option="Biology"),
    ],
    created_at_ms=dt_ms(2026, 10, 1, 8, 30),
)
EXAM_MESSAGE = ElementXMessageAsset(
    room=ROOM_ALIAS,
    sender_username="v2-11-blair",
    sender_password="password",
    text="Biology exam is October 5 and Calculus is October 6. Literature can wait until later.",
    created_at_ms=dt_ms(2026, 10, 1, 8, 45),
)
WINDOW_MESSAGE = ElementXMessageAsset(
    room=ROOM_ALIAS,
    sender_username="v2-11-casey",
    sender_password="password",
    text="I can do Friday after 4 PM and Sunday morning, but late sessions are hard.",
    created_at_ms=dt_ms(2026, 10, 1, 9),
)
LITERATURE_MESSAGE = ElementXMessageAsset(
    room=ROOM_ALIAS,
    sender_username="v2-11-avery",
    sender_password="password",
    text="I can skim Literature on my own after the science exams; group time should go to the subjects from the poll.",
    created_at_ms=dt_ms(2026, 10, 1, 9, 5),
)
OPTIONAL_WINDOW_MESSAGE = ElementXMessageAsset(
    room=ROOM_ALIAS,
    sender_username="v2-11-blair",
    sender_password="password",
    text="Saturday afternoon is only a backup for extra reading. If the calendar is crowded, keep the main sessions Friday and Sunday.",
    created_at_ms=dt_ms(2026, 10, 1, 9, 10),
)
SESSION_LENGTH_MESSAGE = ElementXMessageAsset(
    room=ROOM_ALIAS,
    sender_username="v2-11-avery",
    sender_password="password",
    text="Let's keep each main study block to 90 minutes so there is enough time for review and practice without running late.",
    created_at_ms=dt_ms(2026, 10, 1, 9, 12),
)
PRIVATE_CONTACT = ContactAsset(name="Casey Study", phone_number="+15550121101")
PRIVATE_SMS = SmsMessageAsset(
    address=PRIVATE_CONTACT.phone_number,
    body="Please avoid late-night study blocks for me this week. On Sunday, I am not available after 11:30 AM.",
    box="inbox",
    read=True,
    timestamp_ms=dt_ms(2026, 10, 1, 9, 15),
)
XSL_USERS = (
    XiaoShiLiuUserAsset(user_id="v2-11-avery-music", nickname="Avery Focus", email="avery.focus@example.com", avatar=XIAOSHILIU_DEFAULT_AVATAR),
    XiaoShiLiuUserAsset(user_id="v2-11-blair-music", nickname="Blair Notes", email="blair.notes@example.com", avatar=XIAOSHILIU_DEFAULT_AVATAR),
)
XSL_POSTS = (
    XiaoShiLiuPostAsset(
        author_user_id="v2-11-avery-music",
        title="Instrumental Library Focus",
        content=(
            "Instrumental and lo-fi tracks help me focus; lyrics distract me during problem sets. "
            "I keep returning to the album The End of Asia, especially the title track, when I need a quiet anchor for exam review."
        ),
        category="Music",
        tags=["study", "instrumental"],
        created_at_ms=dt_ms(2026, 9, 30, 18),
    ),
    XiaoShiLiuPostAsset(
        author_user_id="v2-11-blair-music",
        title="Quiet Classical Study Mix",
        content=(
            "For exam review I prefer quiet acoustic or classical songs, not workout music. "
            "On Ego, Lights Go Out stays calm enough for reading, and Tangerine Dreams works for problem sets without pulling attention."
        ),
        category="Music",
        tags=["study", "quiet"],
        created_at_ms=dt_ms(2026, 9, 30, 19),
    ),
    XiaoShiLiuPostAsset(
        author_user_id="v2-11-blair-music",
        title="Workout Beats for Running",
        content="Fast workout beats are only for running, not for study sessions.",
        category="Music",
        tags=["workout"],
        created_at_ms=dt_ms(2026, 9, 29, 19),
    ),
    XiaoShiLiuPostAsset(
        author_user_id="v2-11-avery-music",
        title="Lyrics Take Over My Notes",
        content="Songs with big hooks or shouted vocals make me copy the chorus into the margin instead of finishing formulas; save those for breaks.",
        category="Music",
        tags=["study", "lyrics"],
        created_at_ms=dt_ms(2026, 9, 30, 17, 30),
    ),
    XiaoShiLiuPostAsset(
        author_user_id="v2-11-blair-music",
        title="Too Sleepy for Group Review",
        content="In the Dark is nice for a late walk, but for group study it feels too sleepy and lyrical. I still need calm focus, not a nap track.",
        category="Music",
        tags=["quiet", "evening"],
        created_at_ms=dt_ms(2026, 9, 30, 20),
    ),
    XiaoShiLiuPostAsset(
        author_user_id="v2-11-avery-music",
        title="Presentation Pump-Up Queue",
        content="For presentations I like faster tracks with a strong beat, but that energy is too much for exam problem sets.",
        category="Music",
        tags=["presentation", "energy"],
        created_at_ms=dt_ms(2026, 9, 29, 20),
    ),
)
CALENDAR_CONFLICTS = (
    CalendarEventAsset(title="Friday Lab", start_ms=dt_ms(2026, 10, 2, 14), end_ms=dt_ms(2026, 10, 2, 15, 30), timezone="UTC"),
    CalendarEventAsset(title="Saturday Volunteer Shift", start_ms=dt_ms(2026, 10, 3, 13), end_ms=dt_ms(2026, 10, 3, 16), timezone="UTC"),
    CalendarEventAsset(title="Sunday Family Breakfast", start_ms=dt_ms(2026, 10, 4, 8), end_ms=dt_ms(2026, 10, 4, 9, 30), timezone="UTC"),
    CalendarEventAsset(title="Sunday Library Commute", start_ms=dt_ms(2026, 10, 4, 9, 30), end_ms=dt_ms(2026, 10, 4, 10), timezone="UTC"),
)
EXPECTED_PLAYLIST = TempusPlaylistAsset(
    name=PLAYLIST_NAME,
    owner_username="testuserfjx",
    visibility="private",
    track_titles=TRACKS,
    track_albums=TRACK_ALBUMS,
)
BIOLOGY_EVENT = CalendarEventAsset(
    title="Biology Study Block",
    start_ms=dt_ms(2026, 10, 2, 16),
    end_ms=dt_ms(2026, 10, 2, 17, 30),
    description=f"Use Tempus playlist {PLAYLIST_NAME}.",
    timezone="UTC",
    reminder_minutes=(30,),
)
CALCULUS_EVENT = CalendarEventAsset(
    title="Calculus Study Block",
    start_ms=dt_ms(2026, 10, 4, 10),
    end_ms=dt_ms(2026, 10, 4, 11, 30),
    description=f"Use Tempus playlist {PLAYLIST_NAME}.",
    timezone="UTC",
    reminder_minutes=(30,),
)
EXPECTED_GROUP_MESSAGE = ElementXMessageAsset(
    room=ROOM_ALIAS,
    sender_username="testuser",
    sender_password="testpass123",
    text=FINAL_MESSAGE,
)


class StudyGroupPlaylistScheduleTask(BaseTask):
    apps = {"XiaoShiLiu", "Tempus", "ElementX", "Calendar", "Messages"}
    difficulty = "realistic"
    category = ['Selection / Optimization Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    assets = (
        *MEMBERS,
        ROOM,
        PRIORITY_POLL,
        EXAM_MESSAGE,
        WINDOW_MESSAGE,
        LITERATURE_MESSAGE,
        OPTIONAL_WINDOW_MESSAGE,
        SESSION_LENGTH_MESSAGE,
        PRIVATE_CONTACT,
        PRIVATE_SMS,
        *XSL_USERS,
        *XSL_POSTS,
        *CALENDAR_CONFLICTS,
    )
    goal = (
        "Please organize the study group plan from ElementX, XiaoShiLiu, Messages, Calendar, and Tempus. Use the ElementX poll result, group timing notes, session-length note, the private Messages availability constraint, and Calendar conflicts to select the subjects and feasible windows. "
        "Create a private Tempus playlist exactly named 'Quiet Exam Focus' and include every track explicitly supported by the quiet/instrumental study evidence in XiaoShiLiu; exclude lyrical, workout, high-energy, or sleepy distractor music. "
        "Add Calendar events titled '<Subject> Study Block' with description 'Use Tempus playlist Quiet Exam Focus.' and a 30-minute reminder. "
        "Send the ElementX group the final plan using exactly this format: 'Study plan is set: <subject one> review on <date> from <start> to <end>, <subject two> practice on <date> from <start> to <end>, and Tempus playlist Quiet Exam Focus is ready.'. Use date format like 'October 7' and time format like '4:00 PM'."
    )

    def criteria(self):
        return [
            AssetExists(EXPECTED_PLAYLIST, task=self),
            AssetExists(BIOLOGY_EVENT, task=self),
            AssetExists(CALCULUS_EVENT, task=self),
            AssetExists(EXPECTED_GROUP_MESSAGE, task=self),
        ]
