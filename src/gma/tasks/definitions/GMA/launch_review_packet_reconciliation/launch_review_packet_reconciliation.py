from __future__ import annotations

from datetime import UTC, datetime

from gma.assets import (
    AlarmAsset,
    CalendarEventAsset,
    DeviceFileAsset,
    ElementXMessageAsset,
    ElementXRoomAsset,
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
from gma.evaluation import AssetExists, AssetMissing
from gma.tasks.base import BaseTask


def dt_ms(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


ACCOUNT = MailAccountAsset(display_name="Taylor Brooks", email="taylor.brooks@example.com")

V2_TEXT = "Launch timeline v2: QA freeze October 6; App review October 9; Launch October 14.\n"
V3_TEXT = (
    "Approved launch timeline v3: QA freeze October 8; App review October 10; "
    "Launch October 15. Risk log: payment smoke retest remains open.\n"
)
V4_TEXT = (
    "Launch timeline v4 working draft: QA freeze October 12; App review October 13; "
    "Launch October 18. Proposed downstream schedule for finance/legal review.\n"
)
QA_BODY = (
    "For the launch review packet, QA is signing off one limited correction to the approved baseline: "
    "move QA freeze from October 8 to October 9 because regression retest needs one extra day. "
    "No other milestone changes are approved for this review. Use the latest QA Automation risk email subject "
    "as the remaining-risk label."
)
APP_REVIEW_BODY = (
    "I put the v4 working draft in Files for next week's finance/legal planning. "
    "It may help App Review estimate the downstream queue, but do not treat it as an approved review packet yet."
)
COMMS_BODY = (
    "For launch comms, I can hold the customer notice draft until October 11 if the review packet shifts. "
    "I only own comms timing and will follow the packet you finalize."
)
PAYMENT_BODY = (
    "Payment smoke test rerun is still producing mixed evidence this morning. This is the risk note for the "
    "launch review; use this email subject as the risk label until QA accepts a clean retest."
)
FINANCE_BODY = (
    "Finance/legal planning is penciled for October 12. I am checking budget notes against the v4 planning sheet "
    "and will refresh the cost memo after the owner packet is final."
)

FILES = (
    DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="timeline_v3_approved.pdf",
        mime_type="application/pdf",
        text_content=V3_TEXT,
    ),
    DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="timeline_v4_draft.pdf",
        mime_type="application/pdf",
        text_content=V4_TEXT,
    ),
)
MAILS = (
    MailMessageAsset(
        mailbox="inbox",
        from_name="Project Owner",
        from_email="owner.launch@example.com",
        to=[ACCOUNT.email],
        subject="timeline_v2.pdf reference copy",
        body="Older launch timeline attached for historical reference while the owner finishes review.",
        attachments=[MailAttachment(filename="timeline_v2.pdf", mime_type="application/pdf", text_content=V2_TEXT)],
        timestamp_ms=dt_ms(2026, 9, 28, 10),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Project Owner",
        from_email="owner.launch@example.com",
        to=[ACCOUNT.email],
        subject="Approved launch review baseline",
        body="timeline_v3_approved.pdf is approved by the project owner and is the baseline for launch review.",
        attachments=[MailAttachment(filename="timeline_v3_approved.pdf", mime_type="application/pdf", text_content=V3_TEXT)],
        timestamp_ms=dt_ms(2026, 9, 30, 9),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="App Review Coordinator",
        from_email="appreview.launch@example.com",
        to=[ACCOUNT.email],
        subject="v4 working draft app review dates",
        body=APP_REVIEW_BODY,
        timestamp_ms=dt_ms(2026, 9, 30, 17),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Launch Comms",
        from_email="comms.launch@example.com",
        to=[ACCOUNT.email],
        subject="Customer notice timing hold",
        body=COMMS_BODY,
        timestamp_ms=dt_ms(2026, 9, 30, 18),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="Finance Review",
        from_email="finance.launch@example.com",
        to=[ACCOUNT.email],
        subject="Budget memo timing for launch review",
        body=FINANCE_BODY,
        timestamp_ms=dt_ms(2026, 9, 30, 19),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="QA Lead",
        from_email="qa.launch@example.com",
        to=[ACCOUNT.email],
        subject="QA freeze correction for launch review",
        body=QA_BODY,
        timestamp_ms=dt_ms(2026, 10, 1, 8),
        read=False,
    ),
    MailMessageAsset(
        mailbox="inbox",
        from_name="QA Automation",
        from_email="qa.automation@example.com",
        to=[ACCOUNT.email],
        subject="Payment smoke test rerun notes",
        body=PAYMENT_BODY,
        timestamp_ms=dt_ms(2026, 10, 1, 8, 20),
        read=False,
    ),
)

MATTERMOST_USERS = (
    MattermostUserAsset(
        username="launch-coordinator",
        email="launch.coordinator@example.com",
        first_name="Launch",
        last_name="Coordinator",
        team="company",
        channel_memberships=["launch-review"],
    ),
    MattermostUserAsset(
        username="release-manager",
        email="release.manager@example.com",
        first_name="Release",
        last_name="Manager",
        team="company",
        channel_memberships=["launch-review"],
    ),
    MattermostUserAsset(
        username="app-reviewer",
        email="app.reviewer@example.com",
        first_name="App",
        last_name="Reviewer",
        team="company",
        channel_memberships=["launch-review"],
    ),
    MattermostUserAsset(
        username="qa-automation",
        email="qa.automation@example.com",
        first_name="QA",
        last_name="Automation",
        team="company",
        channel_memberships=["launch-review"],
    ),
    MattermostUserAsset(
        username="launch-comms",
        email="launch.comms@example.com",
        first_name="Launch",
        last_name="Comms",
        team="company",
        channel_memberships=["launch-review"],
    ),
    MattermostUserAsset(
        username="finance-review",
        email="finance.review@example.com",
        first_name="Finance",
        last_name="Review",
        team="company",
        channel_memberships=["launch-review"],
    ),
    MattermostUserAsset(
        username="support-ops",
        email="support.ops@example.com",
        first_name="Support",
        last_name="Ops",
        team="company",
        channel_memberships=["launch-review"],
    ),
)
MATTERMOST_CHANNEL = MattermostChannelAsset(
    team="company",
    name="launch-review",
    display_name="Launch Review",
    channel_type="O",
)
MATTERMOST_POSTS = (
    MattermostPostAsset(
        team="company",
        channel="launch-review",
        username="app-reviewer",
        message=(
            "I saw the v4 planning draft in Files. It is useful for app-review queue estimates, but I am "
            "not treating those later dates as approved for this review packet."
        ),
    ),
    MattermostPostAsset(
        team="company",
        channel="launch-review",
        username="qa-automation",
        message=(
            "Payment smoke test rerun is still inconsistent. I would keep the payment smoke retest "
            "on the open-risk list until the clean retest is accepted."
        ),
    ),
    MattermostPostAsset(
        team="company",
        channel="launch-review",
        username="launch-comms",
        message=(
            "Customer notice copy can wait until October 11 if needed. That only affects comms prep; "
            "I will mirror whatever milestone packet gets finalized."
        ),
    ),
    MattermostPostAsset(
        team="company",
        channel="launch-review",
        username="finance-review",
        message=(
            "Finance/legal planning is still penciled for October 12. I am using the v4 sheet for rough "
            "budget prep only and will refresh my memo after the owner packet is final."
        ),
    ),
    MattermostPostAsset(
        team="company",
        channel="launch-review",
        username="support-ops",
        message=(
            "Support coverage still has placeholder dates from an earlier staffing draft. Once the review "
            "meeting is on the calendar, I can update staffing notes around the final plan."
        ),
    ),
    MattermostPostAsset(
        team="company",
        channel="launch-review",
        username="release-manager",
        message=(
            "When Taylor posts the review packet here, please use the owner-approved baseline, not a planning draft, "
            "and keep the note limited to the signed QA change plus the open launch risk."
        ),
    ),
    MattermostPostAsset(
        team="company",
        channel="launch-review",
        username="release-manager",
        message=(
            "For the review meeting, the release team can cover Oct 7 13:00-16:00 or Oct 8 15:00-17:00. "
            "Please check Taylor's Calendar and use the first open one-hour slot in those windows."
        ),
    ),
)
LEADERSHIP_USER = ElementXUserAsset(username="v2-09-leadership", password="password", display_name="Leadership Reviewer")
LEADERSHIP_ROOM = ElementXRoomAsset(
    name="Launch Leadership",
    room_type="group",
    creator_username="testuser",
    creator_password="testpass123",
    members=[LEADERSHIP_USER.username],
    alias_localpart="v2-09-launch-leadership",
    topic="Launch review leadership updates.",
)
LEADERSHIP_ASK = ElementXMessageAsset(
    room="v2-09-launch-leadership",
    sender_username=LEADERSHIP_USER.username,
    sender_password="password",
    text="Please send only what changed from the approved baseline and the remaining risky milestone.",
    created_at_ms=dt_ms(2026, 10, 1, 9),
)
CALENDAR_CONFLICTS = (
    CalendarEventAsset(
        title="Launch prep block",
        start_ms=dt_ms(2026, 10, 7, 13),
        end_ms=dt_ms(2026, 10, 7, 15),
        timezone="UTC",
    ),
    CalendarEventAsset(
        title="QA sync block",
        start_ms=dt_ms(2026, 10, 8, 15),
        end_ms=dt_ms(2026, 10, 8, 17),
        timezone="UTC",
    ),
)

MATTERMOST_MESSAGE = (
    "approved packet attached: timeline_v3_approved.pdf. authorized correction: "
    "qa freeze moves to october 9; remaining risk is payment smoke test rerun notes."
)
LEADERSHIP_SUMMARY = (
    "changed milestone: qa freeze moved from october 8 to october 9. "
    "remaining risk: payment smoke test rerun notes."
)
EXPECTED_EVENT = CalendarEventAsset(
    title="Launch Review Meeting",
    start_ms=dt_ms(2026, 10, 7, 15),
    end_ms=dt_ms(2026, 10, 7, 16),
    description="Review approved baseline timeline_v3 with authorized milestone correction.",
    timezone="UTC",
    reminder_minutes=(30,),
)
EXPECTED_ALARM = AlarmAsset(
    hour=14,
    minute=30,
    label="Launch review reminder",
    enabled=True,
    scheduled_year=2026,
    scheduled_month=10,
    scheduled_day=7,
)
EXPECTED_PACKET = MattermostFilePostAsset(
    team="company",
    channel="launch-review",
    username="launch-coordinator",
    message=MATTERMOST_MESSAGE,
    filename="timeline_v3_approved.pdf",
    mime_type="application/pdf",
    text_content=V3_TEXT,
)
WRONG_PACKET = MattermostFilePostAsset(
    team="company",
    channel="launch-review",
    username="launch-coordinator",
    message=MATTERMOST_MESSAGE,
    filename="timeline_v4_draft.pdf",
    mime_type="application/pdf",
    text_content=V4_TEXT,
)
EXPECTED_LEADERSHIP = ElementXMessageAsset(
    room="v2-09-launch-leadership",
    sender_username="testuser",
    sender_password="testpass123",
    text=LEADERSHIP_SUMMARY,
)


class LaunchReviewPacketReconciliationTask(BaseTask):
    apps = {"Mail", "Files", "Mattermost", "ElementX", "Calendar", "Clock"}
    difficulty = "realistic"
    category = ['Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    assets = (
        ACCOUNT,
        *MAILS,
        *FILES,
        MATTERMOST_CHANNEL,
        *MATTERMOST_USERS,
        MattermostSessionAsset(username="launch-coordinator"),
        *MATTERMOST_POSTS,
        LEADERSHIP_USER,
        LEADERSHIP_ROOM,
        LEADERSHIP_ASK,
        *CALENDAR_CONFLICTS,
    )
    goal = (
        "Please prepare the launch review packet. First reconcile the evidence across Mail and Files: identify the owner-approved baseline, "
        "ignore unapproved planning drafts, and apply only the explicitly signed QA correction. Then use Mattermost for the packet posting "
        "instructions and release review windows, ElementX for the leadership update, and Calendar for conflicts. "
        "Use the lowercase subject of the latest QA Automation risk email as <risk>. "
        "Post the packet in the Mattermost launch-review channel with this exact single-paragraph message format and no extra line breaks: "
        "'approved packet attached: <approved filename>. authorized correction: <changed milestone> moves to <new date>; remaining risk is <risk>.' "
        "Attach the approved baseline file with that post. "
        "Send ElementX leadership exactly: 'changed milestone: <changed milestone> moved from <old date> to <new date>. remaining risk: <risk>.' "
        "Use lowercase letters for Mattermost and ElementX message text. For date text in those messages, use full month name plus day, such as january 2. "
        "Schedule a Calendar event exactly titled 'Launch Review Meeting' in the first available one-hour release review slot after checking Calendar, "
        "with description 'Review approved baseline timeline_v3 with authorized milestone correction.' and a 30-minute reminder. "
        "Set a Clock alarm at the Calendar reminder time, labeled 'Launch review reminder'."
    )

    def criteria(self):
        return [
            AssetExists(EXPECTED_PACKET, task=self),
            AssetMissing(WRONG_PACKET, task=self, weight=0.5),
            AssetExists(EXPECTED_LEADERSHIP, task=self),
            AssetExists(EXPECTED_EVENT, task=self),
            AssetExists(EXPECTED_ALARM, task=self),
        ]
