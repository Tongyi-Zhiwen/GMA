from __future__ import annotations

from datetime import UTC, datetime

from gma.apps.hmdp import HMDP_DEFAULT_ICON, HMDP_LOGIN_NICKNAME, HMDP_LOGIN_PASSWORD, HMDP_LOGIN_PHONE
from gma.assets import (
    CalendarEventAsset,
    ElementXMessageAsset,
    ElementXRoomAsset,
    ElementXSessionAsset,
    ElementXUserAsset,
    HmdpShopFavoriteAsset,
    HmdpUserAsset,
    MailAccountAsset,
    MailMessageAsset,
)
from gma.evaluation import AssetExists, AssetModified
from gma.tasks.base import BaseTask


def utc_ms(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


ROOM_ALIAS = "v2-15-client-lunch"
SELECTED_RESTAURANT = "Willa Jean"
TEAM_UPDATE = (
    "Client lunch selected: Willa Jean. Willa Jean is 70 per person and fits before the 14:00 Board prep lockout."
)
CLIENT_REPLY_BODY = (
    "Confirmed Willa Jean for October 2 at 12:30. It is 70 per person and stays under the 80 per person budget."
)


class ClientLunchComparisonReportTask(BaseTask):
    apps = {"HMDP", "Mail", "ElementX", "Calendar"}
    difficulty = "realistic"
    category = ['Information-Gathering Tasks', 'Selection / Optimization Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    max_steps = 180

    account = MailAccountAsset(display_name="Client Lunch Owner", email="client.lunch.owner@example.com")
    client_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Client Coordinator",
        from_email="client.coordinator@example.com",
        to=[account.email],
        subject="Client lunch constraints for October 2",
        body=(
            "Please finalize the client lunch for October 2 at 12:30. Budget ceiling is 80 per person. "
            "Vegetarian options are preferred and one guest has a no-shellfish restriction. Keep travel tight around the 14:00 board prep. "
            "Once selected, send me the confirmed restaurant in a short reply."
        ),
        timestamp_ms=utc_ms(2026, 10, 1, 8),
        read=False,
    )
    old_client_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Client Coordinator",
        from_email="client.coordinator@example.com",
        to=[account.email],
        subject="Earlier lunch thought",
        body="Last week I mentioned a higher budget for a dinner plan, but the October 2 lunch note has the actual constraints.",
        timestamp_ms=utc_ms(2026, 9, 26, 11),
        read=True,
    )
    account_note = MailMessageAsset(
        mailbox="inbox",
        from_name="Accounts Team",
        from_email="accounts@example.com",
        to=[account.email],
        subject="Client meeting receipts",
        body="Please keep client lunch receipts under the per-person ceiling from the coordinator's latest note.",
        timestamp_ms=utc_ms(2026, 10, 1, 7, 30),
        read=True,
    )
    expected_reply = MailMessageAsset(
        mailbox="sent",
        from_name=account.display_name,
        from_email="test@gmail.com",
        to=["client.coordinator@example.com"],
        subject="Client lunch confirmed: Willa Jean",
        body=CLIENT_REPLY_BODY,
        read=True,
    )

    teammate = ElementXUserAsset(username="v2-15-teammate", password="password", display_name="Lunch Teammate")
    room = ElementXRoomAsset(
        name="Client Lunch Candidates",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=["v2-15-teammate"],
        alias_localpart=ROOM_ALIAS,
        topic="Compare HMDP restaurants for the Oct 2 client lunch",
    )
    candidate_message = ElementXMessageAsset(
        room=ROOM_ALIAS,
        sender_username="v2-15-teammate",
        sender_password="password",
        text="HMDP shortlist for the client lunch: Acme Oyster House, Commander's Palace, and Willa Jean. Please compare against the client's constraints before confirming.",
        created_at_ms=utc_ms(2026, 10, 1, 9),
    )
    cafe_distractor = ElementXMessageAsset(
        room=ROOM_ALIAS,
        sender_username="v2-15-teammate",
        sender_password="password",
        text="Cafe Beignet came up for breakfast last month; keeping that breakfast thread separate from the lunch shortlist discussion.",
        created_at_ms=utc_ms(2026, 10, 1, 9, 8),
    )
    route_message = ElementXMessageAsset(
        room=ROOM_ALIAS,
        sender_username="v2-15-teammate",
        sender_password="password",
        text="The board-prep block at 14:00 is the hard stop, so a long return trip would be a problem.",
        created_at_ms=utc_ms(2026, 10, 1, 9, 15),
    )

    busy_after_lunch = CalendarEventAsset(
        title="Board prep lockout",
        start_ms=utc_ms(2026, 10, 2, 14),
        end_ms=utc_ms(2026, 10, 2, 15),
        timezone="UTC",
        location="Office 9F",
        description="No long travel buffer before this meeting.",
    )
    morning_meeting = CalendarEventAsset(
        title="Client deck review",
        start_ms=utc_ms(2026, 10, 2, 10),
        end_ms=utc_ms(2026, 10, 2, 11),
        timezone="UTC",
        location="Office 9F",
    )
    lunch_hold = CalendarEventAsset(
        title="Client Lunch Hold",
        start_ms=utc_ms(2026, 10, 2, 12, 30),
        end_ms=utc_ms(2026, 10, 2, 13, 30),
        description="Finalize HMDP restaurant from candidate list.",
        timezone="UTC",
    )
    lunch_event = CalendarEventAsset(
        title="Client Lunch - Willa Jean",
        start_ms=utc_ms(2026, 10, 2, 12, 30),
        end_ms=utc_ms(2026, 10, 2, 13, 30),
        location="Willa Jean",
        description="Selected Willa Jean: 70 per person, within 80 budget, before 14:00 Board prep lockout.",
        timezone="UTC",
        reminder_minutes=(30,),
    )

    hmdp_user = HmdpUserAsset(
        phone=HMDP_LOGIN_PHONE,
        password=HMDP_LOGIN_PASSWORD,
        nick_name=HMDP_LOGIN_NICKNAME,
        icon=HMDP_DEFAULT_ICON,
        city="New Orleans",
    )

    assets = (
        account,
        client_mail,
        old_client_mail,
        account_note,
        teammate,
        room,
        candidate_message,
        cafe_distractor,
        route_message,
        ElementXSessionAsset(username="testuser", password="testpass123"),
        busy_after_lunch,
        morning_meeting,
        lunch_hold,
        hmdp_user,
    )
    goal = (
        "Please finalize the client lunch from the HMDP restaurant candidates the team discussed. Use Mail to find the client constraints "
        "and reply details, ElementX to find the restaurant shortlist and internal schedule concern, HMDP shop details to compare visible "
        "candidate prices and menu tags, and Calendar to update the existing lunch hold. Save the selected HMDP restaurant. Modify the "
        "existing Calendar hold with title 'Client Lunch - <selected restaurant>', location '<selected restaurant>', a 30-minute reminder, "
        "and description exactly in this format: 'Selected <selected restaurant>: <selected average price integer> per person, within <per-person "
        "budget> budget, before <hard-stop time> <hard-stop short label>.'. Send Mail to the client coordinator with subject "
        "'Client lunch confirmed: <selected restaurant>' and body exactly in this format: 'Confirmed <selected restaurant> for <date> at "
        "<time>. It is <selected average price integer> per person and stays under the <per-person budget> per person budget.'. Send the ElementX "
        "group exactly in this format: 'Client lunch selected: <selected restaurant>. <selected restaurant> is <selected average price integer> "
        "per person and fits before the <hard-stop time> <hard-stop short label>.'. Use the evidence values, not the placeholders. "
        "For <hard-stop short label>, use the exact title of the Calendar hard-stop event. "
        "Use these examples for formatting only: <selected average price integer> '55'; <per-person budget> '90'; "
        "<date> 'September 14'; <time> '9:15'; <hard-stop time> '15:30'."
    )

    user_interaction = (
        "If the agent asks which Mail recipient should receive the client lunch confirmation, answer exactly: "
        "Send it to client.coordinator@example.com."
    )

    def criteria(self):
        return [
            AssetExists(HmdpShopFavoriteAsset(user_phone=HMDP_LOGIN_PHONE, shop_name=SELECTED_RESTAURANT), task=self),
            AssetModified(self.lunch_hold, self.lunch_event, task=self),
            AssetExists(self.expected_reply, task=self),
            AssetExists(ElementXMessageAsset(room=ROOM_ALIAS, sender_username="testuser", sender_password="testpass123", text=TEAM_UPDATE), task=self),
        ]
