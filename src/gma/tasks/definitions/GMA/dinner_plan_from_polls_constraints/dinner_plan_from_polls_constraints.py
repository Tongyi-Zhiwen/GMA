from __future__ import annotations

from datetime import UTC, datetime

from gma.assets import (
    CalendarEventAsset,
    ContactAsset,
    ElementXMessageAsset,
    ElementXPollAsset,
    ElementXPollResponse,
    ElementXRoomAsset,
    ElementXSessionAsset,
    ElementXUserAsset,
    MailAccountAsset,
    MailMessageAsset,
    SmsMessageAsset,
)
from gma.evaluation import AssetExists
from gma.tasks.base import BaseTask


def dt_ms(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


ROOM_ALIAS = "v2-02-dinner-planning-group"
FINAL_ELEMENTX_MESSAGE = (
    "Dinner Planning Group: cuisine Vegetarian noodles; tied option Spicy hotpot rejected; "
    "time October 3, 2026 7:00 PM; budget Under 80 total; venue Order in."
)
FINAL_SMS = "Dinner Planning Group: Vegetarian noodles, Oct 3 7:00 PM, under 80 total, order in."


class DinnerPlanFromPollsConstraintsTask(BaseTask):
    apps = {"ElementX", "Mail", "Calendar", "Messages"}
    difficulty = "realistic"
    category = ['Selection / Optimization Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    max_steps = 170

    users = (
        ElementXUserAsset(username="v2-02-avery", display_name="Avery"),
        ElementXUserAsset(username="v2-02-blake", display_name="Blake"),
        ElementXUserAsset(username="v2-02-casey", display_name="Casey"),
        ElementXUserAsset(username="v2-02-jordan", display_name="Jordan"),
    )
    room = ElementXRoomAsset(
        name="Dinner Planning Group",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=[user.username for user in users],
        alias_localpart=ROOM_ALIAS,
        topic="Dinner planning",
    )
    old_cuisine_poll = ElementXPollAsset(
        room=ROOM_ALIAS,
        sender_username="v2-02-jordan",
        question="Sep 30 draft cuisine for Saturday dinner",
        options=["Vegetarian noodles", "Spicy hotpot", "Pizza"],
        responses=[
            ElementXPollResponse(username="v2-02-avery", option="Vegetarian noodles"),
            ElementXPollResponse(username="v2-02-blake", option="Spicy hotpot"),
            ElementXPollResponse(username="v2-02-jordan", option="Spicy hotpot"),
            ElementXPollResponse(username="testuser", option="Spicy hotpot", password="testpass123"),
            ElementXPollResponse(username="v2-02-casey", option="Pizza"),
        ],
        created_at_ms=dt_ms(2026, 9, 30, 16),
    )
    old_time_poll = ElementXPollAsset(
        room=ROOM_ALIAS,
        sender_username="v2-02-casey",
        question="Sep 30 draft dinner time",
        options=["6:30 PM", "7:00 PM", "7:30 PM"],
        responses=[
            ElementXPollResponse(username="v2-02-avery", option="7:30 PM"),
            ElementXPollResponse(username="v2-02-blake", option="7:30 PM"),
            ElementXPollResponse(username="v2-02-jordan", option="7:30 PM"),
            ElementXPollResponse(username="v2-02-casey", option="7:00 PM"),
        ],
        created_at_ms=dt_ms(2026, 9, 30, 16, 15),
    )
    old_budget_poll = ElementXPollAsset(
        room=ROOM_ALIAS,
        sender_username="v2-02-blake",
        question="Sep 30 draft dinner budget",
        options=["Under 80 total", "Under 120 total", "No budget limit"],
        responses=[
            ElementXPollResponse(username="v2-02-avery", option="Under 120 total"),
            ElementXPollResponse(username="v2-02-blake", option="Under 120 total"),
            ElementXPollResponse(username="v2-02-jordan", option="Under 120 total"),
            ElementXPollResponse(username="v2-02-casey", option="Under 80 total"),
        ],
        created_at_ms=dt_ms(2026, 9, 30, 16, 30),
    )
    old_venue_poll = ElementXPollAsset(
        room=ROOM_ALIAS,
        sender_username="v2-02-avery",
        question="Sep 30 draft venue mode",
        options=["Order in", "Go out"],
        responses=[
            ElementXPollResponse(username="v2-02-avery", option="Go out"),
            ElementXPollResponse(username="v2-02-blake", option="Go out"),
            ElementXPollResponse(username="v2-02-jordan", option="Go out"),
            ElementXPollResponse(username="v2-02-casey", option="Order in"),
        ],
        created_at_ms=dt_ms(2026, 9, 30, 16, 45),
    )
    cuisine_poll = ElementXPollAsset(
        room=ROOM_ALIAS,
        sender_username="v2-02-avery",
        question="Saturday dinner cuisine",
        options=["Vegetarian noodles", "Spicy hotpot", "Pizza"],
        responses=[
            ElementXPollResponse(username="v2-02-avery", option="Vegetarian noodles"),
            ElementXPollResponse(username="v2-02-casey", option="Vegetarian noodles"),
            ElementXPollResponse(username="v2-02-blake", option="Spicy hotpot"),
            ElementXPollResponse(username="v2-02-jordan", option="Spicy hotpot"),
            ElementXPollResponse(username="testuser", option="Pizza", password="testpass123"),
        ],
        created_at_ms=dt_ms(2026, 10, 1, 9),
    )
    time_poll = ElementXPollAsset(
        room=ROOM_ALIAS,
        sender_username="v2-02-blake",
        question="Saturday dinner time",
        options=["6:30 PM", "7:00 PM", "7:30 PM"],
        responses=[
            ElementXPollResponse(username="v2-02-avery", option="7:00 PM"),
            ElementXPollResponse(username="v2-02-blake", option="7:00 PM"),
            ElementXPollResponse(username="v2-02-casey", option="7:30 PM"),
            ElementXPollResponse(username="v2-02-jordan", option="7:30 PM"),
        ],
        created_at_ms=dt_ms(2026, 10, 1, 9, 15),
    )
    budget_poll = ElementXPollAsset(
        room=ROOM_ALIAS,
        sender_username="v2-02-casey",
        question="Saturday dinner budget",
        options=["Under 80 total", "Under 120 total", "No budget limit"],
        responses=[
            ElementXPollResponse(username="v2-02-avery", option="Under 80 total"),
            ElementXPollResponse(username="v2-02-blake", option="Under 80 total"),
            ElementXPollResponse(username="v2-02-jordan", option="Under 80 total"),
            ElementXPollResponse(username="v2-02-casey", option="Under 120 total"),
        ],
        created_at_ms=dt_ms(2026, 10, 1, 9, 30),
    )
    venue_poll = ElementXPollAsset(
        room=ROOM_ALIAS,
        sender_username="v2-02-jordan",
        question="Saturday dinner venue mode",
        options=["Order in", "Go out"],
        responses=[
            ElementXPollResponse(username="v2-02-avery", option="Order in"),
            ElementXPollResponse(username="v2-02-blake", option="Order in"),
            ElementXPollResponse(username="v2-02-casey", option="Order in"),
            ElementXPollResponse(username="v2-02-jordan", option="Go out"),
        ],
        created_at_ms=dt_ms(2026, 10, 1, 9, 45),
    )
    mail_account = MailAccountAsset(display_name="Morgan Dinner", email="morgan.dinner@example.com")
    mail_constraints = (
        MailMessageAsset(
            mailbox="inbox",
            from_name="Avery",
            from_email="avery@example.com",
            to=[mail_account.email],
            subject="Early dinner preference",
            body="I usually like vegetarian noodles, but treat that as a preference until I send a hard constraint.",
            timestamp_ms=dt_ms(2026, 9, 30, 17),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Blake",
            from_email="blake@example.com",
            to=[mail_account.email],
            subject="Early spice note",
            body="Mild spice would probably be fine if the group wants it.",
            timestamp_ms=dt_ms(2026, 9, 30, 17, 20),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Jordan",
            from_email="jordan@example.com",
            to=[mail_account.email],
            subject="Early budget note",
            body="For a special venue, under 120 total would be acceptable.",
            timestamp_ms=dt_ms(2026, 9, 30, 17, 40),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Riley",
            from_email="riley@example.com",
            to=[mail_account.email],
            subject="Dinner idea",
            body="I can help with pizza pickup if the group ends up choosing pizza, but I do not have a dietary constraint.",
            timestamp_ms=dt_ms(2026, 10, 1, 10, 30),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Avery",
            from_email="avery@example.com",
            to=[mail_account.email],
            subject="Dinner dietary restriction",
            body="I need a vegetarian option for dinner.",
            timestamp_ms=dt_ms(2026, 10, 1, 11),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Blake",
            from_email="blake@example.com",
            to=[mail_account.email],
            subject="Dinner spice constraint",
            body="I cannot eat spicy food this weekend.",
            timestamp_ms=dt_ms(2026, 10, 1, 11, 20),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Casey",
            from_email="casey@example.com",
            to=[mail_account.email],
            subject="Dinner duration",
            body="Please keep the dinner window to 25 minutes.",
            timestamp_ms=dt_ms(2026, 10, 1, 11, 40),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Jordan",
            from_email="jordan@example.com",
            to=[mail_account.email],
            subject="Dinner budget",
            body="Please keep the dinner under 80 total.",
            timestamp_ms=dt_ms(2026, 10, 1, 12),
            read=False,
        ),
    )
    conflict_event = CalendarEventAsset(
        title="Remote project sync",
        start_ms=dt_ms(2026, 10, 3, 19, 30),
        end_ms=dt_ms(2026, 10, 3, 20, 0),
        description="Standing Saturday evening project call.",
        timezone="UTC",
    )
    saturday_errand_event = CalendarEventAsset(
        title="Grocery pickup",
        start_ms=dt_ms(2026, 10, 3, 17, 0),
        end_ms=dt_ms(2026, 10, 3, 17, 30),
        description="Pick up drinks and snacks before the evening.",
        timezone="UTC",
    )
    saturday_cleanup_event = CalendarEventAsset(
        title="Kitchen cleanup",
        start_ms=dt_ms(2026, 10, 3, 20, 30),
        end_ms=dt_ms(2026, 10, 3, 21, 0),
        description="Clean up after the evening plans.",
        timezone="UTC",
    )
    sunday_brunch_event = CalendarEventAsset(
        title="Sunday brunch check-in",
        start_ms=dt_ms(2026, 10, 4, 10, 30),
        end_ms=dt_ms(2026, 10, 4, 11, 15),
        description="Follow-up brunch plan with Avery.",
        timezone="UTC",
    )
    distractor_event = CalendarEventAsset(
        title="Friday pizza pickup idea",
        start_ms=dt_ms(2026, 10, 2, 19, 0),
        end_ms=dt_ms(2026, 10, 2, 20, 0),
        description="Earlier Friday dinner idea with Riley; separate from the Saturday group dinner.",
        timezone="UTC",
    )
    jordan_contact = ContactAsset(name="Jordan Miller", phone_number="+15552012650")
    spicy_hotpot_distractor = SmsMessageAsset(
        address=jordan_contact.phone_number,
        body="I was originally leaning toward spicy hotpot if the cuisine poll is close.",
        box="inbox",
        read=False,
        timestamp_ms=dt_ms(2026, 10, 1, 13),
    )
    tie_breaker = SmsMessageAsset(
        address=jordan_contact.phone_number,
        body="If a poll ties, hard attendee constraints beat preferences; pick the tied option that satisfies every hard constraint.",
        box="inbox",
        read=False,
        timestamp_ms=dt_ms(2026, 10, 1, 15),
    )
    expected_event = CalendarEventAsset(
        title="Dinner Planning Group dinner",
        start_ms=dt_ms(2026, 10, 3, 19, 0),
        end_ms=dt_ms(2026, 10, 3, 19, 25),
        location="Order in",
        description="Dinner Planning Group: Vegetarian noodles; Under 80 total; Order in.",
        timezone="UTC",
        reminder_minutes=(30,),
    )
    assets = (
        *users,
        room,
        old_cuisine_poll,
        old_time_poll,
        old_budget_poll,
        old_venue_poll,
        cuisine_poll,
        time_poll,
        budget_poll,
        venue_poll,
        ElementXSessionAsset(username="testuser", password="testpass123"),
        mail_account,
        *mail_constraints,
        conflict_event,
        saturday_errand_event,
        saturday_cleanup_event,
        sunday_brunch_event,
        distractor_event,
        jordan_contact,
        spicy_hotpot_distractor,
        tie_breaker,
    )

    goal = (
        "Open ElementX and review the dinner polls in Dinner Planning Group. Use the latest poll results, Mail constraints, "
        "Calendar availability, and relevant Messages tie-break instructions to decide the final dinner plan. "
        "Create a Calendar event titled exactly `Dinner Planning Group dinner` on the chosen date at the selected dinner time, using the maximum duration allowed by the Mail constraints, "
        "with location exactly `Order in`, a 30-minute reminder, and description using the format "
        "`Dinner Planning Group: <cuisine>; <budget>; <venue>.` Then send Dinner Planning Group an ElementX message using "
        "the format `Dinner Planning Group: cuisine <cuisine>; tied option <rejected cuisine> rejected; "
        "time <full date> <time>; budget <budget>; venue <venue>.` Finally send Jordan Miller an SMS using the format "
        "`Dinner Planning Group: <cuisine>, <short date> <time>, <budget lowercase>, <venue lowercase>.` Use the exact latest "
        "poll option text for cuisine, budget, and venue in the Calendar and ElementX outputs. For date and time formatting, "
        "examples use sample values only: write a full date like `January 2, 2026` for <full date>, a short date like "
        "`Jan 2` for <short date>, and only the selected start time, such as `5:45 PM`, for <time>; do not use a time range."
    )

    def criteria(self):
        return [
            AssetExists(self.expected_event, task=self),
            AssetExists(
                ElementXMessageAsset(
                    room=ROOM_ALIAS,
                    sender_username="testuser",
                    sender_password="testpass123",
                    text=FINAL_ELEMENTX_MESSAGE,
                ),
                task=self,
            ),
            AssetExists(SmsMessageAsset(address=self.jordan_contact.phone_number, body=FINAL_SMS, box="sent", read=True), task=self),
        ]
