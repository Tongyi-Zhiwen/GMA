from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from gma.apps.xiaoshiliu import XIAOSHILIU_LOGIN_USER_ID
from gma.assets import (
    DeviceFileAsset,
    ElementXMessageAsset,
    ElementXRoomAsset,
    ElementXUserAsset,
    ImageContentExpectation,
    MailAccountAsset,
    MailAttachment,
    MailMessageAsset,
    MastodonAccountAsset,
    MastodonFollowAsset,
    MastodonSessionAsset,
    MastodonStatusAsset,
    XiaoShiLiuCommentAsset,
    XiaoShiLiuPostAsset,
    XiaoShiLiuSessionAsset,
    XiaoShiLiuUserAsset,
)
from gma.evaluation import AssetExists
from gma.tasks.base import BaseTask


def dt_ms(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


MAIL_ACCOUNT = MailAccountAsset(display_name="Morgan Carter", email="morgan.carter@example.com")
OFFICIAL_NOTICE = """Riverfront Volunteer Fair official notice
Date: October 12, 2026
Start time: 10:30 AM
Location: Hall B
Signup rule: free signup closes October 10
Price: no fee
Organizer source: Riverfront Community Office"""
DRAFT_NOTICE = """Riverfront Volunteer Fair draft
Draft only: October 12 at 9:30 AM in Hall A with a $5 paid signup table closing October 9."""
USER_DRAFT_POST = """Saved public-post notes, not yet verified:
Riverfront Volunteer Fair is Oct 12 at 9:30 AM in Hall A. Bring $5 for signup before Oct 9.
Verify every detail against the final organizer notice before posting."""
NOTICE_FILE = "riverfront-briefing-oct1.txt"
OLDER_NOTE_FILE = "riverfront-table-notes.txt"
SAVED_POST_FILE = "riverfront-post-notes.txt"
DRAFT_FLYER_IMAGE = "riverfront_flyer_photo.png"

MASTODON_POST = (
    "Verified Riverfront Volunteer Fair update: Oct 12 at 10:30 AM in Hall B. "
    "Free signup closes Oct 10. Source: official organizer notice."
)
XSL_TITLE = "Verified Riverfront Volunteer Fair Update"
XSL_CONTENT = (
    "Official source check: the Riverfront Volunteer Fair is October 12, 2026 at "
    "10:30 AM in Hall B. Signup is free and closes October 10."
)
ELEMENTX_SUMMARY = (
    f"Verified from {NOTICE_FILE}: Oct 12, 2026 at 10:30 AM in Hall B; "
    "free signup closes Oct 10."
)


class CrossAppFactcheckPostTask(BaseTask):
    apps = {"Mastodon", "XiaoShiLiu", "Mail", "Files", "Gallery", "ElementX"}
    difficulty = "realistic"
    category = ['Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"

    assets = (
        MastodonSessionAsset(username="owner"),
        MastodonAccountAsset(username="river-rumor", email="river.rumor@example.com", display_name="River Rumor"),
        MastodonAccountAsset(username="hall-watch", email="hall.watch@example.com", display_name="Hall Watch"),
        MastodonAccountAsset(username="signup-board", email="signup.board@example.com", display_name="Signup Board"),
        MastodonAccountAsset(username="community-calendar", email="community.calendar@example.com", display_name="Community Calendar"),
        MastodonAccountAsset(username="eastbank-events", email="eastbank.events@example.com", display_name="Eastbank Events"),
        MastodonAccountAsset(username="volunteer-vibes", email="volunteer.vibes@example.com", display_name="Volunteer Vibes"),
        MastodonAccountAsset(username="campus-market", email="campus.market@example.com", display_name="Campus Market"),
        MastodonAccountAsset(username="old-flyer-archive", email="old.flyer.archive@example.com", display_name="Old Flyer Archive"),
        MastodonFollowAsset(follower_username="owner", followed_username="river-rumor"),
        MastodonFollowAsset(follower_username="owner", followed_username="hall-watch"),
        MastodonFollowAsset(follower_username="owner", followed_username="signup-board"),
        MastodonFollowAsset(follower_username="owner", followed_username="community-calendar"),
        MastodonFollowAsset(follower_username="owner", followed_username="eastbank-events"),
        MastodonFollowAsset(follower_username="owner", followed_username="volunteer-vibes"),
        MastodonFollowAsset(follower_username="owner", followed_username="campus-market"),
        MastodonFollowAsset(follower_username="owner", followed_username="old-flyer-archive"),
        MastodonStatusAsset(
            username="river-rumor",
            text=(
                "Riverfront Volunteer Fair is Oct 12 in Hall B, but the flyer photo I saw "
                "says the start is 9:30 AM. Can anyone verify the time?"
            ),
            visibility="public",
            created_at_ms=dt_ms(2026, 10, 1, 9, 0),
        ),
        MastodonStatusAsset(
            username="hall-watch",
            text=(
                "I heard Riverfront Volunteer Fair starts at 10:30 AM, but people keep saying "
                "it moved to Hall A this year instead of Hall B."
            ),
            visibility="public",
            created_at_ms=dt_ms(2026, 10, 1, 9, 15),
        ),
        MastodonStatusAsset(
            username="signup-board",
            text=(
                "Riverfront Volunteer Fair signup closes Oct 10, but a draft screenshot says "
                "there is a $5 paid signup table. Is the fair free or paid?"
            ),
            visibility="public",
            created_at_ms=dt_ms(2026, 10, 1, 9, 30),
        ),
        MastodonStatusAsset(
            username="community-calendar",
            text=(
                "Busy civic week: neighborhood cleanup is Oct 11 at Riverside Steps, and the "
                "Riverfront Volunteer Fair chatter says Oct 12. I am waiting for the organizer notice before updating our calendar."
            ),
            visibility="public",
            created_at_ms=dt_ms(2026, 10, 1, 9, 38),
        ),
        MastodonStatusAsset(
            username="eastbank-events",
            text=(
                "Eastbank volunteer orientation is Oct 12 at 9:30 AM in Hall A. People keep mixing "
                "it with the Riverfront fair posts, so double-check the event name before sharing."
            ),
            visibility="public",
            created_at_ms=dt_ms(2026, 10, 1, 9, 46),
        ),
        MastodonStatusAsset(
            username="volunteer-vibes",
            text=(
                "Someone mentioned a $5 donation jar for volunteer supplies. I cannot tell whether "
                "that is required signup money or just a separate table."
            ),
            visibility="public",
            created_at_ms=dt_ms(2026, 10, 1, 9, 54),
        ),
        MastodonStatusAsset(
            username="campus-market",
            text=(
                "Campus market reminder: Hall B vendor setup is Oct 10 at 10:30 AM, and vendor "
                "registration has a $5 table fee."
            ),
            visibility="public",
            created_at_ms=dt_ms(2026, 10, 1, 10, 2),
        ),
        MastodonStatusAsset(
            username="old-flyer-archive",
            text=(
                "Found an old Riverfront flyer in my photos: Hall A, 9:30 AM, signup by Oct 9. "
                "No idea whether this was the working copy or the final notice."
            ),
            visibility="public",
            created_at_ms=dt_ms(2026, 10, 1, 10, 8),
        ),
        XiaoShiLiuSessionAsset(user_id=XIAOSHILIU_LOGIN_USER_ID),
        XiaoShiLiuUserAsset(user_id="riverfront-helper", nickname="Riverfront Helper", email="riverfront.helper@example.com"),
        XiaoShiLiuUserAsset(user_id="campus-rumor", nickname="Campus Rumor", email="campus.rumor@example.com"),
        XiaoShiLiuPostAsset(
            author_user_id="riverfront-helper",
            title="Riverfront fair draft screenshot",
            content=(
                "This screenshot says the Riverfront Volunteer Fair is October 12, but it also "
                "claims Hall A, 9:30 AM, a $5 signup table, and an October 9 signup deadline. "
                "It looks like an old draft, so I would not repost it without the official notice."
            ),
            category="Campus Life",
            created_at_ms=dt_ms(2026, 10, 1, 10, 0),
        ),
        XiaoShiLiuPostAsset(
            author_user_id="campus-rumor",
            title="Riverfront fair signup question",
            content=(
                "Another volunteer thread says the fair starts at 10:30 AM and signup is free, "
                "but it still lists Hall A and says the deadline is October 9. We need the final "
                "organizer attachment before posting anything public."
            ),
            category="Campus Life",
            image_urls=[],
            created_at_ms=dt_ms(2026, 10, 1, 10, 20),
        ),
        XiaoShiLiuCommentAsset(
            post_title="Riverfront fair draft screenshot",
            post_author_user_id="riverfront-helper",
            author_user_id="campus-rumor",
            content="The date may be right, but the hall, time, fee, and deadline all need official confirmation.",
            created_at_ms=dt_ms(2026, 10, 1, 10, 10),
        ),
        XiaoShiLiuCommentAsset(
            post_title="Riverfront fair signup question",
            post_author_user_id="campus-rumor",
            author_user_id="riverfront-helper",
            content="The final notice should settle Hall A vs Hall B, Oct 9 vs Oct 10, and whether any fee exists.",
            created_at_ms=dt_ms(2026, 10, 1, 10, 25),
        ),
        MAIL_ACCOUNT,
        MailMessageAsset(
            mailbox="inbox",
            from_name="Riverfront Community Office",
            from_email="organizer@riverfront.example.com",
            to=[MAIL_ACCOUNT.email],
            subject="Riverfront Volunteer Fair organizer packet",
            body="Please use the attached organizer packet for public post details after checking it against the circulating posts.",
            attachments=[
                MailAttachment(
                    filename=NOTICE_FILE,
                    mime_type="text/plain",
                    text_content=OFFICIAL_NOTICE,
                )
            ],
            timestamp_ms=dt_ms(2026, 10, 1, 11, 0),
            read=False,
        ),
        DeviceFileAsset(
            app="Files",
            storage_dir="Download",
            filename=OLDER_NOTE_FILE,
            mime_type="text/plain",
            text_content=DRAFT_NOTICE,
        ),
        DeviceFileAsset(
            app="Files",
            storage_dir="Documents",
            filename=SAVED_POST_FILE,
            mime_type="text/plain",
            text_content=USER_DRAFT_POST,
        ),
        DeviceFileAsset(
            app="Gallery",
            storage_dir="Pictures",
            filename=DRAFT_FLYER_IMAGE,
            mime_type="image/png",
            source_path=f"assets/{DRAFT_FLYER_IMAGE}",
        ),
        ElementXUserAsset(username="factcheck-lead", password="password", display_name="Factcheck Lead"),
        ElementXRoomAsset(
            name="Riverfront Factcheck",
            room_type="group",
            creator_username="factcheck-lead",
            creator_password="password",
            members=["testuser"],
            alias_localpart="riverfront-factcheck",
        ),
        ElementXMessageAsset(
            room="riverfront-factcheck",
            sender_username="factcheck-lead",
            sender_password="password",
            text=(
                "Please fact-check the Riverfront Volunteer Fair claims across the social posts, "
                "the organizer email, and the related Files notes. People disagree on time, location, "
                "signup deadline, and whether there is a fee. Post public corrections and send "
                "me the verified source-backed summary."
            ),
            created_at_ms=dt_ms(2026, 10, 1, 11, 10),
        ),
    )

    goal = (
        "Please fact-check the Riverfront Volunteer Fair announcement people are discussing. Inspect Mastodon and XiaoShiLiu posts/comments to understand which details are disputed, then inspect or download the organizer email attachment to identify the authoritative organizer notice; use the related Files notes only as context. Use the authoritative notice date/time/location, not the draft posts. Use these date formats exactly: in the Mastodon post, write the event date and signup deadline as abbreviated Month D with no year, such as Sep 4 and Sep 2; in the XiaoShiLiu post, write the event date as full Month D, YYYY, such as September 4, 2026, and the signup deadline as full Month D, such as September 2; in the ElementX summary, write the event date as abbreviated Month D, YYYY, such as Sep 4, 2026, and the signup deadline as abbreviated Month D, such as Sep 2. Publish a public Mastodon update using the format: \'Verified Riverfront Volunteer Fair update: <date> at <time> in <location>. <signup rule>. Source: official organizer notice.\' Create a XiaoShiLiu post with category exactly \'Campus Life\', title exactly \'Verified Riverfront Volunteer Fair Update\', and attach the Riverfront draft flyer image from Gallery for context. Use content in the format: \'Official source check: the Riverfront Volunteer Fair is <date> at <time> in <location>. Signup is <fee status> and closes <deadline>.\' If XiaoShiLiu requires a tag to publish, use \'factcheck\'. Then send Riverfront Factcheck using the format: \'Verified from <organizer notice file>: <date> at <time> in <location>; <signup rule>.\'."
    )

    def criteria(self):
        return [
            AssetExists(MastodonStatusAsset(username="owner", text=MASTODON_POST, visibility="public"), task=self),
            AssetExists(
                XiaoShiLiuPostAsset(
                    author_user_id=XIAOSHILIU_LOGIN_USER_ID,
                    title=XSL_TITLE,
                    content=XSL_CONTENT,
                    category="Campus Life",
                    min_image_count=1,
                    expected_images=(
                        ImageContentExpectation(
                            filename=DRAFT_FLYER_IMAGE,
                            source_path=str(Path(__file__).with_name("assets") / DRAFT_FLYER_IMAGE),
                        ),
                    ),
                ),
                task=self,
            ),
            AssetExists(
                ElementXMessageAsset(
                    room="riverfront-factcheck",
                    sender_username="testuser",
                    sender_password="testpass123",
                    text=ELEMENTX_SUMMARY,
                ),
                task=self,
            ),
        ]
