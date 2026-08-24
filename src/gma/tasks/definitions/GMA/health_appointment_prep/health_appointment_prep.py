from __future__ import annotations

from datetime import UTC, datetime

from gma.assets import (
    AlarmAsset,
    CalendarEventAsset,
    ContactAsset,
    DeviceFileAsset,
    MailAccountAsset,
    MailMessageAsset,
    SmsMessageAsset,
)
from gma.evaluation import AssetExists, AssetModified
from gma.tasks.base import BaseTask


def dt_ms(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


ACCOUNT = MailAccountAsset(display_name="Morgan Carter", email="morgan.carter@example.com")
FAMILY_PHONE = "+1555202301"

OLD_APPOINTMENT = CalendarEventAsset(
    title="Dermatology appointment",
    start_ms=dt_ms(2026, 10, 2, 13, 30),
    end_ms=dt_ms(2026, 10, 2, 14, 0),
    description="Appointment packet listed Room 2A and the 2025 intake packet.",
    location="North Clinic Room 2A",
    timezone="UTC",
    reminder_minutes=(60,),
)
UPDATED_APPOINTMENT = CalendarEventAsset(
    title="Dermatology appointment",
    start_ms=dt_ms(2026, 10, 2, 14, 30),
    end_ms=dt_ms(2026, 10, 2, 15, 15),
    description=(
        "North Clinic Room 4B. Bring north-clinic-intake-2026.pdf, "
        "referral-letter.pdf, insurance-card-info.txt, and medication-list-october.txt."
    ),
    location="North Clinic Room 4B",
    timezone="UTC",
    reminder_minutes=(15,),
)
DEPARTURE_ALARM = AlarmAsset(
    hour=13,
    minute=0,
    label="Leave for dermatology appointment",
    enabled=True,
    vibrate=True,
    scheduled_year=2026,
    scheduled_month=10,
    scheduled_day=2,
)
MEDICATION_ALARM = AlarmAsset(
    hour=9,
    minute=0,
    label="Pack medication list",
    enabled=True,
    vibrate=True,
    scheduled_year=2026,
    scheduled_month=10,
    scheduled_day=2,
)
CONFIRMATION_TEXT = (
    "Clinic logistics are updated: October 2 at 2:30 PM, North Clinic Room 4B. "
    "I will bring north-clinic-intake-2026.pdf, referral-letter.pdf, "
    "insurance-card-info.txt, and medication-list-october.txt."
)


class HealthAppointmentPrepTask(BaseTask):
    apps = {"Mail", "Messages", "Contacts", "Calendar", "Clock", "Files"}
    difficulty = "realistic"
    category = ['Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    max_steps = 160

    assets = (
        ACCOUNT,
        MailMessageAsset(
            mailbox="inbox",
            from_name="North Clinic Scheduling",
            from_email="scheduling@northclinic.example.com",
            to=[ACCOUNT.email],
            subject="Dermatology appointment packet",
            body=(
                "Your dermatology appointment packet lists October 2, 2026 at 1:30 PM in Room 2A. "
                "The packet references north-clinic-intake-2025.pdf and insurance details."
            ),
            timestamp_ms=dt_ms(2026, 9, 28, 16, 0),
            read=True,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="North Clinic Scheduling",
            from_email="scheduling@northclinic.example.com",
            to=[ACCOUNT.email],
            subject="Room assignment and arrival notes for Oct 2",
            body=(
                "For the October 2 dermatology visit, check in at 2:30 PM in North Clinic Room 4B. "
                "The visit is booked for 45 minutes. Please bring north-clinic-intake-2026.pdf, referral-letter.pdf, "
                "insurance-card-info.txt, and medication-list-october.txt for front-desk intake. "
                "The 2026 intake packet replaces the 2025 packet for this visit."
            ),
            timestamp_ms=dt_ms(2026, 10, 1, 9, 15),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="North Clinic Billing",
            from_email="billing@northclinic.example.com",
            to=[ACCOUNT.email],
            subject="Billing portal estimate",
            body="A billing estimate is available in the portal. It is not needed at check-in if the insurance card is available.",
            timestamp_ms=dt_ms(2026, 10, 1, 9, 45),
            read=False,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="North Clinic Portal",
            from_email="portal@northclinic.example.com",
            to=[ACCOUNT.email],
            subject="Portal lab notice",
            body="A lab notice from September can be viewed in the portal. No lab document is required for the Oct 2 dermatology front desk.",
            timestamp_ms=dt_ms(2026, 10, 1, 10, 20),
            read=True,
        ),
        MailMessageAsset(
            mailbox="inbox",
            from_name="Community Flu Clinic",
            from_email="fluclinic@example.com",
            to=[ACCOUNT.email],
            subject="Saturday flu clinic hours",
            body="The Saturday flu clinic is in the west gym from 9 AM to noon. This is separate from North Clinic dermatology scheduling.",
            timestamp_ms=dt_ms(2026, 10, 1, 11, 0),
            read=True,
        ),
        DeviceFileAsset(
            app="Files",
            storage_dir="Download",
            filename="north-clinic-intake-2025.pdf",
            mime_type="application/pdf",
            text_content="North Clinic intake packet used for last year's dermatology visit.",
        ),
        DeviceFileAsset(
            app="Files",
            storage_dir="Download",
            filename="north-clinic-intake-2026.pdf",
            mime_type="application/pdf",
            text_content="North Clinic intake packet for the October 2, 2026 dermatology visit.",
        ),
        DeviceFileAsset(
            app="Files",
            storage_dir="Download",
            filename="referral-letter.pdf",
            mime_type="application/pdf",
            text_content="Referral letter for North Clinic dermatology front-desk intake.",
        ),
        DeviceFileAsset(
            app="Files",
            storage_dir="Download",
            filename="insurance-card-info.txt",
            mime_type="text/plain",
            text_content="Insurance card information for check-in. Bring current card and photo ID.",
        ),
        DeviceFileAsset(
            app="Files",
            storage_dir="Download",
            filename="medication-list-october.txt",
            mime_type="text/plain",
            text_content="Medication list document for appointment check-in. This is a packing document only.",
        ),
        DeviceFileAsset(
            app="Files",
            storage_dir="Download",
            filename="referral-letter-draft-2025.pdf",
            mime_type="application/pdf",
            text_content="Draft referral from a prior year, kept for records.",
        ),
        DeviceFileAsset(
            app="Files",
            storage_dir="Download",
            filename="clinic-map-room-2a.txt",
            mime_type="text/plain",
            text_content="Map note for Room 2A from the appointment packet.",
        ),
        DeviceFileAsset(
            app="Files",
            storage_dir="Download",
            filename="billing-estimate.txt",
            mime_type="text/plain",
            text_content="Billing estimate from the portal. Not a check-in document.",
        ),
        DeviceFileAsset(
            app="Files",
            storage_dir="Download",
            filename="pharmacy-refill-note.txt",
            mime_type="text/plain",
            text_content="Pharmacy refill reminder for a separate pickup window.",
        ),
        ContactAsset(name="North Clinic", phone_number="+1555202300", notes="Dermatology front desk"),
        ContactAsset(name="Avery Carter", phone_number=FAMILY_PHONE, notes="Family appointment contact"),
        ContactAsset(name="North Clinic Billing", phone_number="+1555202302", notes="Billing desk"),
        ContactAsset(name="Quinn Carter", phone_number="+1555202303", notes="Family contact for rides"),
        ContactAsset(name="Pine Pharmacy", phone_number="+1555202304", notes="Pharmacy pickup desk"),
        SmsMessageAsset(
            address=FAMILY_PHONE,
            body=(
                "Text me once the dermatology logistics are handled. I only need the time, room, and document list. "
                "The garage has been slow around lunch, so a one-time 1 PM leave reminder on the appointment day is safest."
            ),
            box="inbox",
            timestamp_ms=dt_ms(2026, 10, 1, 12, 0),
            read=False,
        ),
        SmsMessageAsset(
            address="+1555202303",
            body="If you need a ride after 3:30, I can help, but I do not need the clinic paperwork list.",
            box="inbox",
            timestamp_ms=dt_ms(2026, 10, 1, 12, 10),
            read=True,
        ),
        SmsMessageAsset(
            address="+1555202304",
            body="Your pharmacy refill can be picked up after Friday. This is separate from the dermatology appointment packet.",
            box="inbox",
            timestamp_ms=dt_ms(2026, 10, 1, 12, 20),
            read=True,
        ),
        SmsMessageAsset(
            address=FAMILY_PHONE,
            body="Also set a one-time dated morning reminder to pack the medication list so it is not missed with the forms.",
            box="inbox",
            timestamp_ms=dt_ms(2026, 10, 1, 12, 25),
            read=False,
        ),
        CalendarEventAsset(
            title="Work handoff",
            start_ms=dt_ms(2026, 10, 2, 12, 15),
            end_ms=dt_ms(2026, 10, 2, 12, 45),
            description="Finish before leaving for the clinic.",
            timezone="UTC",
        ),
        OLD_APPOINTMENT,
        CalendarEventAsset(
            title="Pharmacy pickup window",
            start_ms=dt_ms(2026, 10, 2, 15, 45),
            end_ms=dt_ms(2026, 10, 2, 16, 15),
            description="Separate pickup after appointment if time allows.",
            timezone="UTC",
        ),
    )

    goal = (
        "Please get my dermatology appointment logistics ready. Reconcile the clinic Mail, Messages, Files, Contacts, and Calendar information to resolve the appointment time, location, check-in documents, and family-contact update. "
        "Modify the existing Calendar event titled 'Dermatology appointment' instead of making a duplicate, and keep that title. Set the event start to the active clinic check-in time, use the active clinic visit length, set location to the active clinic room, and set a single Calendar reminder exactly 15 minutes before. "
        "Use this exact Calendar description format: '<clinic room>. Bring <required files in clinic Mail order>.'. "
        "Set one-time dated Clock alarms, not weekly or repeating alarms, with vibration on: 'Pack medication list' on the date for dermatology at 9:00 AM and 'Leave for dermatology appointment' on the date for dermatology at 1:00 PM. "
        "Send Avery Carter, the family contact who asked for the update, exactly using this format: 'Clinic logistics are updated: <date> at <time>, <clinic room>. I will bring <required files>.'. "
        "Use these examples for formatting only: <date> 'September 14'; <time> '9:30 AM'; <required files> 'alpha.pdf, beta.pdf, and gamma.txt'."
    )

    def criteria(self):
        return [
            AssetModified(OLD_APPOINTMENT, UPDATED_APPOINTMENT, task=self),
            AssetExists(MEDICATION_ALARM, task=self),
            AssetExists(DEPARTURE_ALARM, task=self),
            AssetExists(
                SmsMessageAsset(address=FAMILY_PHONE, body=CONFIRMATION_TEXT, box="sent", read=True),
                task=self,
            ),
        ]
