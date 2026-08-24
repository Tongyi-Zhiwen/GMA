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
    AlarmAsset,
    CalendarEventAsset,
    ContactAsset,
    ElementXMessageAsset,
    ElementXRoomAsset,
    ElementXUserAsset,
    MailAccountAsset,
    MailMessageAsset,
    SmsMessageAsset,
    TravelFlightBookingAsset,
    TravelHotelBookingAsset,
    TravelUserAsset,
)
from gma.evaluation import AssetExists
from gma.tasks.base import BaseTask


def dt_ms(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


def open_travel(client) -> None:
    login_travel_app(
        client,
        email=TRAVEL_LOGIN_EMAIL,
        username=TRAVEL_LOGIN_USERNAME,
        password=TRAVEL_LOGIN_PASSWORD,
        ensure_user=False,
    )


TRAVEL_USER = TravelUserAsset(
    email=TRAVEL_LOGIN_EMAIL,
    username=TRAVEL_LOGIN_USERNAME,
    password=TRAVEL_LOGIN_PASSWORD,
    first_name=TRAVEL_LOGIN_FIRST_NAME,
    last_name=TRAVEL_LOGIN_LAST_NAME,
    phone="5550101116",
)

MAIL_ACCOUNT = MailAccountAsset(display_name="Evan Carter", email="evan.carter@example.com")
ROOM_ALIAS = "v2-01-travel-planning-group"
TRIP_TITLE = "London Client Trip"
FLIGHT_AIRLINE = "Emirates"
FLIGHT_CODE = "EK2106"
FROM_CITY = "Dubai"
FROM_AIRPORT = "DXB"
TO_CITY = "London"
TO_AIRPORT = "LHR"
DEPARTURE_DATE = (2026, 10, 5)
DEPARTURE_DATE_LONG = "October 5, 2026"
DEPARTURE_DATE_SHORT = "Oct 5"
HOTEL = "Thames Riverside Inn"
HOTEL_SLUG = "thames-riverside-inn-luxury-lat51-4892-lon-0-1273"
HOTEL_ADDRESS = "378 Main St, London, England, 58908, United Kingdom"
CHECK_IN_DATE = (2026, 10, 5)
CHECK_OUT_DATE = (2026, 10, 8)
STAY_DATES_LONG = "October 5 to October 8, 2026"
STAY_DATES_SHORT = "Oct 5-Oct 8"
ALARM_LABEL = "London trip final check"

EVENT_DESCRIPTION = f"Final itinerary: {FLIGHT_AIRLINE} {FLIGHT_CODE} {FROM_AIRPORT} to {TO_AIRPORT}; hotel {HOTEL}."
FINAL_ELEMENTX_MESSAGE = (
    f"Final {TRIP_TITLE}: {FLIGHT_AIRLINE} {FLIGHT_CODE} from {FROM_AIRPORT} to {TO_AIRPORT} "
    f"on {DEPARTURE_DATE_LONG}. Hotel: {HOTEL}, {STAY_DATES_LONG}, {HOTEL_ADDRESS}."
)
FINAL_SMS = f"London trip confirmed: {FLIGHT_CODE} on {DEPARTURE_DATE_SHORT}, {HOTEL} {STAY_DATES_SHORT}."
FORMAT_RULES = (
    "Use the full airline name for <airline>, the full flight code for <flight code>, "
    "and three-letter IATA airport codes for <from airport> and <to airport>. "
    "For date formatting, use day-level dates. Examples use sample dates only: write a full date "
    'like "January 2, 2026" for <departure date>, <flight departure date>, and '
    '<hotel checkout date>; write a short date like "Jan 2" for <departure short date>; '
    'write full stay dates like "January 2 to January 5, 2026" for <stay dates>; and '
    'write short stay dates like "Jan 2-Jan 5" for <stay dates short>.'
)

CONFIRMED_BODY = "\n".join(
    [
        "CONFIRMED: for the London client trip, use the latest Travel Desk route option, "
        "the settled client schedule note, and the Client Team hotel recommendation.",
        "This supersedes the earlier London trip drafts and review copies.",
        "Use economy class for the flight booking.",
    ]
)


class TripReconcileMultiAppTask(BaseTask):
    apps = {"Mail", "Travel", "Calendar", "ElementX", "Messages", "Clock"}
    difficulty = "realistic"
    category = ['Information-Gathering Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    max_steps = 180

    old_proposal = MailMessageAsset(
        mailbox="inbox",
        from_name="Travel Desk",
        from_email="travel.desk@example.com",
        to=[MAIL_ACCOUNT.email],
        subject="Draft Tokyo to Dubai trip proposal - Sep 21 version",
        body="Version dated September 21: Japan Airlines JL1541 from HND to DXB for the early Tokyo-to-Dubai proposal.",
        timestamp_ms=dt_ms(2026, 9, 21, 9, 0),
        read=False,
    )
    cancelled_london = MailMessageAsset(
        mailbox="inbox",
        from_name="Travel Desk",
        from_email="travel.desk@example.com",
        to=[MAIL_ACCOUNT.email],
        subject="London route option - Sep 22",
        body="Travel Desk route option dated September 22: Emirates EK2156 from DXB to LHR.",
        timestamp_ms=dt_ms(2026, 9, 22, 10, 30),
        read=False,
    )
    early_timing = MailMessageAsset(
        mailbox="inbox",
        from_name="Scheduling Desk",
        from_email="scheduling@example.com",
        to=[MAIL_ACCOUNT.email],
        subject="London timing estimate - Sep 22",
        body="Scheduling estimate dated September 22: depart for London on October 2, 2026, with a hotel stay estimate of October 2 to October 4.",
        timestamp_ms=dt_ms(2026, 9, 22, 15, 10),
        read=False,
    )
    confirmed_hold = MailMessageAsset(
        mailbox="inbox",
        from_name="Travel Desk",
        from_email="travel.desk@example.com",
        to=[MAIL_ACCOUNT.email],
        subject="CONFIRMED London finance review copy - Sep 22",
        body=(
            "Finance review copy dated September 22: Emirates EK2156 from DXB to LHR, "
            "with the October 2 to October 4 London cost estimate."
        ),
        timestamp_ms=dt_ms(2026, 9, 22, 18, 5),
        read=False,
    )
    hotel_only = MailMessageAsset(
        mailbox="inbox",
        from_name="Client Team",
        from_email="client.team@example.com",
        to=[MAIL_ACCOUNT.email],
        subject="London hotel recommendation - Sep 23",
        body=f"Hotel recommendation copy dated September 23: {HOTEL} at {HOTEL_ADDRESS} for the London client trip file.",
        timestamp_ms=dt_ms(2026, 9, 23, 12, 0),
        read=False,
    )
    hotel_block_confirmed = MailMessageAsset(
        mailbox="inbox",
        from_name="Client Team",
        from_email="client.team@example.com",
        to=[MAIL_ACCOUNT.email],
        subject="CONFIRMED London hotel block - Sep 24",
        body=(
            f"Lodging copy dated September 24: {HOTEL} at {HOTEL_ADDRESS}. "
            "The travel desk copied this hotel block into the London client trip file."
        ),
        timestamp_ms=dt_ms(2026, 9, 24, 9, 15),
        read=False,
    )
    route_clarification = MailMessageAsset(
        mailbox="inbox",
        from_name="Travel Desk",
        from_email="travel.desk@example.com",
        to=[MAIL_ACCOUNT.email],
        subject="Latest London route option - Sep 24",
        body=(
            f"Latest Travel Desk route option dated September 24: {FLIGHT_AIRLINE} {FLIGHT_CODE} "
            f"from {FROM_CITY} {FROM_AIRPORT} to {TO_CITY} {TO_AIRPORT}."
        ),
        timestamp_ms=dt_ms(2026, 9, 24, 15, 40),
        read=False,
    )
    final_draft = MailMessageAsset(
        mailbox="inbox",
        from_name="Scheduling Desk",
        from_email="scheduling@example.com",
        to=[MAIL_ACCOUNT.email],
        subject="Settled London client schedule - Sep 25 morning",
        body=(
            f"Settled client schedule dated September 25: depart for London on {DEPARTURE_DATE_LONG}; "
            f"keep the hotel booking window as {STAY_DATES_LONG}."
        ),
        timestamp_ms=dt_ms(2026, 9, 25, 9, 10),
        read=False,
    )
    confirmed_plan = MailMessageAsset(
        mailbox="inbox",
        from_name="Travel Desk",
        from_email="travel.desk@example.com",
        to=[MAIL_ACCOUNT.email],
        subject="CONFIRMED London client trip final plan",
        body=CONFIRMED_BODY,
        timestamp_ms=dt_ms(2026, 9, 25, 16, 45),
        read=False,
    )
    distractor = MailMessageAsset(
        mailbox="inbox",
        from_name="London Events",
        from_email="events@example.com",
        to=[MAIL_ACCOUNT.email],
        subject="CONFIRMED London Eye ticket reminder",
        body="Ticketing note dated September 25: London Eye tickets are confirmed for sightseeing research next week.",
        timestamp_ms=dt_ms(2026, 9, 25, 17, 20),
        read=False,
    )
    flight_booking = TravelFlightBookingAsset(
        user_email=TRAVEL_USER.email,
        from_airport=FROM_AIRPORT,
        to_airport=TO_AIRPORT,
        departure_date_ms=dt_ms(*DEPARTURE_DATE, 12),
        flight_code=FLIGHT_CODE,
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
    hotel_booking = TravelHotelBookingAsset(
        user_email=TRAVEL_USER.email,
        hotel_name=HOTEL,
        hotel_slug=HOTEL_SLUG,
        check_in_ms=dt_ms(*CHECK_IN_DATE, 15),
        check_out_ms=dt_ms(*CHECK_OUT_DATE, 11),
        guest_first_name="Evan",
        guest_last_name="Carter",
        guest_phone="5550101116",
        guest_count=1,
        room_count=1,
        room_selections=[
            {
                "room_type": "Deluxe Room",
                "count": 1,
            }
        ],
        guests=[
            {
                "first_name": "Evan",
                "last_name": "Carter",
                "email": "254536854@gmail.com",
                "phone": "5550101116",
                "guest_type": "adult",
            }
        ],
        booking_status="confirmed",
        payment_status="paid",
    )
    trip_event = CalendarEventAsset(
        title=TRIP_TITLE,
        start_ms=dt_ms(*DEPARTURE_DATE, 9),
        end_ms=dt_ms(*CHECK_OUT_DATE, 18),
        location=HOTEL_ADDRESS,
        description=EVENT_DESCRIPTION,
        timezone="UTC",
    )
    group_member = ElementXUserAsset(username="v2-01-travel-member", display_name="Travel Planning Member")
    group_room = ElementXRoomAsset(
        name="Travel Planning Group",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=[group_member.username],
        alias_localpart=ROOM_ALIAS,
        topic="Trip planning updates",
    )
    jordan = ContactAsset(name="Jordan Miller", phone_number="+15552012650")
    trip_alarm = AlarmAsset(
        hour=7,
        minute=0,
        label=ALARM_LABEL,
        enabled=True,
        days_of_week=(),
        vibrate=True,
        scheduled_year=DEPARTURE_DATE[0],
        scheduled_month=DEPARTURE_DATE[1],
        scheduled_day=DEPARTURE_DATE[2],
    )
    assets = (
        TRAVEL_USER,
        MAIL_ACCOUNT,
        old_proposal,
        cancelled_london,
        early_timing,
        confirmed_hold,
        hotel_only,
        hotel_block_confirmed,
        route_clarification,
        final_draft,
        confirmed_plan,
        distractor,
        group_member,
        group_room,
        jordan,
    )

    goal = (
        'Open Mail and find the confirmed final approval for the London client trip. Use the route, timing, '
        'and hotel source emails named by that approval to determine the itinerary, then book the required Travel flight and hotel and finish payment for both the flight and hotel. There is no seat, meal, or baggage preference. After the bookings are confirmed, '
        'create a Calendar event with title exactly "London Client Trip", location exactly the booked hotel '
        'address, and description using the format "Final itinerary: <airline> <flight code> <from airport> '
        'to <to airport>; hotel <hotel name>." Set the event from <flight departure date> 9:00 AM to '
        '<hotel checkout date> 6:00 PM. Notify Travel Planning Group in ElementX using the format '
        '"Final London Client Trip: <airline> <flight code> from <from airport> to <to airport> on '
        '<departure date>. Hotel: <hotel name>, <stay dates>, <hotel address>." Send Jordan Miller an SMS '
        'using the format "London trip confirmed: <flight code> on <departure short date>, <hotel name> '
        '<stay dates short>." Set a Clock alarm on <flight departure date> at 7:00 AM with vibration enabled and label exactly '
        '"London trip final check". '
        + FORMAT_RULES
    )
    user_interaction = (
        "If the agent asks which London flight to choose, answer: Use Emirates EK2106. "
        "If the agent asks which hotel room type to book, answer: Use one Deluxe Room. "
        "If the agent asks for passenger, guest, passport, or contact details for the Travel booking, answer: "
        "Use passenger and guest Evan Carter. Date of birth June 18, 1990. Gender Female. Nationality United States. "
        "Passport number 6536549879861, passport expiry November 20, 2028. Email 254536854@gmail.com. "
        "US phone +1 5550101116. Book one adult passenger, one hotel guest, and one room. "
        "Use economy class and no seat, meal, or baggage preference."
    )

    def setup(self, client) -> None:
        open_travel(client)

    def criteria(self):
        return [
            AssetExists(self.flight_booking, task=self),
            AssetExists(self.hotel_booking, task=self),
            AssetExists(self.trip_event, task=self),
            AssetExists(
                ElementXMessageAsset(
                    room=ROOM_ALIAS,
                    sender_username="testuser",
                    sender_password="testpass123",
                    text=FINAL_ELEMENTX_MESSAGE,
                ),
                task=self,
            ),
            AssetExists(SmsMessageAsset(address=self.jordan.phone_number, body=FINAL_SMS, box="sent", read=True), task=self),
            AssetExists(self.trip_alarm, task=self),
        ]
