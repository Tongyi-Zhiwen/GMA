from __future__ import annotations

from datetime import UTC, datetime

from gma.apps.xiaoshiliu import XIAOSHILIU_DEFAULT_AVATAR, XIAOSHILIU_LOGIN_USER_ID
from gma.assets import (
    ContactAsset,
    ElementXMessageAsset,
    ElementXRoomAsset,
    ElementXSessionAsset,
    ElementXUserAsset,
    MailAccountAsset,
    MailMessageAsset,
    MastodonSessionAsset,
    MastodonStatusAsset,
    SmsMessageAsset,
    XiaoShiLiuCommentAsset,
    XiaoShiLiuPostAsset,
    XiaoShiLiuSessionAsset,
    XiaoShiLiuUserAsset,
)
from gma.evaluation import AssetExists, AssetModified
from gma.tasks.base import BaseTask


def utc_ms(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


RIDE_ROOM_ALIAS = "v2-18-weekend-ride-board"
VOLUNTEER_ROOM_ALIAS = "v2-18-volunteer-bench"
SWAP_ROOM_ALIAS = "v2-18-swap-rides"
POST_TITLE = "Community Repair Fair Details"
MASTODON_BEFORE_TEXT = "Community repair fair is Saturday at 10:00 AM in North Hall. Registration link still works."
MASTODON_AFTER_TEXT = "Community repair fair is Sunday at 1:00 PM in East Library Room 204. Registration link still works."
XSL_BEFORE_CONTENT = "The community repair fair is Saturday at 10:00 AM in North Hall. Bring small electronics. Registration link still works."
XSL_AFTER_CONTENT = "The community repair fair is Sunday at 1:00 PM in East Library Room 204. Bring small electronics. Registration link still works."
GROUP_UPDATE = "Ride update: the repair fair moved to Sunday at 1:00 PM in East Library Room 204. Please switch pickup planning to East Library."
DIRECT_REPLY = "The original plan changed: the repair fair is now Sunday at 1:00 PM in East Library Room 204. Registration is still valid."
XSL_REPLY = "Correction: the fair is now Sunday at 1:00 PM in East Library Room 204."
CLARIFY_COMMENT = "Is the Saturday North Hall info still correct? I am arranging pickup around that."


class SocialModerationCleanupTask(BaseTask):
    apps = {"Mastodon", "XiaoShiLiu", "ElementX", "Messages", "Mail"}
    difficulty = "realistic"
    category = ["Multi-Step Workflow Tasks"]
    snapshot = "gma_ready_state"
    max_steps = 180

    account = MailAccountAsset(display_name="Repair Fair Volunteer", email="repair.fair.volunteer@example.com")

    logistics_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Repair Fair Organizer",
        from_email="organizer@repairfair.example",
        to=[account.email],
        subject="Repair fair logistics after library confirmation",
        body=(
            "Hi volunteers, final host note for the community repair fair: we are using Sunday 1 PM in East Library Room 204. "
            "The earlier Saturday 10:00 AM North Hall flyer went out before the library confirmed space. Registration links remain valid, "
            "and attendee guidance is still to bring small electronics. Please adjust public notes that still send guests to the Saturday/North Hall plan "
            "and keep ride planning pointed to East Library."
        ),
        timestamp_ms=utc_ms(2026, 10, 1, 8),
        read=False,
    )
    registration_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Repair Fair Organizer",
        from_email="organizer@repairfair.example",
        to=[account.email],
        subject="Registration desk and waivers",
        body="Registration links remain active through Friday. Printed waiver forms will be at the desk for walk-ins.",
        timestamp_ms=utc_ms(2026, 9, 29, 8),
        read=True,
    )
    toolkit_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Repair Fair Organizer",
        from_email="organizer@repairfair.example",
        to=[account.email],
        subject="Volunteer toolkit packing note",
        body="Bring label tape, two small screwdrivers, USB-C testers, and the shared battery meter if you have it.",
        timestamp_ms=utc_ms(2026, 9, 30, 12),
        read=True,
    )
    seed_swap_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Campus Garden Club",
        from_email="garden@example.com",
        to=[account.email],
        subject="Seed swap remains in North Hall",
        body="The campus seed swap is still Saturday at 10:00 AM in North Hall. This is separate from repair fair volunteer logistics.",
        timestamp_ms=utc_ms(2026, 10, 1, 7, 45),
        read=False,
    )
    library_av_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Library AV Desk",
        from_email="avdesk@example.com",
        to=[account.email],
        subject="East Library Room 204 display cart",
        body="Room 204 has the display cart and power strips. The east entrance will be open for event setup after noon on Sunday.",
        timestamp_ms=utc_ms(2026, 10, 1, 8, 20),
        read=False,
    )

    mastodon_session = MastodonSessionAsset(username="owner")
    mastodon_before = MastodonStatusAsset(username="owner", text=MASTODON_BEFORE_TEXT, visibility="public", created_at_ms=utc_ms(2026, 9, 30, 10))
    mastodon_after = MastodonStatusAsset(username="owner", text=MASTODON_AFTER_TEXT, visibility="public")
    mastodon_registration_note = MastodonStatusAsset(username="owner", text="Repair fair registration link still works, and small electronics are welcome.", visibility="public", created_at_ms=utc_ms(2026, 9, 30, 10, 8))
    mastodon_toolkit_note = MastodonStatusAsset(username="owner", text="Volunteer toolkit packing list: label tape, small screwdrivers, battery meter, and spare USB-C cables.", visibility="public", created_at_ms=utc_ms(2026, 9, 30, 13))
    mastodon_seed_swap = MastodonStatusAsset(username="owner", text="Campus seed swap is Saturday at 10:00 AM in North Hall. Bring labeled seedlings and extra envelopes.", visibility="public", created_at_ms=utc_ms(2026, 10, 1, 7, 50))
    mastodon_library_note = MastodonStatusAsset(username="librarydesk", text="East Library Room 204 has extra power strips this weekend for scheduled groups.", visibility="public", created_at_ms=utc_ms(2026, 10, 1, 8, 40))

    xsl_commenter = XiaoShiLiuUserAsset(user_id="v2-18-commenter", password="123456", nickname="Repair Fair Attendee", email="repair.attendee@example.com", avatar=XIAOSHILIU_DEFAULT_AVATAR)
    xsl_registration_user = XiaoShiLiuUserAsset(user_id="v2-18-reg-question", password="123456", nickname="Signup Checker", email="repair.signup@example.com", avatar=XIAOSHILIU_DEFAULT_AVATAR)
    xsl_tools_user = XiaoShiLiuUserAsset(user_id="v2-18-tools", password="123456", nickname="Tool Helper", email="repair.tools@example.com", avatar=XIAOSHILIU_DEFAULT_AVATAR)
    xsl_swap_user = XiaoShiLiuUserAsset(user_id="v2-18-swap", password="123456", nickname="Garden Swapper", email="garden.swapper@example.com", avatar=XIAOSHILIU_DEFAULT_AVATAR)
    xsl_before = XiaoShiLiuPostAsset(
        author_user_id=XIAOSHILIU_LOGIN_USER_ID,
        title=POST_TITLE,
        content=XSL_BEFORE_CONTENT,
        category="Campus Life",
        tags=["repair fair", "community"],
        created_at_ms=utc_ms(2026, 9, 30, 10, 30),
    )
    xsl_after = XiaoShiLiuPostAsset(
        author_user_id=XIAOSHILIU_LOGIN_USER_ID,
        title=POST_TITLE,
        content=XSL_AFTER_CONTENT,
        category="Campus Life",
        tags=["repair fair", "community"],
    )
    xsl_registration_post = XiaoShiLiuPostAsset(
        author_user_id=XIAOSHILIU_LOGIN_USER_ID,
        title="Repair Fair Registration Notes",
        content="Registration link still works and small electronics are the best items to bring. I will update time details in the main fair post if needed.",
        category="Campus Life",
        tags=["repair fair", "registration"],
        created_at_ms=utc_ms(2026, 9, 30, 11),
    )
    xsl_toolkit_post = XiaoShiLiuPostAsset(
        author_user_id=XIAOSHILIU_LOGIN_USER_ID,
        title="Repair Fair Volunteer Toolkit",
        content="Volunteer toolkit: label tape, mini screwdrivers, USB testers, and a small sorting tray. This is packing prep, not the attendee schedule.",
        category="Campus Life",
        tags=["repair fair", "volunteer"],
        created_at_ms=utc_ms(2026, 9, 30, 13),
    )
    xsl_seed_swap_post = XiaoShiLiuPostAsset(
        author_user_id=XIAOSHILIU_LOGIN_USER_ID,
        title="Campus Seed Swap Reminder",
        content="Seed swap is Saturday at 10:00 AM in North Hall. Bring labeled seedlings and envelopes.",
        category="Campus Life",
        tags=["garden", "swap"],
        created_at_ms=utc_ms(2026, 10, 1, 7, 55),
    )
    xsl_question = XiaoShiLiuCommentAsset(
        post_title=POST_TITLE,
        post_author_user_id=XIAOSHILIU_LOGIN_USER_ID,
        author_user_id="v2-18-commenter",
        content=CLARIFY_COMMENT,
        created_at_ms=utc_ms(2026, 10, 1, 9),
    )
    xsl_registration_comment = XiaoShiLiuCommentAsset(
        post_title=POST_TITLE,
        post_author_user_id=XIAOSHILIU_LOGIN_USER_ID,
        author_user_id="v2-18-reg-question",
        content="If the plan moved, is the registration link still the same one?",
        created_at_ms=utc_ms(2026, 10, 1, 9, 4),
    )
    xsl_tool_comment = XiaoShiLiuCommentAsset(
        post_title="Repair Fair Volunteer Toolkit",
        post_author_user_id=XIAOSHILIU_LOGIN_USER_ID,
        author_user_id="v2-18-tools",
        content="I can bring the battery meter and extra label tape.",
        created_at_ms=utc_ms(2026, 10, 1, 9, 10),
    )
    xsl_swap_comment = XiaoShiLiuCommentAsset(
        post_title="Campus Seed Swap Reminder",
        post_author_user_id=XIAOSHILIU_LOGIN_USER_ID,
        author_user_id="v2-18-swap",
        content="North Hall still works for the seed swap; I will bring envelopes.",
        created_at_ms=utc_ms(2026, 10, 1, 9, 15),
    )
    expected_xsl_reply = XiaoShiLiuCommentAsset(
        post_title=POST_TITLE,
        post_author_user_id=XIAOSHILIU_LOGIN_USER_ID,
        author_user_id=XIAOSHILIU_LOGIN_USER_ID,
        content=XSL_REPLY,
        parent_content=CLARIFY_COMMENT,
        parent_author_user_id="v2-18-commenter",
    )

    ride_member = ElementXUserAsset(username="v2-18-ride-member", password="password", display_name="Ride Member")
    volunteer_member = ElementXUserAsset(username="v2-18-volunteer", password="password", display_name="Volunteer Helper")
    swap_member = ElementXUserAsset(username="v2-18-swap-rider", password="password", display_name="Seed Swap Rider")
    ride_room = ElementXRoomAsset(
        name="Weekend Ride Board",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=["v2-18-ride-member"],
        alias_localpart=RIDE_ROOM_ALIAS,
        topic="Pickup coordination for campus weekend events",
    )
    volunteer_room = ElementXRoomAsset(
        name="Volunteer Bench",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=["v2-18-volunteer"],
        alias_localpart=VOLUNTEER_ROOM_ALIAS,
        topic="Repair fair supplies and volunteer prep",
    )
    swap_room = ElementXRoomAsset(
        name="Swap Ride Board",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=["v2-18-swap-rider"],
        alias_localpart=SWAP_ROOM_ALIAS,
        topic="Garden club seed swap rides",
    )
    old_ride_message = ElementXMessageAsset(room=RIDE_ROOM_ALIAS, sender_username="v2-18-ride-member", sender_password="password", text="Can we still meet near North Hall for Saturday pickup before the repair fair?", created_at_ms=utc_ms(2026, 10, 1, 9, 15))
    ride_followup_message = ElementXMessageAsset(room=RIDE_ROOM_ALIAS, sender_username="v2-18-ride-member", sender_password="password", text="If the fair moved, I need the pickup side updated before I post the car list.", created_at_ms=utc_ms(2026, 10, 1, 9, 18))
    volunteer_message = ElementXMessageAsset(room=VOLUNTEER_ROOM_ALIAS, sender_username="v2-18-volunteer", sender_password="password", text="I packed label tape and two small screwdrivers for the repair fair table.", created_at_ms=utc_ms(2026, 10, 1, 9, 12))
    volunteer_schedule_message = ElementXMessageAsset(room=VOLUNTEER_ROOM_ALIAS, sender_username="v2-18-volunteer", sender_password="password", text="East Library setup after noon sounds fine; this room is only for supplies.", created_at_ms=utc_ms(2026, 10, 1, 9, 22))
    swap_message = ElementXMessageAsset(room=SWAP_ROOM_ALIAS, sender_username="v2-18-swap-rider", sender_password="password", text="Seed swap pickup is still Saturday 9:45 near North Hall, right?", created_at_ms=utc_ms(2026, 10, 1, 9, 25))

    attendee_contact = ContactAsset(name="Jordan Lee", phone_number="+15550181801", label="repair fair attendee")
    volunteer_contact = ContactAsset(name="Casey Tran", phone_number="+15550181802", label="repair fair volunteer")
    garden_contact = ContactAsset(name="Mina Patel", phone_number="+15550181803", label="garden club")
    registration_contact = ContactAsset(name="Riley Chen", phone_number="+15550181804", label="repair fair attendee")
    attendee_question = SmsMessageAsset(
        address=attendee_contact.phone_number,
        body="Does the original Saturday North Hall repair fair plan still stand?",
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 9, 20),
        read=True,
    )
    volunteer_question = SmsMessageAsset(
        address=volunteer_contact.phone_number,
        body="Do you still need label tape for the repair fair table?",
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 9, 24),
        read=True,
    )
    garden_question = SmsMessageAsset(
        address=garden_contact.phone_number,
        body="Seed swap still Saturday at North Hall? I have envelopes ready.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 9, 26),
        read=True,
    )
    registration_question = SmsMessageAsset(
        address=registration_contact.phone_number,
        body="For the repair fair, I only need to know whether my registration link is still valid.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 9, 28),
        read=True,
    )

    assets = (
        account,
        logistics_mail,
        registration_mail,
        toolkit_mail,
        seed_swap_mail,
        library_av_mail,
        mastodon_session,
        mastodon_before,
        mastodon_registration_note,
        mastodon_toolkit_note,
        mastodon_seed_swap,
        mastodon_library_note,
        xsl_commenter,
        xsl_registration_user,
        xsl_tools_user,
        xsl_swap_user,
        XiaoShiLiuSessionAsset(user_id=XIAOSHILIU_LOGIN_USER_ID),
        xsl_before,
        xsl_registration_post,
        xsl_toolkit_post,
        xsl_seed_swap_post,
        xsl_question,
        xsl_registration_comment,
        xsl_tool_comment,
        xsl_swap_comment,
        ride_member,
        volunteer_member,
        swap_member,
        ride_room,
        volunteer_room,
        swap_room,
        ElementXSessionAsset(username="testuser", password="testpass123"),
        old_ride_message,
        ride_followup_message,
        volunteer_message,
        volunteer_schedule_message,
        swap_message,
        attendee_contact,
        volunteer_contact,
        garden_contact,
        registration_contact,
        attendee_question,
        volunteer_question,
        garden_question,
        registration_question,
    )
    goal = (
        "The event organizer sent a logistics update. Use Mail to determine what changed and what details remain valid, then clean up the social and private follow-up. "
        "Edit my existing Mastodon repair fair post that still sends attendees to the old plan so it has the corrected day, time, and location while preserving the valid registration sentence. In XiaoShiLiu, edit the existing post titled 'Community Repair Fair Details' that still sends attendees to the old plan; keep that title unchanged and update only the post content so it has the corrected day, time, and location while preserving the valid bring-item and registration sentences. Reply to the XiaoShiLiu clarification about the old plan, update the ElementX ride conversation that depends on repair fair pickup, and answer Jordan Lee, the direct Messages contact asking whether the original repair fair plan still stands. "
        "For remaining formatted outputs, use day-of-week plus h:mm AM/PM format for the new day/time, such as Tuesday at 4:30 PM, and use the room-style location from Mail, such as West Hall Room 101. Use these exact output formats: XiaoShiLiu reply 'Correction: the fair is now <new day> at <new time> in <new location>.'; ElementX 'Ride update: the repair fair moved to <new day> at <new time> in <new location>. Please switch pickup planning to <new place>.'; SMS 'The original plan changed: the repair fair is now <new day> at <new time> in <new location>. Registration is still valid.'."
    )

    def criteria(self):
        return [
            AssetModified(self.mastodon_before, self.mastodon_after, task=self),
            AssetModified(self.xsl_before, self.xsl_after, task=self),
            AssetExists(self.expected_xsl_reply, task=self),
            AssetExists(ElementXMessageAsset(room=RIDE_ROOM_ALIAS, sender_username="testuser", sender_password="testpass123", text=GROUP_UPDATE), task=self),
            AssetExists(SmsMessageAsset(address=self.attendee_contact.phone_number, body=DIRECT_REPLY, box="sent", read=True), task=self),
        ]
