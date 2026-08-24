from __future__ import annotations

from datetime import UTC, datetime

from gma.assets import (
    CalendarEventAsset,
    ContactAsset,
    DeviceFileAsset,
    MattermostChannelAsset,
    MattermostPostAsset,
    MattermostSessionAsset,
    MattermostUserAsset,
    SmsMessageAsset,
)
from gma.evaluation import AssetExists
from gma.tasks.base import BaseTask


def dt_ms(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


FRIEND_PHONE = "+1555202501"
IDENTIFICATION_MESSAGE = (
    "That is my blue spiral notebook: silver star sticker on the cover, white elastic strap, "
    "and serial BN-4821 on the inside receipt. I last had it in Project Room Atlas after "
    "the 2:00 PM review. I can pick it up at the North Tower front desk on Oct 2, 2026 at 3:30 PM."
)
PICKUP_EVENT = CalendarEventAsset(
    title="Blue notebook pickup",
    start_ms=dt_ms(2026, 10, 2, 15, 30),
    end_ms=dt_ms(2026, 10, 2, 16, 0),
    description="Pick up blue spiral notebook with silver star sticker, white elastic strap, serial BN-4821.",
    location="North Tower front desk",
    timezone="UTC",
    reminder_minutes=(15,),
)
FRIEND_CONFIRMATION = (
    "Found it. The lost-and-found thread matches my blue spiral notebook with the silver star sticker on the cover "
    "and serial BN-4821. Pickup is scheduled at the North Tower front desk on Oct 2, 2026 at 3:30 PM."
)


class LostItemRecoveryTask(BaseTask):
    apps = {"Messages", "Gallery", "Files", "Calendar", "Mattermost", "Contacts"}
    difficulty = "realistic"
    category = ['Selection / Optimization Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"

    assets = (
        DeviceFileAsset(
            app="Gallery",
            storage_dir="Pictures",
            filename="IMG_2401.png",
            mime_type="image/png",
            source_path="assets/IMG_2401.png",
        ),
        DeviceFileAsset(
            app="Gallery",
            storage_dir="Pictures",
            filename="IMG_2402.png",
            mime_type="image/png",
            source_path="assets/IMG_2402.png",
        ),
        DeviceFileAsset(
            app="Gallery",
            storage_dir="Pictures",
            filename="IMG_2403.png",
            mime_type="image/png",
            source_path="assets/IMG_2403.png",
        ),
        DeviceFileAsset(
            app="Files",
            storage_dir="Download",
            filename="blue-notebook-receipt.txt",
            mime_type="text/plain",
            text_content="Blue spiral notebook receipt. Cover marker: silver star sticker. Strap: white elastic. Serial: BN-4821.",
        ),
        ContactAsset(name="North Tower Front Desk", phone_number="+1555202500", notes="Office lost and found for North Tower meeting rooms"),
        ContactAsset(name="South Tower Front Desk", phone_number="+1555202502", notes="Handles South Tower lobby and training-room lost items"),
        ContactAsset(name="Cafe Security Desk", phone_number="+1555202503", notes="Handles cafe and atrium lost items"),
        ContactAsset(name="Facilities Office", phone_number="+1555202504", notes="Room access and facilities equipment holds"),
        ContactAsset(name="Jamie Review", phone_number=FRIEND_PHONE, notes="Project review teammate"),
        SmsMessageAsset(
            address=FRIEND_PHONE,
            body="I think I left my blue spiral notebook after the September 30 Project Room Atlas review. It has a silver star sticker and a white elastic strap. The receipt in Files has serial BN-4821.",
            box="inbox",
            timestamp_ms=dt_ms(2026, 10, 1, 14, 20),
            read=False,
        ),
        CalendarEventAsset(
            title="Project Room Atlas review",
            start_ms=dt_ms(2026, 9, 30, 14, 0),
            end_ms=dt_ms(2026, 9, 30, 15, 0),
            description="Likely place the notebook was left.",
            location="Project Room Atlas",
            timezone="UTC",
        ),
        CalendarEventAsset(
            title="Client call",
            start_ms=dt_ms(2026, 10, 2, 16, 0),
            end_ms=dt_ms(2026, 10, 2, 17, 0),
            description="Blocks later pickup.",
            timezone="UTC",
        ),
        MattermostChannelAsset(team="company", name="lost-and-found", display_name="Lost and Found", channel_type="O"),
        MattermostUserAsset(
            username="morgan",
            email="morgan.carter@example.com",
            first_name="Morgan",
            last_name="Carter",
            team="company",
            channel_memberships=["lost-and-found"],
        ),
        MattermostUserAsset(
            username="frontdesk-north",
            email="frontdesk.north@example.com",
            first_name="North",
            last_name="Desk",
            team="company",
            channel_memberships=["lost-and-found"],
        ),
        MattermostUserAsset(
            username="frontdesk-south",
            email="frontdesk.south@example.com",
            first_name="South",
            last_name="Desk",
            team="company",
            channel_memberships=["lost-and-found"],
        ),
        MattermostUserAsset(
            username="cafe-security",
            email="cafe.security@example.com",
            first_name="Cafe",
            last_name="Security",
            team="company",
            channel_memberships=["lost-and-found"],
        ),
        MattermostUserAsset(
            username="facilities-avery",
            email="facilities.avery@example.com",
            first_name="Avery",
            last_name="Facilities",
            team="company",
            channel_memberships=["lost-and-found"],
        ),
        MattermostSessionAsset(username="morgan"),
        MattermostPostAsset(
            team="company",
            channel="lost-and-found",
            username="frontdesk-north",
            message="Found after the Project Room Atlas review: blue spiral notebook, white strap, silver star sticker on the cover. No name on the outside. Held at the North Tower front desk until Oct 2, 2026 at 4:00 PM.",
            create_at_ms=dt_ms(2026, 10, 1, 15, 10),
        ),
        MattermostPostAsset(
            team="company",
            channel="lost-and-found",
            username="cafe-security",
            message="Cafe counter pickup: red notebook with a moon sticker and black elastic strap, found near the pastry case. Held at Cafe Security until Oct 2, 2026 at 5:00 PM.",
            create_at_ms=dt_ms(2026, 10, 1, 15, 12),
        ),
        MattermostPostAsset(
            team="company",
            channel="lost-and-found",
            username="frontdesk-south",
            message="South Tower lobby has a plain blue spiral notebook from the training room, no sticker on the cover and a blue elastic strap. Held at the South Tower front desk until Oct 2, 2026 at 4:30 PM.",
            create_at_ms=dt_ms(2026, 10, 1, 15, 14),
        ),
        MattermostPostAsset(
            team="company",
            channel="lost-and-found",
            username="facilities-avery",
            message="Project Room Atlas cleanup also found a blue tablet sleeve with a silver comet sticker; Facilities is holding it with the AV adapters until Oct 3, 2026 at 12:00 PM.",
            create_at_ms=dt_ms(2026, 10, 1, 15, 16),
        ),
        MattermostPostAsset(
            team="company",
            channel="lost-and-found",
            username="frontdesk-north",
            message="North Tower hallway item: black umbrella with a white handle, found outside Atlas after the review block. Held at the North Tower front desk until Oct 2, 2026 at 4:45 PM.",
            create_at_ms=dt_ms(2026, 10, 1, 15, 18),
        ),
        MattermostPostAsset(
            team="company",
            channel="lost-and-found",
            username="frontdesk-south",
            message="Training room item: blue notebook with a silver star sticker but initials AB on the first page and no white strap. Held at the South Tower front desk until Oct 2, 2026 at 4:00 PM.",
            create_at_ms=dt_ms(2026, 10, 1, 15, 20),
        ),
    )

    goal = (
        "Please help recover the item I lost. Use Messages, Gallery photos, Files, Calendar, Mattermost, and Contacts to identify the correct lost item and separate it from lookalikes. Use the held-until date/time, Calendar availability, and front-desk location to choose a feasible pickup 30 minutes before the final pickup deadline. "
        "Post Mattermost Lost and Found exactly: 'That is my <item>: <sticker detail>, <strap detail>, and serial <serial> on the inside receipt. I last had it in <place> after the <review time> review. I can pick it up at the <pickup location> on <pickup date> at <pickup time>.'. Use the attribute order sticker, strap, serial; for example, write non-answer attributes like 'green triangle sticker on the cover, black elastic strap, and serial ZX-1000 on the inside receipt.' Use date/time formatting like 'Jan 5, 2026 at 1:15 PM'. "
        "Add a Calendar pickup event titled '<item short name> pickup' at the feasible time/location. The event must last 30 minutes. Use description 'Pick up <item short name> with <sticker detail>, <strap detail>, serial <serial>.' and set a 15-minute reminder. "
        "Send Jamie Review exactly: 'Found it. The lost-and-found thread matches my <full item name> with the <sticker detail> and serial <serial>. Pickup is scheduled at the <pickup location> on <pickup date> at <pickup time>.'."
    )

    def criteria(self):
        return [
            AssetExists(
                MattermostPostAsset(
                    team="company",
                    channel="lost-and-found",
                    username="morgan",
                    message=IDENTIFICATION_MESSAGE,
                ),
                task=self,
            ),
            AssetExists(PICKUP_EVENT, task=self),
            AssetExists(
                SmsMessageAsset(address=FRIEND_PHONE, body=FRIEND_CONFIRMATION, box="sent", read=True),
                task=self,
            ),
        ]
