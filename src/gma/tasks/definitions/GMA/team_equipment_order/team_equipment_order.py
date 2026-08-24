from __future__ import annotations

from datetime import UTC, datetime

from gma.apps.mall import MALL_LOGIN_CITY, MALL_LOGIN_NICKNAME, MALL_LOGIN_PHONE, MALL_LOGIN_USERNAME
from gma.assets import (
    CalendarEventAsset,
    ElementXMessageAsset,
    ElementXPollAsset,
    ElementXPollResponse,
    ElementXRoomAsset,
    ElementXUserAsset,
    MailAccountAsset,
    MailMessageAsset,
    MallAddressAsset,
    MallMemberAsset,
    MattermostChannelAsset,
    MattermostPostAsset,
    MattermostSessionAsset,
    MattermostUserAsset,
)
from gma.evaluation import AssetExists
from gma.evaluation.checks.mall import MallCheckoutOrderCreated
from gma.tasks.base import BaseTask


def dt_ms(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


PRODUCT_SN = "85QNED82BCA"
PRODUCT_NAME = "2026 85-inch LG QNED evo AI QNED82 Mini LED 4K smart TV"
RECEIVER_NAME = "Morgan Carter"
RECEIVER_PHONE = "5550102401"
RECEIVER_PROVINCE = "New York State"
RECEIVER_CITY = "New York City"
RECEIVER_REGION = "Queens Borough"
RECEIVER_DETAIL_ADDRESS = "Project Room Atlas, Floor 8"
FIT_REQUIREMENT = "76-inch wall-bay"
SETUP_EVENT = CalendarEventAsset(
    title="Project room display setup",
    start_ms=dt_ms(2026, 10, 6, 15, 0),
    end_ms=dt_ms(2026, 10, 6, 16, 0),
    description=f"Set up the {PRODUCT_NAME} in Project Room Atlas.",
    location="Project Room Atlas",
    timezone="UTC",
    reminder_minutes=(60,),
)
TEAM_UPDATE = (
    f"Ordered the {PRODUCT_NAME} for Project Room Atlas. "
    "Setup is scheduled for Oct 6, 2026 at 3:00 PM UTC."
)


class TeamEquipmentOrderTask(BaseTask):
    apps = {"ElementX", "Mall", "Mail", "Mattermost", "Calendar"}
    difficulty = "realistic"
    category = ['Information-Gathering Tasks', 'Selection / Optimization Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    max_steps = 180

    assets = (
        ElementXUserAsset(username="atlas-coord", password="password", display_name="Atlas Coordinator"),
        ElementXUserAsset(username="ana-review", password="password", display_name="Ana Review"),
        ElementXUserAsset(username="omar-design", password="password", display_name="Omar Design"),
        ElementXUserAsset(username="mei-ux", password="password", display_name="Mei UX"),
        ElementXUserAsset(username="ben-audio", password="password", display_name="Ben Audio"),
        ElementXUserAsset(username="nina-ops", password="password", display_name="Nina Ops"),
        ElementXRoomAsset(
            name="Atlas Equipment Decisions",
            room_type="group",
            creator_username="atlas-coord",
            creator_password="password",
            members=["testuser", "ana-review", "omar-design", "mei-ux", "ben-audio", "nina-ops"],
            alias_localpart="atlas-equipment-decisions",
            topic="Project Room Atlas equipment decision log",
        ),
        ElementXRoomAsset(
            name="Demo Lounge Gear",
            room_type="group",
            creator_username="nina-ops",
            creator_password="password",
            members=["testuser", "atlas-coord", "ben-audio"],
            alias_localpart="demo-lounge-gear",
            topic="Demo lounge equipment ideas",
        ),
        ElementXPollAsset(
            room="atlas-equipment-decisions",
            sender_username="atlas-coord",
            sender_password="password",
            question="What should the Atlas room purchase support first?",
            options=["Shared review display", "Audio recording kit", "Loaner laptop", "Mobile whiteboard kit"],
            responses=[
                ElementXPollResponse(username="atlas-coord", password="password", option="Shared review display"),
                ElementXPollResponse(username="ana-review", password="password", option="Shared review display"),
                ElementXPollResponse(username="omar-design", password="password", option="Shared review display"),
                ElementXPollResponse(username="mei-ux", password="password", option="Shared review display"),
                ElementXPollResponse(username="ben-audio", password="password", option="Audio recording kit"),
                ElementXPollResponse(username="nina-ops", password="password", option="Mobile whiteboard kit"),
            ],
            created_at_ms=dt_ms(2026, 10, 1, 9, 10),
        ),
        ElementXMessageAsset(
            room="atlas-equipment-decisions",
            sender_username="ana-review",
            sender_password="password",
            text="The design reviews in Atlas usually have ten or twelve people around the wall, so the shared review surface matters more than individual gear.",
            created_at_ms=dt_ms(2026, 10, 1, 9, 24),
        ),
        ElementXMessageAsset(
            room="atlas-equipment-decisions",
            sender_username="omar-design",
            sender_password="password",
            text="Facilities asked us to keep this to one centered wall display because the room has one clean cable path at the mount.",
            created_at_ms=dt_ms(2026, 10, 1, 9, 28),
        ),
        ElementXMessageAsset(
            room="atlas-equipment-decisions",
            sender_username="ben-audio",
            sender_password="password",
            text="I still want a better audio kit for recordings, but that can move through the media request after this room order is closed.",
            created_at_ms=dt_ms(2026, 10, 1, 9, 33),
        ),
        ElementXMessageAsset(
            room="atlas-equipment-decisions",
            sender_username="mei-ux",
            sender_password="password",
            text="The reception art screen looks good for signage, but our Atlas boards need more review area than that lobby setup gives us.",
            created_at_ms=dt_ms(2026, 10, 1, 9, 41),
        ),
        ElementXPollAsset(
            room="demo-lounge-gear",
            sender_username="nina-ops",
            sender_password="password",
            question="What should the demo lounge consider later?",
            options=["Stage screen", "Podcast microphones", "Cafe speakers", "Soft seating"],
            responses=[
                ElementXPollResponse(username="nina-ops", password="password", option="Stage screen"),
                ElementXPollResponse(username="ben-audio", password="password", option="Podcast microphones"),
            ],
            created_at_ms=dt_ms(2026, 10, 1, 10, 5),
        ),
        ElementXMessageAsset(
            room="demo-lounge-gear",
            sender_username="atlas-coord",
            sender_password="password",
            text="The lounge ideas can wait for a separate facilities walk-through; Atlas is the active room request this week.",
            created_at_ms=dt_ms(2026, 10, 1, 10, 12),
        ),
        MailAccountAsset(display_name="Morgan Carter", email="morgan.carter@example.com"),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Procurement",
            from_email="procurement@example.com",
            to=["morgan.carter@example.com"],
            subject="Atlas room equipment approval",
            body=(
                "For Project Room Atlas, this approval covers one room-equipment item purchased from Mall. "
                "The approved ceiling is 15000 for the product. Personal headphones, laptops, audio kits, carts, "
                "and multi-item bundles need separate approvals. Use the Morgan Carter Atlas address for the order."
            ),
            timestamp_ms=dt_ms(2026, 10, 1, 11, 0),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Procurement",
            from_email="procurement@example.com",
            to=["morgan.carter@example.com"],
            subject="Q4 laptop refresh intake",
            body="The laptop refresh queue is collecting model requests this month. That budget is allocated per employee and will not be merged into room equipment orders.",
            timestamp_ms=dt_ms(2026, 10, 1, 8, 20),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Media Operations",
            from_email="media.ops@example.com",
            to=["morgan.carter@example.com"],
            subject="Audio accessory request timing",
            body="Ben's microphone and speaker ideas can use the media accessories process after the Atlas room purchase is complete. The media accessories cap is separate from the room display request.",
            timestamp_ms=dt_ms(2026, 10, 1, 8, 45),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Facilities",
            from_email="facilities@example.com",
            to=["morgan.carter@example.com"],
            subject="Rolling cart storage",
            body="Rolling carts are being inventoried for conference rooms Orion and Lyra. Project Room Atlas has a fixed wall mount path, so cart storage does not affect the Atlas display order.",
            timestamp_ms=dt_ms(2026, 10, 1, 9, 15),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Reception Desk",
            from_email="reception@example.com",
            to=["morgan.carter@example.com"],
            subject="Lobby art display note",
            body="Reception likes the smaller art-style display for the lobby wall because it blends with signage. That note is for lobby purchasing, not the Project Room Atlas review wall.",
            timestamp_ms=dt_ms(2026, 10, 1, 10, 35),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Shipping Desk",
            from_email="shipping@example.com",
            to=["morgan.carter@example.com"],
            subject="Atlas receiver record",
            body="For Atlas room equipment, Morgan Carter remains the receiver on Floor 8. Use the saved Project Room Atlas address when checkout asks for the shipping address.",
            timestamp_ms=dt_ms(2026, 10, 1, 11, 20),
            read=False,
        ),
        MattermostChannelAsset(
            team="company",
            name="project-room-atlas",
            display_name="Project Room Atlas",
            channel_type="O",
        ),
        MattermostChannelAsset(
            team="company",
            name="office-av",
            display_name="Office AV",
            channel_type="O",
        ),
        MattermostChannelAsset(
            team="company",
            name="procurement-lane",
            display_name="Procurement Lane",
            channel_type="O",
        ),
        MattermostUserAsset(
            username="morgan",
            email="morgan.carter@example.com",
            first_name="Morgan",
            last_name="Carter",
            team="company",
            channel_memberships=["project-room-atlas", "office-av", "procurement-lane"],
        ),
        MattermostUserAsset(
            username="facilities-lena",
            email="facilities.lena@example.com",
            first_name="Lena",
            last_name="Facilities",
            team="company",
            channel_memberships=["project-room-atlas", "office-av"],
        ),
        MattermostUserAsset(
            username="av-ryan",
            email="av.ryan@example.com",
            first_name="Ryan",
            last_name="AV",
            team="company",
            channel_memberships=["project-room-atlas", "office-av"],
        ),
        MattermostUserAsset(
            username="procurement-ivy",
            email="procurement.ivy@example.com",
            first_name="Ivy",
            last_name="Procurement",
            team="company",
            channel_memberships=["project-room-atlas", "procurement-lane"],
        ),
        MattermostSessionAsset(username="morgan"),
        MattermostPostAsset(
            team="company",
            channel="project-room-atlas",
            username="facilities-lena",
            message="Atlas wall bay measurement from this morning: 76 inches of clear width between the trim, with a little clearance needed on the service-panel side.",
            create_at_ms=dt_ms(2026, 10, 1, 11, 30),
        ),
        MattermostPostAsset(
            team="company",
            channel="project-room-atlas",
            username="av-ryan",
            message="For the review wall, compare the 16:9 display width against the 76-inch wall bay. An 85-inch 16:9 screen is about 74 inches wide, while the 100-inch panels are too wide. Smaller signage screens make the design boards hard to read from the back row.",
            create_at_ms=dt_ms(2026, 10, 1, 11, 42),
        ),
        MattermostPostAsset(
            team="company",
            channel="project-room-atlas",
            username="facilities-lena",
            message="Large auditorium panels would cover the Atlas access strip. Please keep the permanent mount centered on the existing conduit.",
            create_at_ms=dt_ms(2026, 10, 1, 11, 51),
        ),
        MattermostPostAsset(
            team="company",
            channel="project-room-atlas",
            username="facilities-lena",
            message="Facilities can install in Atlas on Tuesday Oct 6 after the 2:30 PM design review clears. The room needs a 30-minute reset before mounting starts, and the work must be finished before the 4:00 PM rehearsal.",
            create_at_ms=dt_ms(2026, 10, 1, 12, 5),
        ),
        MattermostPostAsset(
            team="company",
            channel="project-room-atlas",
            username="procurement-ivy",
            message="Once the display is ordered, post the selected product and setup time back here so the room request can be closed.",
            create_at_ms=dt_ms(2026, 10, 1, 12, 12),
        ),
        MattermostPostAsset(
            team="company",
            channel="office-av",
            username="av-ryan",
            message="Orion auditorium is still evaluating a very large stage screen with a separate high-budget request.",
            create_at_ms=dt_ms(2026, 10, 1, 12, 20),
        ),
        MattermostPostAsset(
            team="company",
            channel="office-av",
            username="facilities-lena",
            message="Reception asked about a decorative art-style panel for lobby signage; it does not use the Atlas wall mount.",
            create_at_ms=dt_ms(2026, 10, 1, 12, 28),
        ),
        MattermostPostAsset(
            team="company",
            channel="office-av",
            username="av-ryan",
            message="Portable speaker inventory is fine for the cafe events this month. No room-display decision needed there.",
            create_at_ms=dt_ms(2026, 10, 1, 12, 36),
        ),
        MattermostPostAsset(
            team="company",
            channel="office-av",
            username="facilities-lena",
            message="Lyra conference room is waiting on a rolling stand part before any screen upgrade can happen.",
            create_at_ms=dt_ms(2026, 10, 1, 12, 44),
        ),
        MattermostPostAsset(
            team="company",
            channel="procurement-lane",
            username="procurement-ivy",
            message="Accessory bundles should not be combined with room-display approvals. Keep headphones, speakers, and carts in their own request lines.",
            create_at_ms=dt_ms(2026, 10, 1, 13, 5),
        ),
        MattermostPostAsset(
            team="company",
            channel="procurement-lane",
            username="procurement-ivy",
            message="Mall orders for room equipment should use saved receiver records when available, then pay with the standard Alipay checkout path.",
            create_at_ms=dt_ms(2026, 10, 1, 13, 12),
        ),
        MattermostPostAsset(
            team="company",
            channel="procurement-lane",
            username="procurement-ivy",
            message="The cafe audio request and Atlas display request are both open this week, but they are tracked against different approvals.",
            create_at_ms=dt_ms(2026, 10, 1, 13, 20),
        ),
        CalendarEventAsset(
            title="Vendor standup",
            start_ms=dt_ms(2026, 10, 6, 9, 0),
            end_ms=dt_ms(2026, 10, 6, 9, 30),
            description="Existing meeting.",
            timezone="UTC",
        ),
        CalendarEventAsset(
            title="Atlas seating walkthrough",
            start_ms=dt_ms(2026, 10, 6, 10, 0),
            end_ms=dt_ms(2026, 10, 6, 11, 0),
            description="Existing meeting.",
            timezone="UTC",
        ),
        CalendarEventAsset(
            title="Design ops lunch",
            start_ms=dt_ms(2026, 10, 6, 12, 0),
            end_ms=dt_ms(2026, 10, 6, 13, 0),
            description="Existing meeting.",
            timezone="UTC",
        ),
        CalendarEventAsset(
            title="Design review",
            start_ms=dt_ms(2026, 10, 6, 13, 0),
            end_ms=dt_ms(2026, 10, 6, 14, 30),
            description="Existing meeting.",
            timezone="UTC",
        ),
        CalendarEventAsset(
            title="Project demo rehearsal",
            start_ms=dt_ms(2026, 10, 6, 16, 0),
            end_ms=dt_ms(2026, 10, 6, 17, 0),
            description="Existing meeting.",
            timezone="UTC",
        ),
        CalendarEventAsset(
            title="Facilities follow-up",
            start_ms=dt_ms(2026, 10, 7, 15, 0),
            end_ms=dt_ms(2026, 10, 7, 15, 30),
            description="Separate follow-up hold.",
            timezone="UTC",
        ),
        MallMemberAsset(
            username=MALL_LOGIN_USERNAME,
            password="123456",
            nickname=MALL_LOGIN_NICKNAME,
            phone=MALL_LOGIN_PHONE,
            city=MALL_LOGIN_CITY,
            status=1,
        ),
        MallAddressAsset(
            member_username=MALL_LOGIN_USERNAME,
            name=RECEIVER_NAME,
            phone_number=RECEIVER_PHONE,
            province=RECEIVER_PROVINCE,
            city=RECEIVER_CITY,
            region=RECEIVER_REGION,
            detail_address=RECEIVER_DETAIL_ADDRESS,
            default_status=True,
        ),
        MallAddressAsset(
            member_username=MALL_LOGIN_USERNAME,
            name="Reception Desk",
            phone_number="5550102402",
            province="New York State",
            city="New York City",
            region="Manhattan Borough",
            detail_address="Lobby Reception Storage",
            default_status=False,
        ),
    )

    goal = (
        "Please handle the Project Room Atlas shared display order. Use the ElementX team decision, procurement email, Mattermost Project Room Atlas room-fit posts for the wall-bay fit requirement and feasible install window, actual Mall TV names/sizes/prices, and my Calendar. Buy the display that satisfies all current constraints using the saved room-equipment receiver address and pay with Alipay. Add a Calendar setup session titled 'Project room display setup' at the feasible time after the post-review room reset and before the 4:00 PM rehearsal. The setup session must last exactly one hour. Use location 'Project Room Atlas', description 'Set up the <full display name> in Project Room Atlas.', and a 60-minute reminder. Post in Mattermost Project Room Atlas exactly in this format: 'Ordered the <full display name> for Project Room Atlas. Setup is scheduled for <date/time>.'. For the Mattermost date/time field, use the format shown by this example: January 2, 2026 at 4:30 PM UTC."
    )

    user_interaction = (
        "If the agent asks which Mall shipping address to use for the Project Room Atlas display order, answer exactly: "
        "Use Morgan Carter at Project Room Atlas, Floor 8."
    )

    def criteria(self):
        return [
            MallCheckoutOrderCreated(
                member_username=MALL_LOGIN_USERNAME,
                product_sn=PRODUCT_SN,
                quantity=1,
                expected_status=1,
                receiver_name=RECEIVER_NAME,
                receiver_phone=RECEIVER_PHONE,
                receiver_province=RECEIVER_PROVINCE,
                receiver_city=RECEIVER_CITY,
                receiver_region=RECEIVER_REGION,
                receiver_detail_address=RECEIVER_DETAIL_ADDRESS,
            ),
            AssetExists(SETUP_EVENT, task=self),
            AssetExists(
                MattermostPostAsset(
                    team="company",
                    channel="project-room-atlas",
                    username="morgan",
                    message=TEAM_UPDATE,
                ),
                task=self,
            ),
        ]
