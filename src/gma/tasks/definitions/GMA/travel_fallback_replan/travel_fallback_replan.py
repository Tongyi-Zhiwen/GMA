from __future__ import annotations

from datetime import UTC, datetime

from gma.apps.travel import (
    TRAVEL_LOGIN_EMAIL,
    TRAVEL_LOGIN_FIRST_NAME,
    TRAVEL_LOGIN_LAST_NAME,
    TRAVEL_LOGIN_PASSWORD,
    TRAVEL_LOGIN_USERNAME,
    login_travel_app,
)
from gma.assets import (
    CalendarEventAsset,
    ContactAsset,
    ElementXMessageAsset,
    ElementXRoomAsset,
    ElementXUserAsset,
    MailAccountAsset,
    MailMessageAsset,
    SmsMessageAsset,
    TravelFlightBookingAsset,
    TravelUserAsset,
)
from gma.evaluation import AssetExists
from gma.tasks.base import BaseTask


def dt_ms(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


TRAVEL_USER = TravelUserAsset(
    email=TRAVEL_LOGIN_EMAIL,
    username=TRAVEL_LOGIN_USERNAME,
    password=TRAVEL_LOGIN_PASSWORD,
    first_name=TRAVEL_LOGIN_FIRST_NAME,
    last_name=TRAVEL_LOGIN_LAST_NAME,
)
ACCOUNT = MailAccountAsset(display_name="Taylor Brooks", email="taylor.brooks@example.com")
ORIGINAL_BOOKING = TravelFlightBookingAsset(
    user_email=TRAVEL_LOGIN_EMAIL,
    from_airport="DXB",
    to_airport="LHR",
    flight_code="EK2156",
    departure_date_ms=dt_ms(2026, 10, 5, 0),
    passenger_first_name="Evan",
    passenger_last_name="Carter",
    passenger_email="254536854@gmail.com",
    passenger_phone="5550101116",
    passenger_phone_dial_code="+1",
    passenger_gender="female",
    passenger_country="United States",
    passenger_birth_ms=dt_ms(1990, 6, 18),
    passport_number="6536549879861",
    passport_expiry_ms=dt_ms(2028, 11, 20),
    passenger_count=1,
    seat_class="economy",
    payment_status="refunded",
    ticket_status="cancelled",
)
MAILS = (
    MailMessageAsset(
        mailbox="inbox",
        from_name="CloudBox Billing",
        from_email="billing@cloudbox.example.com",
        to=[ACCOUNT.email],
        subject="Storage renewal receipt",
        body="Your monthly CloudBox storage renewal processed successfully. No action is needed.",
        timestamp_ms=dt_ms(2026, 10, 1, 11, 5),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="City Reads",
        from_email="newsletter@cityreads.example.com",
        to=[ACCOUNT.email],
        subject="October reading list",
        body="This week's picks include essays on urban design, transit maps, and museum cafes.",
        timestamp_ms=dt_ms(2026, 10, 1, 10, 55),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Skywards Offers",
        from_email="offers@skywards.example.com",
        to=[ACCOUNT.email],
        subject="Premium cabin upgrade ideas",
        body="Selected London itineraries may show premium cabin upgrade prompts today. Review fare rules before changing class.",
        timestamp_ms=dt_ms(2026, 10, 1, 10, 45),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="London Weekly",
        from_email="events@londonweekly.example.com",
        to=[ACCOUNT.email],
        subject="Evening gallery openings",
        body="Several galleries have late openings this week. Most events begin after 7 PM and require separate tickets.",
        timestamp_ms=dt_ms(2026, 10, 1, 10, 35),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Transit Notice",
        from_email="notice@metro.example.com",
        to=[ACCOUNT.email],
        subject="Airport rail engineering notice",
        body="Weekend rail engineering work may add time to some airport transfers. Check same-day routing before leaving the terminal.",
        timestamp_ms=dt_ms(2026, 10, 1, 10, 25),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Fare Watch",
        from_email="farewatch@example.com",
        to=[ACCOUNT.email],
        subject="Late London fare alert",
        body="A cheaper fare alert appeared for a London arrival after the evening rush. It is useful for flexible leisure trips.",
        timestamp_ms=dt_ms(2026, 10, 1, 10, 15),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Connection Desk",
        from_email="connections@example.com",
        to=[ACCOUNT.email],
        subject="Two-stop routing note",
        body="Two-stop routings can reduce fare totals on some Dubai to London searches, but they add a long connection and a later arrival.",
        timestamp_ms=dt_ms(2026, 10, 1, 10, 5),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Hotel Points",
        from_email="points@hotelclub.example.com",
        to=[ACCOUNT.email],
        subject="London points balance",
        body="Your hotel points balance is ready for the autumn season. This notice does not include an active reservation.",
        timestamp_ms=dt_ms(2026, 10, 1, 9, 55),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Airport Lounge",
        from_email="lounge@airport.example.com",
        to=[ACCOUNT.email],
        subject="Lounge pass promotion",
        body="Single-use lounge passes are discounted this week for afternoon departures from DXB.",
        timestamp_ms=dt_ms(2026, 10, 1, 9, 45),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Calendar Digest",
        from_email="digest@example.com",
        to=[ACCOUNT.email],
        subject="Today at a glance",
        body="You have calendar items around client review, travel planning, and post-trip handoff this week.",
        timestamp_ms=dt_ms(2026, 10, 1, 9, 35),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Restaurant Club",
        from_email="tables@restaurantclub.example.com",
        to=[ACCOUNT.email],
        subject="London dinner openings",
        body="Popular dinner tables are available after 8 PM near the river this week.",
        timestamp_ms=dt_ms(2026, 10, 1, 9, 25),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Office Admin",
        from_email="admin@example.com",
        to=[ACCOUNT.email],
        subject="Printer maintenance window",
        body="The office printer maintenance window is scheduled for Friday afternoon.",
        timestamp_ms=dt_ms(2026, 10, 1, 9, 15),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Museum Friends",
        from_email="friends@museum.example.com",
        to=[ACCOUNT.email],
        subject="Member preview week",
        body="Member preview week begins next Monday. Bring your card for early entry.",
        timestamp_ms=dt_ms(2026, 10, 1, 9, 5),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Travel Gear",
        from_email="gear@example.com",
        to=[ACCOUNT.email],
        subject="Adapter and luggage sale",
        body="Adapters, packing cubes, and luggage scales are discounted for the next 48 hours.",
        timestamp_ms=dt_ms(2026, 10, 1, 8, 55),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Weather Brief",
        from_email="weather@example.com",
        to=[ACCOUNT.email],
        subject="London evening weather",
        body="Expect cool temperatures in London on October 5 with a chance of light rain after sunset.",
        timestamp_ms=dt_ms(2026, 10, 1, 8, 45),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Airline Alerts",
        from_email="alerts@example.com",
        to=[ACCOUNT.email],
        subject="EK2156 operational update",
        body="The planned DXB to LHR flight EK2156 for October 5 has been removed from the operating schedule, and refund processing has started for affected tickets. Cancellation code: LHR-REPLAN-7412.",
        timestamp_ms=dt_ms(2026, 10, 1, 7),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Travel Preferences",
        from_email="travel.preferences@example.com",
        to=[ACCOUNT.email],
        subject="London fallback priorities",
        body=(
            "For the London fallback, first protect arrival before the evening team meeting, then keep the replacement on the same "
            "airline as the disrupted EK booking if a feasible same-airline option is visible, then minimize layovers, then keep the "
            "booking in economy. Avoid any option that lands after the meeting window or conflicts with the calendar."
        ),
        timestamp_ms=dt_ms(2026, 10, 1, 7, 30),
        read=False,
    ),
)
ROOM_MEMBER = ElementXUserAsset(username="v2-12-trip-member", password="password", display_name="London Group Member")
ROOM = ElementXRoomAsset(
    name="London Trip Group",
    room_type="group",
    creator_username="testuser",
    creator_password="testpass123",
    members=[ROOM_MEMBER.username],
    alias_localpart="v2-12-london-trip",
    topic="London trip arrival planning.",
)
MEETING_MESSAGE = ElementXMessageAsset(
    room="v2-12-london-trip",
    sender_username=ROOM_MEMBER.username,
    sender_password="password",
    text="The team meeting in London starts October 5 at 7:00 PM. Please share the new arrival plan.",
    created_at_ms=dt_ms(2026, 10, 1, 8),
)
DIRECT_CONTACT = ContactAsset(name="Jordan Travel", phone_number="+15550121201")
AVOID_SMS = SmsMessageAsset(
    address=DIRECT_CONTACT.phone_number,
    body="For the fallback, please avoid late-night arrivals and anything that conflicts with the calendar. If a same-airline option is feasible, use it before switching airlines; keep it economy if possible.",
    box="inbox",
    read=True,
    timestamp_ms=dt_ms(2026, 10, 1, 8, 15),
)
CALENDAR_CONFLICTS = (
    CalendarEventAsset(title="Client review before travel", start_ms=dt_ms(2026, 10, 5, 5), end_ms=dt_ms(2026, 10, 5, 6), timezone="UTC"),
    CalendarEventAsset(title="Post-trip handoff", start_ms=dt_ms(2026, 10, 6, 10), end_ms=dt_ms(2026, 10, 6, 11), timezone="UTC"),
)
EXPECTED_BOOKING = TravelFlightBookingAsset(
    user_email=TRAVEL_LOGIN_EMAIL,
    from_airport="DXB",
    to_airport="LHR",
    flight_code="EK2106",
    departure_date_ms=dt_ms(2026, 10, 5, 12),
    passenger_first_name="Evan",
    passenger_last_name="Carter",
    passenger_email="254536854@gmail.com",
    passenger_phone="5550101116",
    passenger_phone_dial_code="+1",
    passenger_gender="female",
    passenger_country="United States",
    passenger_birth_ms=dt_ms(1990, 6, 18),
    passport_number="6536549879861",
    passport_expiry_ms=dt_ms(2028, 11, 20),
    passenger_count=1,
    seat_class="economy",
    payment_status="paid",
    ticket_status="confirmed",
)
TRIP_EVENT = CalendarEventAsset(
    title="Revised London flight EK2106",
    start_ms=dt_ms(2026, 10, 5, 12),
    end_ms=dt_ms(2026, 10, 5, 13),
    description="Fallback booking from DXB to LHR before the evening team meeting.",
    timezone="UTC",
    reminder_minutes=(180,),
)
GROUP_NOTICE = ElementXMessageAsset(
    room="v2-12-london-trip",
    sender_username="testuser",
    sender_password="testpass123",
    text="Rebooked fallback travel on Emirates EK2106 from DXB to LHR on October 5. Cancellation code LHR-REPLAN-7412. I will arrive before the 7:00 PM team meeting.",
)


class TravelFallbackReplanTask(BaseTask):
    apps = {"Travel", "Mail", "ElementX", "Calendar", "Messages"}
    difficulty = "realistic"
    category = ['Information-Gathering Tasks', 'Selection / Optimization Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    assets = (
        TRAVEL_USER,
        ORIGINAL_BOOKING,
        ACCOUNT,
        *MAILS,
        ROOM_MEMBER,
        ROOM,
        MEETING_MESSAGE,
        DIRECT_CONTACT,
        AVOID_SMS,
        *CALENDAR_CONFLICTS,
    )
    goal = (
        "My trip got disrupted. Use the existing Travel booking, Mail fallback priorities, ElementX meeting time, Messages constraint, and Calendar conflicts to book the feasible replacement for the disrupted October 5 Travel flight. Use only Travel options visible in the app, and finish payment so the replacement flight is confirmed. There is no seat, meal, or baggage preference. Include the cancellation code from the operational email in the group update. Add a one-hour Calendar event on the selected fallback flight date from 12:00 PM to 1:00 PM titled 'Revised London flight <flight code>' with description 'Fallback booking from <origin IATA> to <destination IATA> before the evening team meeting.' and a 180-minute reminder. For the ElementX group update, use Month D format for the date, such as January 2, and h:mm AM/PM format for the meeting time, such as 4:30 PM. Fill this exact template: 'Rebooked fallback travel on <airline name> <flight code> from <origin IATA> to <destination IATA> on <month day>. Cancellation code <cancellation code>. I will arrive before the <meeting time> team meeting.'."
    )
    user_interaction = (
        "If the agent asks for passenger details for the replacement flight, answer exactly: "
        "Use passenger Evan Carter, date of birth June 18, 1990, gender Female, nationality United States, "
        "email 254536854@gmail.com, country code +1, phone number 5550101116, passport number 6536549879861, "
        "passport expiry November 20, 2028, one adult passenger, economy class, with no seat, meal, or baggage preference."
    )

    def setup(self, client) -> None:
        login_travel_app(
            client,
            email=TRAVEL_LOGIN_EMAIL,
            username=TRAVEL_LOGIN_USERNAME,
            password=TRAVEL_LOGIN_PASSWORD,
            ensure_user=False,
        )

    def criteria(self):
        return [
            AssetExists(EXPECTED_BOOKING, task=self),
            AssetExists(TRIP_EVENT, task=self),
            AssetExists(GROUP_NOTICE, task=self),
        ]
