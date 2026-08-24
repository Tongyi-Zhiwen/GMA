from __future__ import annotations

from datetime import UTC, datetime

from gma.apps.mall import MALL_LOGIN_CITY, MALL_LOGIN_NICKNAME, MALL_LOGIN_USERNAME
from gma.assets import (
    AlarmAsset,
    CalendarEventAsset,
    ContactAsset,
    MailAccountAsset,
    MailMessageAsset,
    MallAddressAsset,
    MallMemberAsset,
    SmsMessageAsset,
)
from gma.evaluation import AssetExists
from gma.evaluation.checks.mall import MallCheckoutOrderCreated
from gma.tasks.base import BaseTask


def dt_ms(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


PRODUCT_SN = "703.786.83"
NEW_RECEIVER = "Taylor Brooks"
NEW_RECEIVER_PHONE = "5550102011"
NEW_POSTAL_CODE = "11201"
ACCOUNT = MailAccountAsset(display_name=NEW_RECEIVER, email="taylor.brooks@example.com")
BUILDING_MANAGER = ContactAsset(name="Riley Building Manager", phone_number="+15550121001", notes="Prefers SMS for elevator confirmations.")
MOVER = ContactAsset(name="Parker Mover Dispatcher", phone_number="+15550121002", notes="Needs address, loading dock, elevator window, and manager contact.")
ROOMMATE = ContactAsset(name="Morgan Roommate", phone_number="+15550121003", notes="Coordinate bedroom furniture by SMS.")

OLD_LANDLORD = MailMessageAsset(
    mailbox="inbox",
    from_name="Landlord Office",
    from_email="landlord@example.com",
    to=[ACCOUNT.email],
    subject="Move-in access notes from September 20",
    body="Preliminary access plan: lobby entrance may be used, and freight elevator reservations were not yet required.",
    timestamp_ms=dt_ms(2026, 9, 20, 9),
    read=True,
)
LANDLORD_PARKING = MailMessageAsset(
    mailbox="inbox",
    from_name="Landlord Office",
    from_email="landlord@example.com",
    to=[ACCOUNT.email],
    subject="River Street loading and parking notes",
    body="Garage staging is limited on move-in week. The service desk can stamp move-in forms after your freight elevator reservation is confirmed.",
    timestamp_ms=dt_ms(2026, 9, 29, 10),
    read=False,
)
LANDLORD_PORTAL = MailMessageAsset(
    mailbox="inbox",
    from_name="Resident Portal",
    from_email="portal@example.com",
    to=[ACCOUNT.email],
    subject="Resident portal setup for River Street",
    body="Your resident portal profile is ready. Package room setup and internet appointments can be handled after move-in access is scheduled.",
    timestamp_ms=dt_ms(2026, 9, 30, 16),
    read=False,
)
LATEST_LANDLORD = MailMessageAsset(
    mailbox="inbox",
    from_name="Landlord Office",
    from_email="landlord@example.com",
    to=[ACCOUNT.email],
    subject="River Street move-in access packet",
    body=(
        "Please follow this October 1 access packet for the move on Tuesday October 6. "
        "Apartment address: 515 River Street Apt 9C, Brooklyn Borough, New York City, New York State. "
        "For online address forms, use the phone number I provide if checkout asks. "
        "Use loading dock B, check in at the west service desk, and give the elevator reservation to movers. "
        "Available freight elevator windows: Tuesday October 6 9:00-11:00 reservation FE-91, or Tuesday October 6 "
        "13:00-15:00 reservation FE-42. Reservation IDs: FE-91 for 9:00-11:00 and FE-42 for 13:00-15:00. "
        "Building manager contact is Riley Building Manager."
    ),
    timestamp_ms=dt_ms(2026, 10, 1, 8, 45),
    read=False,
)
LANDLORD_PACKAGE_UPDATE = MailMessageAsset(
    mailbox="inbox",
    from_name="Landlord Office",
    from_email="landlord@example.com",
    to=[ACCOUNT.email],
    subject="River Street package room and curb permit follow-up",
    body=(
        "Package-room labels can be created starting October 7. Temporary curb permit pickup moved to the "
        "west service desk, and movers can wait on Kent Avenue if loading dock B is full. Keep the freight "
        "elevator reservation details from the access packet ready for check-in."
    ),
    timestamp_ms=dt_ms(2026, 10, 1, 10, 30),
    read=False,
)
OLD_MOVER = SmsMessageAsset(
    address=MOVER.phone_number,
    body="From the first building packet, the lobby entrance looked workable if no freight elevator reservation was available.",
    box="inbox",
    read=True,
    timestamp_ms=dt_ms(2026, 9, 25, 12),
)
MOVER_PACKING_SMS = SmsMessageAsset(
    address=MOVER.phone_number,
    body="Box count can be updated the night before. Please keep fragile labels visible and send building access details once the reservation is set.",
    box="inbox",
    read=True,
    timestamp_ms=dt_ms(2026, 9, 30, 18, 20),
)
LATEST_MOVER = SmsMessageAsset(
    address=MOVER.phone_number,
    body="When you have the confirmed plan, please text us the new address, loading dock, elevator reservation ID, and building manager contact.",
    box="inbox",
    read=True,
    timestamp_ms=dt_ms(2026, 10, 1, 9, 5),
)
ROOMMATE_DECOR_SMS = SmsMessageAsset(
    address=ROOMMATE.phone_number,
    body="The TV cabinet can wait until after we see the room. Bedroom storage is the only thing I want ordered before move-in.",
    box="inbox",
    read=True,
    timestamp_ms=dt_ms(2026, 9, 30, 20),
)
ROOMMATE_SMS = SmsMessageAsset(
    address=ROOMMATE.phone_number,
    body=(
        "For the bedroom wardrobe: must include drawers, width no more than 130 cm, height no more than 210 cm, and budget under 1500. "
        "My Mall notes say MUSKEN two-door wardrobe with 3 drawers is 124 cm wide and 201 cm high at 1299; the larger PAX/FORSAND option was above the size/budget range."
    ),
    box="inbox",
    read=True,
    timestamp_ms=dt_ms(2026, 10, 1, 9, 15),
)
MANAGER_SMS = SmsMessageAsset(
    address=BUILDING_MANAGER.phone_number,
    body="The west service desk can check in movers during a reserved freight elevator window. Send the reservation ID once you choose the slot.",
    box="inbox",
    read=True,
    timestamp_ms=dt_ms(2026, 10, 1, 9, 25),
)
MORNING_CONFLICT = CalendarEventAsset(
    title="Mover supply pickup",
    start_ms=dt_ms(2026, 10, 6, 9),
    end_ms=dt_ms(2026, 10, 6, 11),
    timezone="UTC",
)
OLD_ADDRESS = MallAddressAsset(
    member_username=MALL_LOGIN_USERNAME,
    name="Taylor Old Loft",
    phone_number="5550102100",
    province="New York State",
    city="New York City",
    region="Manhattan Borough",
    detail_address="18 Old Loft Road Apt 2",
    default_status=True,
)
NEW_ADDRESS = MallAddressAsset(
    member_username=MALL_LOGIN_USERNAME,
    name=NEW_RECEIVER,
    phone_number=NEW_RECEIVER_PHONE,
    province="New York State",
    city="New York City",
    region="Brooklyn Borough",
    detail_address="515 River Street Apt 9C",
    post_code=NEW_POSTAL_CODE,
    default_status=True,
)
MOVE_EVENT = CalendarEventAsset(
    title="Move-in freight elevator FE-42",
    start_ms=dt_ms(2026, 10, 6, 13),
    end_ms=dt_ms(2026, 10, 6, 15),
    location="515 River Street Apt 9C",
    description="Use loading dock B and the west service desk. Building manager: Riley Building Manager.",
    timezone="UTC",
    reminder_minutes=(120,),
)
PREP_ALARM = AlarmAsset(
    hour=9,
    minute=0,
    label="Move-in prep",
    enabled=True,
    scheduled_year=2026,
    scheduled_month=10,
    scheduled_day=6,
)
MANAGER_REPLY = SmsMessageAsset(
    address=BUILDING_MANAGER.phone_number,
    body="Confirming freight elevator reservation FE-42 on October 6 from 1:00 PM to 3:00 PM. We will use loading dock B and check in at the west service desk.",
    box="sent",
    read=True,
)
MOVER_REPLY = SmsMessageAsset(
    address=MOVER.phone_number,
    body="Move-in address is 515 River Street Apt 9C, Brooklyn. Use loading dock B, check in at the west service desk, and use freight elevator reservation FE-42 from 1:00 PM to 3:00 PM. Building manager: Riley Building Manager, +15550121001.",
    box="sent",
    read=True,
)
ROOMMATE_REPLY = SmsMessageAsset(
    address=ROOMMATE.phone_number,
    body="I bought the MUSKEN two-door wardrobe with 3 drawers for the new apartment and booked move-in access for October 6 from 1:00 PM to 3:00 PM.",
    box="sent",
    read=True,
)


class MovingDayCoordinationTask(BaseTask):
    apps = {"Mail", "Messages", "Contacts", "Mall", "Calendar", "Clock"}
    difficulty = "realistic"
    category = ['Information-Gathering Tasks', 'Selection / Optimization Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    assets = (
        ACCOUNT,
        OLD_LANDLORD,
        LANDLORD_PARKING,
        LANDLORD_PORTAL,
        LATEST_LANDLORD,
        LANDLORD_PACKAGE_UPDATE,
        BUILDING_MANAGER,
        MOVER,
        ROOMMATE,
        OLD_MOVER,
        MOVER_PACKING_SMS,
        LATEST_MOVER,
        ROOMMATE_DECOR_SMS,
        ROOMMATE_SMS,
        MANAGER_SMS,
        MORNING_CONFLICT,
        MallMemberAsset(
            username=MALL_LOGIN_USERNAME,
            password="123456",
            nickname=MALL_LOGIN_NICKNAME,
            phone=NEW_RECEIVER_PHONE,
            city=MALL_LOGIN_CITY,
            status=1,
        ),
        OLD_ADDRESS,
    )
    goal = (
        "Please coordinate moving day for me. Use the landlord access packet, later landlord follow-up, mover message, roommate wardrobe constraint, Contacts, Mall, Calendar, and Clock evidence. "
        "Use the new apartment address for Mall delivery with the correct delivery receiver details if the address form asks; for the address field format, refer to the existing saved Mall address. "
        "Make it the selected/default delivery address, buy the one matching wardrobe for that address, and finish payment with Alipay. "
        "Schedule the selected access window with a Calendar event titled 'Move-in freight elevator <reservation ID>', location '<apartment street/unit>', description 'Use <loading dock> and <service desk>. Building manager: <manager name>.', and a 120-minute reminder. "
        "Set a Clock alarm on move-in day at 9:00 AM labeled 'Move-in prep'. "
        "For SMS confirmations, examples use sample values only: write the date as full month name plus day, such as January 2, and write 12-hour time ranges like 4:30 PM to 6:00 PM. "
        "Send an SMS to the building manager with exactly this text: 'Confirming freight elevator reservation <reservation ID> on <date> from <start> to <end>. We will use <loading dock> and check in at <service desk>.' "
        "Send an SMS to the mover dispatcher with exactly this text: 'Move-in address is <address>, <borough>. Use <loading dock>, check in at <service desk>, and use freight elevator reservation <reservation ID> from <start> to <end>. Building manager: <name>, <phone>.' "
        "Send an SMS to the roommate with exactly this text: 'I bought the <wardrobe name> for the new apartment and booked move-in access for <date> from <start> to <end>.'."
    )

    user_interaction = (
        "If the agent asks for the receiver name, phone number, or postal code to use for the new Mall delivery address, answer exactly: "
        f"Use receiver name {NEW_RECEIVER}, phone number {NEW_RECEIVER_PHONE}, and postal code {NEW_POSTAL_CODE}."
    )

    def criteria(self):
        return [
            AssetExists(NEW_ADDRESS, task=self),
            MallCheckoutOrderCreated(
                member_username=MALL_LOGIN_USERNAME,
                product_sn=PRODUCT_SN,
                quantity=1,
                expected_status=1,
                receiver_name=NEW_RECEIVER,
                receiver_phone=NEW_RECEIVER_PHONE,
                receiver_province="New York State",
                receiver_city="New York City",
                receiver_region="Brooklyn Borough",
                receiver_detail_address="515 River Street Apt 9C",
            ),
            AssetExists(MOVE_EVENT, task=self),
            AssetExists(PREP_ALARM, task=self),
            AssetExists(MANAGER_REPLY, task=self),
            AssetExists(MOVER_REPLY, task=self),
            AssetExists(ROOMMATE_REPLY, task=self),
        ]
