from __future__ import annotations

from datetime import UTC, datetime

from gma.apps.mall import MALL_LOGIN_CITY, MALL_LOGIN_NICKNAME, MALL_LOGIN_PHONE, MALL_LOGIN_USERNAME
from gma.apps.meituan import MEITUAN_LOGIN_CITY, MEITUAN_LOGIN_USER_ID, MEITUAN_LOGIN_USERNAME
from gma.assets import (
    CalendarEventAsset,
    ContactAsset,
    MailAccountAsset,
    MailMessageAsset,
    MallAddressAsset,
    MallMemberAsset,
    MeituanOrderAsset,
    MeituanOrderFood,
    MeituanUserAsset,
    SmsMessageAsset,
)
from gma.evaluation import AssetExists, AssetModified
from gma.evaluation.checks.mall import MallCheckoutOrderCreated
from gma.tasks.base import BaseTask


def utc_ms(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


PRODUCT_SN = "jbl_flip7_2026"
INVITE_BODY = (
    "Nora's birthday dinner is set for October 4 at 6:00 PM at 44 Queens Boulevard Apt 2. "
    "Jishengke dinner and the JBL Flip 7 gift are handled."
)


class FamilyBirthdayBundleTask(BaseTask):
    apps = {"Contacts", "Calendar", "Mall", "Meituan", "Messages", "Mail"}
    difficulty = "realistic"
    category = ['Information-Gathering Tasks', 'Selection / Optimization Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    max_steps = 180

    account = MailAccountAsset(display_name="Avery Hart", email="avery.hart@example.com")
    nora_contact = ContactAsset(
        name="Nora Hart",
        phone_number="5550101301",
        phone_label="mobile",
        email="nora.hart@example.com",
        label="family",
        notes=(
            "Sister. Birthday October 4. Home address: 44 Queens Boulevard Apt 2."
        ),
    )
    evan_contact = ContactAsset(
        name="Evan Hart",
        phone_number="5550101302",
        phone_label="mobile",
        email="evan.hart@example.com",
        label="family",
        notes="Brother. Invite him to Nora birthday plans if he confirms.",
    )
    maya_contact = ContactAsset(
        name="Maya Hart",
        phone_number="5550101303",
        phone_label="mobile",
        email="maya.hart@example.com",
        label="family",
        notes="Cousin. Invite her to Nora birthday plans if she confirms; she often brings her two kids.",
    )
    theo_contact = ContactAsset(
        name="Theo Hart",
        phone_number="5550101304",
        phone_label="mobile",
        email="theo.hart@example.com",
        label="family",
        notes="Family contact with a birthday on October 12.",
    )
    lena_contact = ContactAsset(
        name="Lena Hart",
        phone_number="5550101305",
        phone_label="mobile",
        email="lena.hart@example.com",
        label="family",
        notes="Aunt. Helps with Theo's birthday planning; check current replies before inviting.",
    )

    nora_birthday = CalendarEventAsset(
        title="Nora Hart Birthday",
        start_ms=utc_ms(2026, 10, 4, 9),
        end_ms=utc_ms(2026, 10, 4, 9, 30),
        description="Family birthday this week. Plan dinner after checking contacts, mail, and messages.",
        timezone="UTC",
    )
    lunch_hold = CalendarEventAsset(
        title="Family lunch hold",
        start_ms=utc_ms(2026, 10, 4, 12),
        end_ms=utc_ms(2026, 10, 4, 13),
        description="Tentative Nora family meal time from earlier planning.",
        timezone="UTC",
    )
    theo_birthday = CalendarEventAsset(
        title="Theo Hart Birthday",
        start_ms=utc_ms(2026, 10, 12, 9),
        end_ms=utc_ms(2026, 10, 12, 9, 30),
        description="Later family birthday in October.",
        timezone="UTC",
    )
    family_menu_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Maya Hart",
        from_email="maya.hart@example.com",
        to=[account.email],
        subject="Sunday family dinner notes",
        body=(
            "Nora still wants Jishengke for the birthday dinner. For the food count, include Nora as one adult, "
            "then add each confirmed adult guest from Messages. If the adult or child food count is unclear, "
            "check with me before ordering. Evan still skips popcorn chicken."
        ),
        timestamp_ms=utc_ms(2026, 9, 30, 18),
        read=True,
    )
    audio_gift_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Nora Hart",
        from_email="nora.hart@example.com",
        to=[account.email],
        subject="Gift idea from last weekend",
        body=(
            "If you are choosing a birthday gift, I would actually use a small portable speaker for dinner music. "
            "Please keep it under 2000; I do not need another pair of earbuds."
        ),
        timestamp_ms=utc_ms(2026, 9, 29, 20, 15),
        read=True,
    )
    theo_wishlist_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Theo Hart",
        from_email="theo.hart@example.com",
        to=[account.email],
        subject="Ideas for October 12",
        body=(
            "For my October 12 birthday dinner, headphones and black desk accessories would be useful. "
            "I am keeping the restaurant simple that weekend."
        ),
        timestamp_ms=utc_ms(2026, 9, 28, 11),
        read=True,
    )
    august_dinner_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Evan Hart",
        from_email="evan.hart@example.com",
        to=[account.email],
        subject="August family meal receipt",
        body=(
            "Found the August Jishengke receipt: we had Old Beijing chicken rolls, popcorn chicken, and two drinks. "
            "That was for the park day, before Nora picked the birthday dinner plan."
        ),
        timestamp_ms=utc_ms(2026, 9, 24, 10, 30),
        read=True,
    )
    mall_sale_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Mall Audio Deals",
        from_email="deals@mall.example.com",
        to=[account.email],
        subject="Audio sale picks",
        body=(
            "This week's audio picks include JBL Tour Pro 3 earbuds, over-ear headphones, portable speakers, and soundbars. "
            "Some items have limited stock during the holiday sale."
        ),
        timestamp_ms=utc_ms(2026, 9, 27, 9),
        read=True,
    )
    delivery_notice_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Queens Building Desk",
        from_email="desk@queens-building.example.com",
        to=[account.email],
        subject="Weekend package desk hours",
        body="The Queens package desk closes early this Sunday. Apartment deliveries should still use the apartment number.",
        timestamp_ms=utc_ms(2026, 9, 26, 16),
        read=True,
    )
    evan_lunch_probe = SmsMessageAsset(
        address="5550101302",
        body="I might have been able to do Nora's birthday at lunch, but my Sunday shift changed again.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 9, 30, 12),
        read=True,
    )
    evan_constraint = SmsMessageAsset(
        address="5550101302",
        body="For Nora's birthday, I can make October 4 at 6 PM. Count me as one adult. Still skipping popcorn chicken.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 8, 30),
        read=True,
    )
    maya_rsvp = SmsMessageAsset(
        address="5550101303",
        body="I can come to Nora's birthday and I am bringing both kids. 6 PM works for us; the kids will stick with Zinger burgers.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 8, 45),
        read=True,
    )
    theo_message = SmsMessageAsset(
        address="5550101304",
        body="I am saving my own birthday dinner for October 12 and will sit Nora's dinner out this time.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 9, 5),
        read=True,
    )
    lena_message = SmsMessageAsset(
        address="5550101305",
        body="I am tied up Sunday evening, but I will call Nora separately before her birthday.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 9, 25),
        read=True,
    )
    nora_address_note = SmsMessageAsset(
        address="5550101301",
        body="If anything gets delivered for my birthday, Apt 2 is still the right door at 44 Queens Boulevard.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 10),
        read=True,
    )
    maya_noise = SmsMessageAsset(
        address="5550101303",
        body="The kids found the paper crowns from the summer picnic, so I might bring those too.",
        box="inbox",
        timestamp_ms=utc_ms(2026, 10, 1, 10, 20),
        read=True,
    )

    meituan_user = MeituanUserAsset(
        username=MEITUAN_LOGIN_USERNAME,
        password="123456",
        user_id=MEITUAN_LOGIN_USER_ID,
        city=MEITUAN_LOGIN_CITY,
        status=1,
    )
    dinner_order = MeituanOrderAsset(
        user_id=MEITUAN_LOGIN_USER_ID,
        restaurant_name="Jishengke",
        foods=[
            MeituanOrderFood(food_name="Mexican chicken rolls", quantity=3),
            MeituanOrderFood(food_name="Zinger burger", quantity=2),
        ],
        status="Payment successful",
        address_name="Nora Hart",
        code=200,
        delivery_status=1,
    )
    mall_member = MallMemberAsset(
        username=MALL_LOGIN_USERNAME,
        password="123456",
        nickname=MALL_LOGIN_NICKNAME,
        phone=MALL_LOGIN_PHONE,
        city=MALL_LOGIN_CITY,
        status=1,
    )
    mall_address = MallAddressAsset(
        member_username=MALL_LOGIN_USERNAME,
        name="Nora Hart",
        phone_number="5550101301",
        province="New York State",
        city="New York City",
        region="Queens Borough",
        detail_address="44 Queens Boulevard Apt 2",
        post_code="11375",
        default_status=True,
    )
    birthday_dinner = CalendarEventAsset(
        title="Nora Hart Birthday Dinner",
        start_ms=utc_ms(2026, 10, 4, 18),
        end_ms=utc_ms(2026, 10, 4, 20),
        location="44 Queens Boulevard Apt 2",
        description="Jishengke dinner ordered; JBL Flip 7 gift purchased; Evan and Maya invited.",
        timezone="UTC",
        reminder_minutes=(60,),
    )

    assets = (
        account,
        nora_contact,
        evan_contact,
        maya_contact,
        theo_contact,
        lena_contact,
        nora_birthday,
        lunch_hold,
        theo_birthday,
        family_menu_mail,
        audio_gift_mail,
        theo_wishlist_mail,
        august_dinner_mail,
        mall_sale_mail,
        delivery_notice_mail,
        evan_lunch_probe,
        evan_constraint,
        maya_rsvp,
        theo_message,
        lena_message,
        nora_address_note,
        maya_noise,
        meituan_user,
        mall_member,
        mall_address,
    )
    goal = (
        "Please handle the family birthday coming up this week. Identify the birthday person from Calendar and Contacts, "
        "then order the Jishengke dinner to that person's home address and pay with Alipay. Use Mail and Messages to determine the adult "
        "and child headcount, dinner time, and food constraints. Buy the Mall gift with Alipay that matches the birthday person's portable "
        "shared-speaker preference and budget. Update the existing birthday event to '<birthday full name> Birthday Dinner' "
        "as a two-hour dinner event with the dinner address, a description in the format 'Jishengke dinner ordered; <gift name> gift purchased; "
        "<invitee first names> invited.', using invitee first names in alphabetical order joined with the word 'and', and a 60-minute reminder. Send each correct invited family member exactly: "
        "'<birthday first name>'s birthday dinner is set for <date> at <time> at <address>. Jishengke dinner and the "
        "<gift name> gift are handled.'. Use a date style like 'September 14' and a time style like '7:30 PM' in the SMS."
    )

    user_interaction = (
        "If the agent asks how to count the Nora birthday dinner food, answer exactly: "
        "Use one Mexican chicken roll for each adult: Nora, Evan, and Maya. Use one Zinger burger for each of Maya's two children. Do not order popcorn chicken. "
        "If the agent asks whether to choose Mr or Ms for the Meituan delivery address, answer exactly: Use Ms. "
        "If the agent asks which Meituan address label to use, answer exactly: Use Home."
    )

    def criteria(self):
        return [
            AssetExists(self.dinner_order, task=self),
            MallCheckoutOrderCreated(
                member_username=MALL_LOGIN_USERNAME,
                product_sn=PRODUCT_SN,
                quantity=1,
                expected_status=1,
                receiver_name="Nora Hart",
                receiver_phone="5550101301",
                receiver_province="New York State",
                receiver_city="New York City",
                receiver_region="Queens Borough",
                receiver_detail_address="44 Queens Boulevard Apt 2",
            ),
            AssetModified(self.nora_birthday, self.birthday_dinner, task=self),
            AssetExists(SmsMessageAsset(address="5550101302", body=INVITE_BODY, box="sent", read=True), task=self),
            AssetExists(SmsMessageAsset(address="5550101303", body=INVITE_BODY, box="sent", read=True), task=self),
        ]
