from __future__ import annotations

from datetime import UTC, datetime

from gma.assets import (
    AlarmAsset,
    CalendarEventAsset,
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
from gma.evaluation import AssetExists
from gma.tasks.base import BaseTask


def dt_ms(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


TARGET_FILE = "checkout_timeout_action_plan.txt"
ACTION_PLAN_TEXT = (
    "Incident summary: Mobile checkout timeout caused intermittent payment handoff failures.\n"
    "Incident title: Mobile checkout timeout\n"
    "Client-success recipient: client-success@example.com\n"
    "Required email subject: INC-2419 checkout timeout action plan\n"
    "Required body note: Please review the attached action plan before the internal review.\n"
    "ElementX room criteria: choose the group room with topic client incident action-plan handoff and setup note Use this room for client-success action plan sent notices after review time is scheduled.\n"
    "Follow-up owner: Harper Lewis\n"
)
MAIL_BODY = "Please review the attached action plan before the internal review."
ELEMENTX_NOTICE = (
    "INC-2419 action plan sent to client-success@example.com. "
    "Internal review is scheduled for October 4 at 9:30 AM."
)
ROOM_ALIAS = "v2-04-client-action-handoff"
RELEASE_ROOM_ALIAS = "v2-04-release-watch"
CLIENT_ROOM_ALIAS = "v2-04-client-questions"
SCHEDULE_ROOM_ALIAS = "v2-04-schedule-desk"
ELEMENTX_ROOM_TOPIC = "client incident action-plan handoff"
ELEMENTX_ROOM_NOTE = "Use this room for client-success action plan sent notices after review time is scheduled."
DESK_QUEUE_CHANNEL = "desk-queue"
RELEASE_LOG_CHANNEL = "release-log"
TEAM_BOARD_CHANNEL = "team-board"


class IncidentFollowupThreadAttachmentDeadlineTask(BaseTask):
    apps = {"Mattermost", "Files", "Mail", "Calendar", "ElementX", "Clock"}
    difficulty = "realistic"
    category = ["Multi-Step Workflow Tasks"]
    snapshot = "gma_ready_state"
    max_steps = 160

    desk_queue_channel = MattermostChannelAsset(team="company", name=DESK_QUEUE_CHANNEL, display_name="Desk Queue", channel_type="O")
    release_log_channel = MattermostChannelAsset(team="company", name=RELEASE_LOG_CHANNEL, display_name="Release Log", channel_type="O")
    team_board_channel = MattermostChannelAsset(team="company", name=TEAM_BOARD_CHANNEL, display_name="Team Board", channel_type="O")
    mattermost_user = MattermostUserAsset(
        username="harper-lewis",
        email="harper.lewis@example.com",
        first_name="Harper",
        last_name="Lewis",
        team="company",
        channel_memberships=[DESK_QUEUE_CHANNEL, RELEASE_LOG_CHANNEL, TEAM_BOARD_CHANNEL],
    )

    old_incident = MattermostFilePostAsset(
        team="company",
        channel=DESK_QUEUE_CHANNEL,
        username="harper-lewis",
        message="INC-2407 Payment retry alert is resolved with no follow-up needed.",
        filename="payment_retry_plan.txt",
        mime_type="text/plain",
        source_path="assets/payment_retry_plan.txt",
        create_at_ms=dt_ms(2026, 9, 30, 9),
    )
    desk_queue_status_note = MattermostPostAsset(
        team="company",
        channel=DESK_QUEUE_CHANNEL,
        username="harper-lewis",
        message=(
            "INC-2419 mobile checkout telemetry watch: timeout counts are back under threshold after the rollback. "
            "Metrics-only note for the dashboard; it has no client mailing details."
        ),
        create_at_ms=dt_ms(2026, 10, 1, 13, 10),
    )
    desk_queue_draft_note = MattermostPostAsset(
        team="company",
        channel=DESK_QUEUE_CHANNEL,
        username="harper-lewis",
        message=(
            "Warehouse label printer queue is waiting on a replacement cartridge; no customer follow-up is needed from this note."
        ),
        create_at_ms=dt_ms(2026, 10, 1, 13, 20),
    )
    desk_queue_owner_note = MattermostPostAsset(
        team="company",
        channel=DESK_QUEUE_CHANNEL,
        username="harper-lewis",
        message=(
            "Harper is also watching the badge-access backlog this afternoon; those tickets should stay separate from incident handoffs."
        ),
        create_at_ms=dt_ms(2026, 10, 1, 13, 35),
    )
    target_incident = MattermostFilePostAsset(
        team="company",
        channel=DESK_QUEUE_CHANNEL,
        username="harper-lewis",
        message=(
            "INC-2419 Mobile checkout timeout. Follow-up owner: Harper Lewis. "
            "Review deadline: October 4, 2026 at 10:00 AM. Send the action plan to the client-success mailbox "
            "and schedule internal review 30 minutes before the deadline."
        ),
        filename=TARGET_FILE,
        mime_type="text/plain",
        source_path=f"assets/{TARGET_FILE}",
        create_at_ms=dt_ms(2026, 10, 1, 14),
    )
    distractor_incident = MattermostFilePostAsset(
        team="company",
        channel=DESK_QUEUE_CHANNEL,
        username="harper-lewis",
        message="INC-2420 Search indexing delay. Later deadline and different recipient.",
        filename="search_indexing_plan.txt",
        mime_type="text/plain",
        source_path="assets/search_indexing_plan.txt",
        create_at_ms=dt_ms(2026, 10, 1, 15),
    )
    desk_queue_metrics_note = MattermostPostAsset(
        team="company",
        channel=DESK_QUEUE_CHANNEL,
        username="harper-lewis",
        message=(
            "Mobile checkout timeout dashboard note: the graph looks stable now. This is monitoring chatter only, with no deadline or attachment."
        ),
        create_at_ms=dt_ms(2026, 10, 1, 15, 25),
    )

    release_log_posts = (
        MattermostFilePostAsset(
            team="company",
            channel=RELEASE_LOG_CHANNEL,
            username="harper-lewis",
            message=(
                "Mobile checkout rollback was deployed after the bridge. Engineering floated a tentative October 4 at 10:30 AM log-review sync for release validation only."
            ),
            filename="checkout_rollback_notes.txt",
            mime_type="text/plain",
            source_path="assets/checkout_rollback_notes.txt",
            create_at_ms=dt_ms(2026, 10, 1, 16),
        ),
        MattermostPostAsset(
            team="company",
            channel=RELEASE_LOG_CHANNEL,
            username="harper-lewis",
            message="Release 2026.10.01 search suggestions hotfix passed smoke tests; no customer incident follow-up is attached.",
            create_at_ms=dt_ms(2026, 10, 1, 16, 5),
        ),
        MattermostPostAsset(
            team="company",
            channel=RELEASE_LOG_CHANNEL,
            username="harper-lewis",
            message="Payment handoff library patch notes are archived for engineering review only; they are not client-success instructions.",
            create_at_ms=dt_ms(2026, 10, 1, 16, 10),
        ),
        MattermostPostAsset(
            team="company",
            channel=RELEASE_LOG_CHANNEL,
            username="harper-lewis",
            message="Search indexing deploy had delayed logs; keep this separate from the mobile checkout timeout follow-up.",
            create_at_ms=dt_ms(2026, 10, 1, 16, 15),
        ),
        MattermostPostAsset(
            team="company",
            channel=RELEASE_LOG_CHANNEL,
            username="harper-lewis",
            message="Release note reminder: deployment logs and rollback chatter are engineering records, not customer handoff packets.",
            create_at_ms=dt_ms(2026, 10, 1, 16, 20),
        ),
    )

    team_board_posts = (
        MattermostFilePostAsset(
            team="company",
            channel=TEAM_BOARD_CHANNEL,
            username="harper-lewis",
            message=(
                "Client Success asked for the quarterly invoice-portal FAQ list. This is unrelated to the mobile checkout incident queue."
            ),
            filename="client_success_questions.txt",
            mime_type="text/plain",
            source_path="assets/client_success_questions.txt",
            create_at_ms=dt_ms(2026, 10, 1, 16, 30),
        ),
        MattermostPostAsset(
            team="company",
            channel=TEAM_BOARD_CHANNEL,
            username="harper-lewis",
            message="Team board reminder: office-hours calendar holds should use the People Ops schedule, not release-log notes.",
            create_at_ms=dt_ms(2026, 10, 1, 16, 35),
        ),
        MattermostPostAsset(
            team="company",
            channel=TEAM_BOARD_CHANNEL,
            username="harper-lewis",
            message="Harper is available for facilities intake after 3 PM; keep those updates out of engineering incident channels.",
            create_at_ms=dt_ms(2026, 10, 1, 16, 40),
        ),
        MattermostPostAsset(
            team="company",
            channel=TEAM_BOARD_CHANNEL,
            username="harper-lewis",
            message="Client Success prefers a short summary for the invoice-portal FAQ refresh, not the full meeting notes.",
            create_at_ms=dt_ms(2026, 10, 1, 16, 45),
        ),
        MattermostPostAsset(
            team="company",
            channel=TEAM_BOARD_CHANNEL,
            username="harper-lewis",
            message="Reminder: the team-board lunch poll closes tomorrow at noon.",
            create_at_ms=dt_ms(2026, 10, 1, 16, 50),
        ),
    )

    mail_account = MailAccountAsset(display_name="Operations Desk", email="ops.desk@example.com")
    expected_mail = MailMessageAsset(
        mailbox="sent",
        from_name=mail_account.display_name,
        from_email="test@gmail.com",
        to=["client-success@example.com"],
        subject="INC-2419 checkout timeout action plan",
        body=MAIL_BODY,
        attachments=[MailAttachment(filename=TARGET_FILE, mime_type="text/plain", text_content=ACTION_PLAN_TEXT)],
        read=True,
    )
    review_event = CalendarEventAsset(
        title="INC-2419 internal review",
        start_ms=dt_ms(2026, 10, 4, 9, 30),
        end_ms=dt_ms(2026, 10, 4, 10, 0),
        description="Mobile checkout timeout follow-up with Harper Lewis.",
        timezone="UTC",
        reminder_minutes=(30,),
    )
    elementx_member = ElementXUserAsset(username="v2-04-ops-member", display_name="Ops Follow-up Member")
    release_member = ElementXUserAsset(username="v2-04-release-member", display_name="Release Watch Member")
    client_member = ElementXUserAsset(username="v2-04-client-member", display_name="Client Questions Member")
    schedule_member = ElementXUserAsset(username="v2-04-schedule-member", display_name="Schedule Desk Member")
    elementx_room = ElementXRoomAsset(
        name="Blue Handoff",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=[elementx_member.username],
        alias_localpart=ROOM_ALIAS,
        topic=ELEMENTX_ROOM_TOPIC,
    )
    release_room = ElementXRoomAsset(
        name="Release Watch",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=[release_member.username],
        alias_localpart=RELEASE_ROOM_ALIAS,
        topic="release rollback review",
    )
    client_room = ElementXRoomAsset(
        name="Client Questions",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=[client_member.username],
        alias_localpart=CLIENT_ROOM_ALIAS,
        topic="client-success intake questions",
    )
    schedule_room = ElementXRoomAsset(
        name="Schedule Desk",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=[schedule_member.username],
        alias_localpart=SCHEDULE_ROOM_ALIAS,
        topic="tentative review holds",
    )
    elementx_room_note = ElementXMessageAsset(
        room=ROOM_ALIAS,
        sender_username=elementx_member.username,
        text=ELEMENTX_ROOM_NOTE,
        created_at_ms=dt_ms(2026, 10, 1, 17),
    )
    release_room_note = ElementXMessageAsset(
        room=RELEASE_ROOM_ALIAS,
        sender_username=release_member.username,
        text="Use this room for rollback notes and tentative engineering log-review syncs.",
        created_at_ms=dt_ms(2026, 10, 1, 17, 5),
    )
    client_room_note = ElementXMessageAsset(
        room=CLIENT_ROOM_ALIAS,
        sender_username=client_member.username,
        text="Use this room for client-success questions before the final action plan is sent.",
        created_at_ms=dt_ms(2026, 10, 1, 17, 10),
    )
    schedule_room_note = ElementXMessageAsset(
        room=SCHEDULE_ROOM_ALIAS,
        sender_username=schedule_member.username,
        text="Use this room for tentative holds only; final incident review times come from the action-plan deadline.",
        created_at_ms=dt_ms(2026, 10, 1, 17, 15),
    )
    prep_alarm = AlarmAsset(
        hour=9,
        minute=0,
        label="INC-2419 review prep",
        enabled=True,
        days_of_week=(),
        vibrate=True,
        scheduled_year=2026,
        scheduled_month=10,
        scheduled_day=4,
    )
    assets = (
        desk_queue_channel,
        release_log_channel,
        team_board_channel,
        mattermost_user,
        MattermostSessionAsset(username="harper-lewis"),
        old_incident,
        desk_queue_status_note,
        desk_queue_draft_note,
        desk_queue_owner_note,
        target_incident,
        distractor_incident,
        desk_queue_metrics_note,
        *release_log_posts,
        *team_board_posts,
        mail_account,
        elementx_member,
        release_member,
        client_member,
        schedule_member,
        elementx_room,
        release_room,
        client_room,
        schedule_room,
        elementx_room_note,
        release_room_note,
        client_room_note,
        schedule_room_note,
    )

    goal = (
        "Open Mattermost and process the unresolved incident follow-up for the mobile checkout timeout. "
        "Inspect the relevant-looking Mattermost channels and use the incident file post plus its action-plan attachment to send the required Mail follow-up, schedule the internal review, "
        "notify the follow-up room, and set a prep alarm. For Mail, use the recipient, subject, body note, and attachment from the target action-plan file, "
        "and preserve the attachment's original filename when saving or attaching it. "
        "For Calendar, title the event `<incident ID> internal review`, schedule it from 30 minutes before the deadline until the deadline, "
        "set a 30-minute reminder, and use description format `<incident title> follow-up with <follow-up owner>.` "
        "For ElementX, find the group room matching the room criteria in the action-plan file, then use format `<incident ID> action plan sent to <recipient>. Internal review is scheduled for <month day> at <time>.` "
        "For ElementX date/time formatting, examples use sample values only: write the month and day like January 2 and the time like 5:45 PM. "
        "For Clock, set a prep alarm 30 minutes before the internal review with vibration on and label `<incident ID> review prep`."
    )

    def criteria(self):
        return [
            AssetExists(self.expected_mail, task=self),
            AssetExists(self.review_event, task=self),
            AssetExists(
                ElementXMessageAsset(
                    room=ROOM_ALIAS,
                    sender_username="testuser",
                    sender_password="testpass123",
                    text=ELEMENTX_NOTICE,
                ),
                task=self,
            ),
            AssetExists(self.prep_alarm, task=self),
        ]
