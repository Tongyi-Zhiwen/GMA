from __future__ import annotations

from datetime import UTC, datetime

from gma.assets import (
    AlarmAsset,
    CalendarEventAsset,
    ContactAsset,
    DeviceFileAsset,
    MailAccountAsset,
    MailAttachment,
    MailMessageAsset,
    SmsMessageAsset,
)
from gma.evaluation import AssetExists
from gma.tasks.base import BaseTask


def utc_ms(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


KITCHEN_PHOTO_IMAGE = "kitchen-sink-leak-photo.png"
KITCHEN_PHOTO_TEXT = (
    "Kitchen photo summary: Water is visible under the kitchen sink and spreading across the cabinet floor panel.\n"
)
UNDER_SINK_TEXT = (
    "Under-sink status report: shutoff valve is closed; leak slowed after several minutes but did not fully stop.\n"
)
REPAIR_BODY = (
    "Unit: 4B\n"
    "Issue: kitchen sink leak\n"
    "Location: kitchen sink\n"
    "Preferred access window: October 2, 2026, 2:00 PM-4:00 PM"
)
ROOMMATE_REPLY = "kitchen sink leak submitted now with the matching evidence files."


class HomeRepairCoordinationTask(BaseTask):
    apps = {"Messages", "Mail", "Files", "Gallery", "Calendar", "Clock", "Contacts"}
    difficulty = "realistic"
    category = ['Information-Gathering Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    max_steps = 180

    account = MailAccountAsset(display_name="Avery Brooks", email="avery.brooks@example.com")

    roommate = ContactAsset(name="Sam Rivera", phone_number="+15550161601", label="roommate")
    maintenance = ContactAsset(
        name="Cedar Flats Maintenance",
        phone_number="+15550161602",
        email="building.maintenance@example.com",
        email_label="work",
        label="home",
    )
    landlord = ContactAsset(name="Jules Kim", phone_number="+15550161603", email="jules.kim@example.com", label="home")
    property_coordinator = ContactAsset(
        name="Morgan Lee",
        phone_number="+15550161604",
        email="old.manager@example.com",
        email_label="work",
        label="property services",
    )

    kitchen_leak_message = SmsMessageAsset(
        address=roommate.phone_number,
        body=(
            "Kitchen sink leak: water is spreading across the cabinet floor panel. I turned the shutoff valve; "
            "it slowed after a few minutes but did not fully stop."
        ),
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 8, 15),
        read=True,
    )
    gallery_note_message = SmsMessageAsset(
        address=roommate.phone_number,
        body="I moved the cleaning bin out and put towels down. The photo in Gallery shows the water line under the sink.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 8, 19),
        read=True,
    )
    loose_handle_message = SmsMessageAsset(
        address=roommate.phone_number,
        body="The cabinet handle near the hallway is loose again. It can wait after the sink is handled.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 8, 26),
        read=True,
    )
    bathroom_history_message = SmsMessageAsset(
        address=roommate.phone_number,
        body="The September bathroom drip stayed dry after the gasket fix; I kept the note in case records are useful.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 9, 12, 9),
        read=True,
    )
    radiator_message = SmsMessageAsset(
        address=roommate.phone_number,
        body="The radiator clicked for a minute last night, then stopped. I am not sure it needs anything.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 9, 30, 21, 5),
        read=True,
    )

    move_in_card_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Morgan Lee",
        from_email="old.manager@example.com",
        to=[account.email],
        subject="August move-in maintenance card",
        body=(
            "During the August move-in period, minor requests used old.manager@example.com with subject "
            "Maintenance Request - Unit <unit>. Keep this card for move-in records."
        ),
        timestamp_ms=utc_ms(2026, 8, 20, 10),
        read=True,
    )
    repair_intake_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Jules Kim",
        from_email="jules.kim@example.com",
        to=[account.email],
        subject="Unit 4B repair intake procedure",
        body=(
            "For urgent apartment repairs in Unit 4B, email Cedar Flats Maintenance at building.maintenance@example.com. "
            "Use subject format URGENT REPAIR - Unit <unit> - <issue>. Include unit number, issue, location, "
            "and preferred access window. "
            "Preferred access windows should be two-hour blocks from 10:00 AM-12:00 PM, 2:00 PM-4:00 PM, "
            "or 4:00 PM-6:00 PM on the requested date when possible."
        ),
        timestamp_ms=utc_ms(2026, 10, 1, 7, 30),
        read=False,
    )
    building_newsletter_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Cedar Flats Office",
        from_email="office@cedarflats.example.com",
        to=[account.email],
        subject="October building notes",
        body="Recycling pickup moves to Friday this week. Quiet hours stay 10:00 PM-7:00 AM.",
        timestamp_ms=utc_ms(2026, 10, 1, 7, 50),
        read=False,
    )
    package_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Jules Kim",
        from_email="jules.kim@example.com",
        to=[account.email],
        subject="Package desk and parking reminder",
        body="The package desk is staffed until 6:30 PM today. Guest parking passes are still available from the lobby kiosk.",
        timestamp_ms=utc_ms(2026, 10, 1, 10),
        read=False,
    )
    portal_notice_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Cedar Flats Portal",
        from_email="portal@cedarflats.example.com",
        to=[account.email],
        subject="Resident portal banner this week",
        body="Some residents may see a maintenance portal migration banner next week. Email intake remains available for emergencies.",
        timestamp_ms=utc_ms(2026, 9, 29, 11),
        read=True,
    )

    leak_photo = DeviceFileAsset(
        app="Gallery",
        storage_dir="Pictures",
        filename=KITCHEN_PHOTO_IMAGE,
        mime_type="image/png",
        source_path=f"assets/{KITCHEN_PHOTO_IMAGE}",
    )
    leak_photo_note = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="kitchen-leak-photo-note.txt",
        mime_type="text/plain",
        text_content=KITCHEN_PHOTO_TEXT,
    )
    under_sink_note = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="under-sink-status.txt",
        mime_type="text/plain",
        text_content=UNDER_SINK_TEXT,
    )
    cabinet_handle_note = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="cabinet-handle-note.txt",
        mime_type="text/plain",
        text_content="Cabinet handle note: hallway-side cabinet pull is loose; no water or access issue reported.\n",
    )
    bathroom_drip_note = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="bathroom-drip-september-note.txt",
        mime_type="text/plain",
        text_content="September bathroom drip note: gasket replaced and the sink stayed dry during the follow-up check.\n",
    )
    radiator_note = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="radiator-click-note.txt",
        mime_type="text/plain",
        text_content="Radiator note: one short clicking noise was heard at night and then stopped.\n",
    )
    appliance_manual = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="dishwasher-manual.txt",
        mime_type="text/plain",
        text_content="Dishwasher manual excerpt: check filter monthly and avoid blocking the drain line.\n",
    )
    repair_template = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="repair-request-template.txt",
        mime_type="text/plain",
        text_content=(
            "Repair request fields: unit, issue, location, preferred access window.\n"
        ),
    )

    client_call = CalendarEventAsset(
        title="Client call",
        start_ms=utc_ms(2026, 10, 2, 10),
        end_ms=utc_ms(2026, 10, 2, 12),
        timezone="UTC",
    )
    lunch_hold = CalendarEventAsset(
        title="Lunch with Maya",
        start_ms=utc_ms(2026, 10, 2, 12, 30),
        end_ms=utc_ms(2026, 10, 2, 13, 15),
        timezone="UTC",
    )
    lease_pickup = CalendarEventAsset(
        title="Lease paperwork pickup",
        start_ms=utc_ms(2026, 10, 2, 16),
        end_ms=utc_ms(2026, 10, 2, 18),
        timezone="UTC",
    )

    access_event = CalendarEventAsset(
        title="Repair Access Window - kitchen sink leak",
        start_ms=utc_ms(2026, 10, 2, 14),
        end_ms=utc_ms(2026, 10, 2, 16),
        location="Unit 4B",
        description="Preferred access window for urgent kitchen sink leak repair request.",
        timezone="UTC",
        reminder_minutes=(60,),
    )
    expected_mail = MailMessageAsset(
        mailbox="sent",
        from_name=account.display_name,
        from_email="test@gmail.com",
        to=["building.maintenance@example.com"],
        subject="URGENT REPAIR - Unit 4B - kitchen sink leak",
        body=REPAIR_BODY,
        attachments=[
            MailAttachment(filename="kitchen-leak-photo-note.txt", mime_type="text/plain", text_content=KITCHEN_PHOTO_TEXT),
            MailAttachment(filename="under-sink-status.txt", mime_type="text/plain", text_content=UNDER_SINK_TEXT),
        ],
        read=True,
    )
    reply_alarm = AlarmAsset(
        hour=18,
        minute=0,
        label="Check maintenance reply",
        enabled=True,
        vibrate=False,
        scheduled_year=2026,
        scheduled_month=10,
        scheduled_day=1,
    )
    access_alarm = AlarmAsset(
        hour=13,
        minute=30,
        label="Prepare for repair access",
        enabled=True,
        vibrate=False,
        scheduled_year=2026,
        scheduled_month=10,
        scheduled_day=2,
    )

    assets = (
        account,
        roommate,
        maintenance,
        landlord,
        property_coordinator,
        kitchen_leak_message,
        gallery_note_message,
        loose_handle_message,
        bathroom_history_message,
        radiator_message,
        move_in_card_mail,
        repair_intake_mail,
        building_newsletter_mail,
        package_mail,
        portal_notice_mail,
        leak_photo,
        leak_photo_note,
        under_sink_note,
        cabinet_handle_note,
        bathroom_drip_note,
        radiator_note,
        appliance_manual,
        repair_template,
        client_call,
        lunch_hold,
        lease_pickup,
    )
    goal = (
        "Please handle the apartment repair situation from Sam's messages. Use the landlord repair instructions in Mail, "
        "Contacts, Files and Gallery evidence, Calendar, and Clock. Decide which issue needs the urgent repair Mail. "
        "Send the Mail to the maintenance recipient with subject exactly 'URGENT REPAIR - Unit <unit> - <issue>' where "
        "<issue> is the urgent issue phrase from Sam's messages in lowercase, and a body using one line per field in this exact template: "
        "start each field label at the beginning of its line with no leading spaces. "
        "'Unit: <unit>\nIssue: <issue>\nLocation: <location>\n"
        "Preferred access window: <full Month D, YYYY, h:mm AM-h:mm PM window>'. "
        "For the access-window date and time, use full Month D, YYYY plus h:mm AM-h:mm PM range, "
        "such as January 2, 2026, 2:00 PM-4:00 PM. "
        "Attach only the matching evidence summary/status text files for the urgent issue. Add a Calendar access-window event "
        "titled 'Repair Access Window - <issue>' at the selected window, located at 'Unit <unit>', with description "
        "'Preferred access window for urgent <issue> repair request.' and a 60-minute reminder. Set Clock alarms with vibration off labeled "
        "'Check maintenance reply' at October 1, 2026 6:00 PM and 'Prepare for repair access' 30 minutes before the selected access window starts. "
        "Text Sam exactly using the format '<urgent issue> submitted now with the matching evidence files.'."
    )

    user_interaction = (
        "If the agent asks which repair access window to offer, answer exactly: "
        "Use October 2, 2026, 2:00 PM-4:00 PM."
    )

    def criteria(self):
        return [
            AssetExists(self.expected_mail, task=self),
            AssetExists(self.access_event, task=self),
            AssetExists(self.reply_alarm, task=self),
            AssetExists(self.access_alarm, task=self),
            AssetExists(SmsMessageAsset(address=self.roommate.phone_number, body=ROOMMATE_REPLY, box="sent", read=True), task=self),
        ]
