from __future__ import annotations

from datetime import UTC, datetime

from gma.apps.hmdp import HMDP_DEFAULT_ICON, HMDP_LOGIN_NICKNAME, HMDP_LOGIN_PASSWORD, HMDP_LOGIN_PHONE
from gma.apps.meituan import MEITUAN_LOGIN_CITY, MEITUAN_LOGIN_USER_ID, MEITUAN_LOGIN_USERNAME
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
    ElementXPollAsset,
    ElementXPollResponse,
    ElementXRoomAsset,
    ElementXUserAsset,
    HmdpUserAsset,
    MailAccountAsset,
    MailMessageAsset,
    MeituanAddressAsset,
    MeituanOrderAsset,
    MeituanOrderFood,
    MeituanUserAsset,
    SmsMessageAsset,
    TravelHotelBookingAsset,
    TravelUserAsset,
)
from gma.evaluation import AssetExists
from gma.tasks.base import BaseTask


def dt_ms(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


TRAVEL_USER = TravelUserAsset(
    email=TRAVEL_LOGIN_EMAIL,
    username=TRAVEL_LOGIN_USERNAME,
    password=TRAVEL_LOGIN_PASSWORD,
    first_name=TRAVEL_LOGIN_FIRST_NAME,
    last_name=TRAVEL_LOGIN_LAST_NAME,
)
HOTEL_SLUG = "country-residence-hotel-extended-stay-lat36.107281-lon-86.816017"
HOTEL_NAME = "Country Residence Hotel"
HOTEL_STREET_ADDRESS = "2126 Abbott Martin Rd, Nashville, USA"
MEITUAN_RECIPIENT_NAME = "Morgan Carter"
MEITUAN_RECIPIENT_PHONE = "5550102201"

DINNER_EVENT = CalendarEventAsset(
    title="Weekend dinner: Acme Oyster House",
    start_ms=dt_ms(2026, 10, 3, 18, 30),
    end_ms=dt_ms(2026, 10, 3, 20, 0),
    description="Chosen from HMDP shop details: prioritized casual dinner, score 4.3, average price 70.",
    location="Acme Oyster House",
    timezone="UTC",
    reminder_minutes=(30,),
)
BREAKFAST_EVENT = CalendarEventAsset(
    title="Weekend breakfast: Cafe Beignet on Royal Street",
    start_ms=dt_ms(2026, 10, 4, 9, 0),
    end_ms=dt_ms(2026, 10, 4, 10, 0),
    description="Breakfast slot from the existing Travel hotel window; selected from the food brief.",
    location="Cafe Beignet on Royal Street",
    timezone="UTC",
    reminder_minutes=(30,),
)
DESSERT_EVENT = CalendarEventAsset(
    title="Meituan dessert order: Mixue Ice Cream & Tea",
    start_ms=dt_ms(2026, 10, 4, 15, 30),
    end_ms=dt_ms(2026, 10, 4, 16, 0),
    description="Order three Crispy sundaes for the group dessert snack before late checkout.",
    location=HOTEL_NAME,
    timezone="UTC",
    reminder_minutes=(15,),
)
EXPECTED_MEITUAN_ADDRESS = MeituanAddressAsset(
    user_id=MEITUAN_LOGIN_USER_ID,
    name=MEITUAN_RECIPIENT_NAME,
    phone=MEITUAN_RECIPIENT_PHONE,
    address=HOTEL_STREET_ADDRESS,
    address_detail=HOTEL_NAME,
    label="Work",
    gender="female",
    city="Nashville",
)
EXPECTED_ORDER = MeituanOrderAsset(
    user_id=MEITUAN_LOGIN_USER_ID,
    restaurant_name="Mixue Ice Cream & Tea",
    foods=[MeituanOrderFood(food_name="Crispy sundae", quantity=3)],
    status="Payment successful",
    address_name=MEITUAN_RECIPIENT_NAME,
    code=200,
    delivery_status=1,
)
FINAL_MESSAGE = (
    "Weekend food plan: Saturday dinner at Acme Oyster House for the casual dinner vote; "
    "Sunday breakfast at Cafe Beignet on Royal Street; Sunday snack is three Crispy sundaes from "
    "Mixue Ice Cream & Tea delivered to Country Residence Hotel."
)


class WeekendCityItineraryTask(BaseTask):
    apps = {"Travel", "HMDP", "Mail", "Meituan", "Calendar", "ElementX", "Messages"}
    difficulty = "realistic"
    category = ['Information-Gathering Tasks', 'Selection / Optimization Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    max_steps = 180

    assets = (
        TRAVEL_USER,
        MailAccountAsset(display_name="Morgan Carter", email="morgan.carter@example.com"),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Maya Food",
            from_email="maya.food@example.com",
            to=["morgan.carter@example.com"],
            subject="Nashville weekend food brief",
            body=(
                "Use this food brief for the Nashville weekend itinerary. "
                "The group priority vote should drive the dinner choice; casual dinner is the priority to satisfy first. "
                "Dinner slot: Saturday October 3, 18:30-20:00, with a 30-minute reminder. "
                "Acme Oyster House works as the casual dinner stop; use HMDP shop details for its score and average price, and note that non-spicy seafood plates are easy to split. "
                "Breakfast: Cafe Beignet on Royal Street is the Sunday 9 AM breakfast pick; hold one hour and set a 30-minute reminder. "
                "Jim's South St is normally a lunch candidate, but the weekend menu note says the cheesesteak tray is not listed, so skip it for this itinerary. "
                "Dessert order slot: Sunday October 4, 15:30-16:00 in the hotel gap, with a 15-minute reminder. "
                "Snack count is three people. Mixue Ice Cream & Tea has Crispy sundae at 6.6 each; Peach season spring is a drink, and ZHANGLIANG hotpot is a meal-style spicy option rather than a hotel snack."
            ),
            timestamp_ms=dt_ms(2026, 10, 1, 9, 30),
            read=False,
        ),
        TravelHotelBookingAsset(
            user_email=TRAVEL_USER.email,
            hotel_slug=HOTEL_SLUG,
            check_in_ms=dt_ms(2026, 10, 3, 15, 0),
            check_out_ms=dt_ms(2026, 10, 4, 17, 0),
            guest_first_name="Morgan",
            guest_last_name="Carter",
            guest_phone="5550102201",
            guest_count=1,
            room_count=1,
            total_price=210.0,
        ),
        CalendarEventAsset(
            title="Nashville arrival and hotel check-in",
            start_ms=dt_ms(2026, 10, 3, 15, 0),
            end_ms=dt_ms(2026, 10, 3, 16, 0),
            description="Travel booking at Country Residence Hotel.",
            location=HOTEL_NAME,
            timezone="UTC",
        ),
        CalendarEventAsset(
            title="Downtown photo walk",
            start_ms=dt_ms(2026, 10, 3, 12, 0),
            end_ms=dt_ms(2026, 10, 3, 14, 30),
            description="Blocks Saturday lunch.",
            timezone="UTC",
        ),
        CalendarEventAsset(
            title="Museum timed entry",
            start_ms=dt_ms(2026, 10, 4, 11, 30),
            end_ms=dt_ms(2026, 10, 4, 13, 30),
            description="Blocks Sunday lunch window.",
            timezone="UTC",
        ),
        CalendarEventAsset(
            title="Late checkout packing",
            start_ms=dt_ms(2026, 10, 4, 16, 15),
            end_ms=dt_ms(2026, 10, 4, 17, 0),
            description="Leave hotel after the afternoon snack window.",
            location=HOTEL_NAME,
            timezone="UTC",
        ),
        HmdpUserAsset(
            phone=HMDP_LOGIN_PHONE,
            password=HMDP_LOGIN_PASSWORD,
            nick_name=HMDP_LOGIN_NICKNAME,
            icon=HMDP_DEFAULT_ICON,
            city="Nashville",
        ),
        MeituanUserAsset(
            username=MEITUAN_LOGIN_USERNAME,
            password="123456",
            user_id=MEITUAN_LOGIN_USER_ID,
            city=MEITUAN_LOGIN_CITY,
            status=1,
        ),
        MeituanAddressAsset(
            user_id=MEITUAN_LOGIN_USER_ID,
            name="Downtown Apartment",
            phone="5550102202",
            address="120 Broadway",
            address_detail="Apt 6C",
            label="Home",
            city="Nashville",
        ),
        ElementXUserAsset(username="nashville-planner", password="password", display_name="Nashville Planner"),
        ElementXUserAsset(username="maya-food", password="password", display_name="Maya Food"),
        ElementXUserAsset(username="leo-food", password="password", display_name="Leo Food"),
        ElementXUserAsset(username="noah-logistics", password="password", display_name="Noah Logistics"),
        ElementXRoomAsset(
            name="Nashville Food Weekend",
            room_type="group",
            creator_username="nashville-planner",
            creator_password="password",
            members=["testuser", "maya-food", "leo-food", "noah-logistics"],
            alias_localpart="nashville-food-weekend",
            topic="Food planning around the existing Nashville hotel booking",
        ),
        ElementXPollAsset(
            room="nashville-food-weekend",
            sender_username="nashville-planner",
            sender_password="password",
            question="Weekend food priority?",
            options=["Casual dinner", "Breakfast", "Hot chicken", "Dessert"],
            responses=[
                ElementXPollResponse(username="nashville-planner", password="password", option="Casual dinner"),
                ElementXPollResponse(username="maya-food", password="password", option="Breakfast"),
                ElementXPollResponse(username="leo-food", password="password", option="Dessert"),
                ElementXPollResponse(username="noah-logistics", password="password", option="Casual dinner"),
            ],
            created_at_ms=dt_ms(2026, 10, 1, 10, 0),
        ),
        ElementXMessageAsset(
            room="nashville-food-weekend",
            sender_username="noah-logistics",
            sender_password="password",
            text="The hotel is already handled in Travel. Use the Mail food brief for restaurant details and schedule the food stops around the existing Calendar. Please post the final food plan here.",
            created_at_ms=dt_ms(2026, 10, 1, 10, 4),
        ),
        ContactAsset(name="Avery Food Constraint", phone_number="+1555202202"),
        ContactAsset(name="Riley Coffee Note", phone_number="+1555202203"),
        ContactAsset(name="Jordan Budget Note", phone_number="+1555202204"),
        SmsMessageAsset(
            address="+1555202202",
            body="For Nashville, Avery had a bad time with hot chicken last trip. Please keep the paid delivery snack sweet or cold later in the day, not as breakfast; drinks are already covered.",
            box="inbox",
            timestamp_ms=dt_ms(2026, 10, 1, 10, 30),
            read=False,
        ),
        SmsMessageAsset(
            address="+1555202203",
            body="Coffee is optional for me. If breakfast is pastries, I am fine without a separate cafe stop.",
            box="inbox",
            timestamp_ms=dt_ms(2026, 10, 1, 10, 36),
            read=True,
        ),
        SmsMessageAsset(
            address="+1555202204",
            body="I can cover dinner if it stays around the usual casual range. No need to optimize for the absolute cheapest place.",
            box="inbox",
            timestamp_ms=dt_ms(2026, 10, 1, 10, 40),
            read=True,
        ),
    )

    goal = (
        "Please turn our Nashville weekend trip into a food itinerary. The hotel is already booked in Travel, so use that existing booking only for the stay window and pay with Alipay for any Meituan order. Use Calendar conflicts, the Mail food brief, HMDP shop details, ElementX food-category vote, private Messages food constraints, and supported Meituan options. "
        "Add Calendar events for the selected dinner, breakfast, and dessert order. Use title formats 'Weekend dinner: <dinner place>', 'Weekend breakfast: <breakfast place>', and 'Meituan dessert order: <Meituan restaurant>'. Use the time windows and reminders from the itinerary evidence. Use these exact description formats: dinner 'Chosen from HMDP shop details: prioritized <winning food priority lowercase>, score <score>, average price <average price>.'; breakfast 'Breakfast slot from the existing Travel hotel window; selected from the food brief.'; dessert 'Order <quantity word and plural item> for the group dessert snack before late checkout.'. For the dinner description score and average price, use HMDP shop details. "
        "Create a Meituan address for the hotel using the receiver details from user interaction, the full hotel address from the Travel booking in Street, the hotel name in Apt, and label Work. Place the supported dessert order to this address. Send Nashville Food Weekend exactly: 'Weekend food plan: Saturday dinner at <dinner place> for the <winning food priority lowercase> vote; Sunday breakfast at <breakfast place>; Sunday snack is <quantity word and plural item> from <Meituan restaurant> delivered to <hotel>.'."
    )

    user_interaction = (
        "If the agent asks for Meituan delivery recipient details for the Nashville dessert order, answer exactly: "
        "Use receiver name Morgan Carter, gender female, select Ms, phone 5550102201."
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
            AssetExists(DINNER_EVENT, task=self),
            AssetExists(BREAKFAST_EVENT, task=self),
            AssetExists(DESSERT_EVENT, task=self),
            AssetExists(EXPECTED_MEITUAN_ADDRESS, task=self),
            AssetExists(EXPECTED_ORDER, task=self),
            AssetExists(
                ElementXMessageAsset(
                    room="nashville-food-weekend",
                    sender_username="testuser",
                    sender_password="testpass123",
                    text=FINAL_MESSAGE,
                ),
                task=self,
            ),
        ]
