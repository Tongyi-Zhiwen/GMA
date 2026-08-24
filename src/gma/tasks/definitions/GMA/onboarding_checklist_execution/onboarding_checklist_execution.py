from __future__ import annotations

from datetime import UTC, datetime

from gma.assets import (
    CalendarEventAsset,
    ContactAsset,
    DeviceFileAsset,
    ElementXMessageAsset,
    ElementXRoomAsset,
    ElementXSessionAsset,
    ElementXUserAsset,
    MailAccountAsset,
    MailAttachment,
    MailMessageAsset,
    MattermostChannelAsset,
    MattermostFilePostAsset,
    MattermostPostAsset,
    MattermostSessionAsset,
    MattermostUserAsset,
)
from gma.evaluation import AssetExists, AssetModified
from gma.tasks.base import BaseTask


def utc_ms(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


MATTERMOST_USER = "v2-14-riley"
MATTERMOST_CHANNEL = "v2-14-people-ops"
ELEMENTX_ALIAS = "v2-14-people-programs"
GUIDE_FILE = "welcome-guide-2026-10.txt"
GUIDE_TEXT = (
    "Welcome guide for the October Product Operations cohort.\n"
    "Confirm official start date, review first-week systems, attend orientation, and meet the assigned mentor.\n"
)
STATUS_UPDATE = (
    "Jordan Ellis onboarding complete: contact updated, welcome email sent, orientation scheduled for Oct 8 at 10:30, "
    "mentor check-in scheduled for Oct 9 at 15:00."
)
WELCOME_BODY = (
    "Welcome Jordan. Your official start date is October 12, 2026. "
    "Please review the attached welcome guide before orientation."
)


class OnboardingChecklistExecutionTask(BaseTask):
    apps = {"Mattermost", "Mail", "Files", "Calendar", "ElementX", "Contacts"}
    difficulty = "realistic"
    category = ["Multi-Step Workflow Tasks"]
    snapshot = "gma_ready_state"
    max_steps = 180

    partial_contact = ContactAsset(name="Jordan Ellis", phone_number="+15550141414", label="candidate")
    completed_contact = ContactAsset(
        name="Jordan Ellis",
        phone_number="+15550141414",
        phone_label="mobile",
        email="jordan.ellis@company.example",
        email_label="work",
        notes="Product Operations Analyst. Starts October 12, 2026. Mentor: Priya Shah.",
        label="Work",
    )
    account = MailAccountAsset(display_name="Riley Cooper", email="riley.cooper@example.com")

    hr_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="HR Operations",
        from_email="hr.ops@example.com",
        to=[account.email],
        subject="Jordan Ellis official HR record",
        body=(
            "Jordan Ellis is joining as Product Operations Analyst. Official start date: October 12, 2026. "
            "Onboarding email: jordan.ellis@company.example. Mobile: +15550141414."
        ),
        timestamp_ms=utc_ms(2026, 10, 1, 9),
        read=False,
    )
    guide_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Olivia Chen",
        from_email="olivia.chen@example.com",
        to=[account.email],
        subject="October guide file for Jordan",
        body=(
            "For Jordan's October 12 start, send welcome-guide-2026-10.txt. "
            "The September guide is still in Downloads for the last cohort."
        ),
        timestamp_ms=utc_ms(2026, 10, 1, 9, 12),
        read=True,
    )
    mentor_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Priya Shah",
        from_email="priya.shah@example.com",
        to=[account.email],
        subject="Jordan mentor timing",
        body=(
            "I am Jordan's mentor. Please put our mentor check-in on October 9 at 15:00 in Product Ops Room. "
            "Use a 15-minute reminder and describe it as Priya Shah mentor check-in for Jordan Ellis."
        ),
        timestamp_ms=utc_ms(2026, 10, 1, 9, 25),
        read=True,
    )
    draft_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Recruiting Desk",
        from_email="recruiting@example.com",
        to=[account.email],
        subject="September intake draft",
        body=(
            "Early intake draft for Jordan listed a tentative October 5 start and the recruiting alias. "
            "HR said the official record would follow once the offer packet cleared."
        ),
        timestamp_ms=utc_ms(2026, 9, 24, 14),
        read=True,
    )
    badge_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Facilities",
        from_email="facilities@example.com",
        to=[account.email],
        subject="Badge queue update",
        body="Jordan's badge packet and laptop request are already in the facilities queue for the October cohort.",
        timestamp_ms=utc_ms(2026, 9, 30, 16),
        read=True,
    )
    desk_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Desk Planning",
        from_email="desks@example.com",
        to=[account.email],
        subject="Product Ops seating map",
        body="The Product Ops seating map changed this week. Orientation still uses People Ops Room unless the checklist says otherwise.",
        timestamp_ms=utc_ms(2026, 10, 1, 8, 20),
        read=True,
    )
    expected_mail = MailMessageAsset(
        mailbox="sent",
        from_name=account.display_name,
        from_email="test@gmail.com",
        to=["jordan.ellis@company.example"],
        subject="Welcome to Product Operations",
        body=WELCOME_BODY,
        attachments=[MailAttachment(filename=GUIDE_FILE, mime_type="text/plain", text_content=GUIDE_TEXT)],
        read=True,
    )

    mattermost_user = MattermostUserAsset(
        username=MATTERMOST_USER,
        email="riley.cooper@example.com",
        first_name="Riley",
        last_name="Cooper",
        team="company",
        channel_memberships=[MATTERMOST_CHANNEL],
    )
    mattermost_channel = MattermostChannelAsset(
        team="company",
        name=MATTERMOST_CHANNEL,
        display_name="People Ops",
        channel_type="O",
        purpose="Onboarding coordination",
    )
    september_packet = MattermostFilePostAsset(
        team="company",
        channel=MATTERMOST_CHANNEL,
        username=MATTERMOST_USER,
        message="Jordan packet from the September planning pass. Leaving it here with the badge notes.",
        filename="jordan-ellis-2026-09-24-packet.txt",
        mime_type="text/plain",
        text_content=(
            "Jordan Ellis packet 2026-09-24\n"
            "Send welcome-guide-2026-09.txt. Request badge packet. Check possible October 5 start.\n"
            "Laptop request and badge queue were not settled when this packet was written.\n"
        ),
        create_at_ms=utc_ms(2026, 9, 24, 15),
    )
    october_packet = MattermostFilePostAsset(
        team="company",
        channel=MATTERMOST_CHANNEL,
        username=MATTERMOST_USER,
        message="Jordan packet from the October 1 people-ops standup. Ana said this packet is the one for execution.",
        filename="jordan-ellis-2026-10-01-packet.txt",
        mime_type="text/plain",
        text_content=(
            "Jordan Ellis packet 2026-10-01\n"
            "Complete the contact from HR's official record. Use mobile for the phone label, work for the email label, "
            "put the contact in the Work label, and add a note in this format: <role>. Starts <official start date>. Mentor: <mentor name>.\n"
            "Welcome mail: use the guide file named by Olivia and the standard Product Operations welcome subject.\n"
            "Orientation: Oct 8 options are 09:30 or 10:30 in People Ops Room; choose the slot that does not overlap Riley's calendar. Schedule it for one hour, use a 30-minute reminder, and describe it as orientation for Jordan Ellis, Product Operations Analyst.\n"
            "Mentor check-in: use Priya's mail and schedule it for 30 minutes.\n"
            "Completion update goes in the ElementX room whose topic is for new teammate onboarding updates.\n"
            "Facilities already has laptop and badge requests.\n"
        ),
        create_at_ms=utc_ms(2026, 10, 1, 10),
    )
    desk_post = MattermostPostAsset(
        team="company",
        channel=MATTERMOST_CHANNEL,
        username=MATTERMOST_USER,
        message="Desk map note: Jordan may sit near Product Ops after orientation, but the room booking is still separate.",
        create_at_ms=utc_ms(2026, 10, 1, 10, 12),
    )
    lunch_post = MattermostPostAsset(
        team="company",
        channel=MATTERMOST_CHANNEL,
        username=MATTERMOST_USER,
        message="People Ops lunch count moved to Friday; no action needed for Jordan's welcome mail.",
        create_at_ms=utc_ms(2026, 10, 1, 10, 30),
    )

    old_guide = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="welcome-guide-2026-09.txt",
        mime_type="text/plain",
        text_content="Welcome guide for the September Product Operations cohort.\n",
    )
    october_guide = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename=GUIDE_FILE,
        mime_type="text/plain",
        text_content=GUIDE_TEXT,
    )
    desk_map = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="product-ops-seating-notes.txt",
        mime_type="text/plain",
        text_content="Seating notes for Product Ops desks. Orientation events are handled by People Ops.\n",
    )

    orientation_conflict = CalendarEventAsset(
        title="Vendor readiness sync",
        start_ms=utc_ms(2026, 10, 8, 9, 15),
        end_ms=utc_ms(2026, 10, 8, 10, 15),
        timezone="UTC",
    )
    afternoon_hold = CalendarEventAsset(
        title="Product Ops office hours",
        start_ms=utc_ms(2026, 10, 8, 14),
        end_ms=utc_ms(2026, 10, 8, 14, 45),
        timezone="UTC",
    )
    orientation_event = CalendarEventAsset(
        title="Jordan Ellis Orientation",
        start_ms=utc_ms(2026, 10, 8, 10, 30),
        end_ms=utc_ms(2026, 10, 8, 11, 30),
        location="People Ops Room",
        description="Orientation for Jordan Ellis, Product Operations Analyst.",
        timezone="UTC",
        reminder_minutes=(30,),
    )
    mentor_event = CalendarEventAsset(
        title="Jordan Ellis Mentor Check-in",
        start_ms=utc_ms(2026, 10, 9, 15),
        end_ms=utc_ms(2026, 10, 9, 15, 30),
        location="Product Ops Room",
        description="Priya Shah mentor check-in for Jordan Ellis.",
        timezone="UTC",
        reminder_minutes=(15,),
    )

    status_user = ElementXUserAsset(username="v2-14-priya", password="password", display_name="Priya Shah")
    ops_user = ElementXUserAsset(username="v2-14-ana", password="password", display_name="Ana Morales")
    status_room = ElementXRoomAsset(
        name="People Programs",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=["v2-14-priya"],
        alias_localpart=ELEMENTX_ALIAS,
        topic="New teammate onboarding updates watched by Priya Shah",
    )
    mentor_room = ElementXRoomAsset(
        name="Mentor Corner",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=["v2-14-priya"],
        alias_localpart="v2-14-mentor-corner",
        topic="General mentoring questions and office-hour swaps",
    )
    ops_room = ElementXRoomAsset(
        name="Ops Desk",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=["v2-14-ana"],
        alias_localpart="v2-14-ops-desk",
        topic="Desk maps, badges, and facilities logistics",
    )

    assets = (
        partial_contact,
        account,
        hr_mail,
        guide_mail,
        mentor_mail,
        draft_mail,
        badge_mail,
        desk_mail,
        mattermost_channel,
        mattermost_user,
        MattermostSessionAsset(username=MATTERMOST_USER),
        september_packet,
        october_packet,
        desk_post,
        lunch_post,
        old_guide,
        october_guide,
        desk_map,
        orientation_conflict,
        afternoon_hold,
        status_user,
        ops_user,
        status_room,
        mentor_room,
        ops_room,
        ElementXSessionAsset(username="testuser", password="testpass123"),
    )
    goal = (
        "Please finish the onboarding checklist for the new teammate. Use the Mattermost packet dated for the active "
        "onboarding round, HR email, Files, Contacts, Calendar, and ElementX. Complete Jordan Ellis's contact from the "
        "official HR details. Send a Mail message to the onboarding email with subject 'Welcome to Product Operations', "
        "body 'Welcome Jordan. Your official start date is <date>. Please review the attached welcome guide before orientation.', "
        "using full Month D, YYYY format for <date>, such as January 2, 2026, and attach the correct welcome guide file. "
        "Schedule Calendar events titled 'Jordan Ellis Orientation' and "
        "'Jordan Ellis Mentor Check-in' in the required conflict-free slots with the source locations/descriptions and reminders. "
        "Post ElementX status in the room whose topic is for new teammate onboarding updates exactly: 'Jordan Ellis onboarding "
        "complete: contact updated, welcome email sent, orientation scheduled for <date/time>, mentor check-in scheduled for "
        "<date/time>.'. Use status date/time format like 'Oct 8 at 10:30'."
    )

    def criteria(self):
        return [
            AssetModified(self.partial_contact, self.completed_contact, task=self),
            AssetExists(self.expected_mail, task=self),
            AssetExists(self.orientation_event, task=self),
            AssetExists(self.mentor_event, task=self),
            AssetExists(
                ElementXMessageAsset(
                    room=ELEMENTX_ALIAS,
                    sender_username="testuser",
                    sender_password="testpass123",
                    text=STATUS_UPDATE,
                ),
                task=self,
            ),
        ]
