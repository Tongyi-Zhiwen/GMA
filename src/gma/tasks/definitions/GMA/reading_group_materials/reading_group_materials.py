from __future__ import annotations

from datetime import UTC, datetime

from gma.assets import (
    CalendarEventAsset,
    DeviceFileAsset,
    ElementXFileAsset,
    ElementXMessageAsset,
    ElementXRoomAsset,
    ElementXSessionAsset,
    ElementXUserAsset,
    MailAccountAsset,
    MailAttachment,
    MailMessageAsset,
    TempusPlaylistAsset,
    TempusSessionAsset,
)
from gma.evaluation import AssetExists
from gma.tasks.base import BaseTask


def utc_ms(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    return int(datetime(year, month, day, hour, minute, tzinfo=UTC).timestamp() * 1000)


TARGET_ROOM_ALIAS = "v2-17-paper-circle"
SEMINAR_ROOM_ALIAS = "v2-17-seminar-logistics"
BOOK_ROOM_ALIAS = "v2-17-book-notes"
PAPER_FILE = "mobile-agents-contrastive-rev-b.txt"
PAPER_TITLE = "Contrastive Learning for Mobile Agents"
PAPER_TEXT = (
    "Title: Contrastive Learning for Mobile Agents\n"
    "Packet: revision B for the Oct 6 reading group\n"
    "Key update: Figure 2 and the method-comparison paragraph in Section 3 were refreshed after the author reply.\n"
)
AGENDA_TEXT = (
    "Reading group set for Oct 6 at 16:00 in Library Room 204. Paper: Contrastive Learning for Mobile Agents (rev B). "
    "Agenda priority: section 3 method comparison, then failure cases. Quiet Reading Focus playlist is ready."
)
QUIET_TRACKS = ["The A Team", "Lego House", "Grade 8"]
QUIET_TRACK_ALBUMS = {"The A Team": "+", "Lego House": "+", "Grade 8": "+"}


class ReadingGroupMaterialsTask(BaseTask):
    apps = {"Mail", "Files", "ElementX", "Calendar", "Tempus"}
    difficulty = "realistic"
    category = ["Multi-Step Workflow Tasks"]
    snapshot = "gma_ready_state"
    max_steps = 180

    account = MailAccountAsset(display_name="Reading Group Host", email="reading.host@example.com")

    paper_archive_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Paper Coordinator",
        from_email="papers@example.com",
        to=[account.email],
        subject="September paper archive",
        body="Keeping the September packet in the archive. That discussion centered on representation drift and Section 2.",
        attachments=[
            MailAttachment(
                filename="mobile-agents-contrastive-sept.txt",
                mime_type="text/plain",
                text_content=(
                    "Title: Contrastive Learning for Mobile Agents\n"
                    "Packet: September archive\n"
                    "Focus: Section 2 representation drift.\n"
                ),
            )
        ],
        timestamp_ms=utc_ms(2026, 9, 23, 10),
        read=True,
    )
    draft_packet_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Paper Coordinator",
        from_email="papers@example.com",
        to=[account.email],
        subject="Oct 6 packet draft",
        body=(
            "The first Oct 6 packet is attached for early reading. I am still waiting on the author note about Figure 2 "
            "and the Section 3 method-comparison paragraph."
        ),
        attachments=[
            MailAttachment(
                filename="mobile-agents-contrastive-rev-a.txt",
                mime_type="text/plain",
                text_content=(
                    "Title: Contrastive Learning for Mobile Agents\n"
                    "Packet: revision A for Oct 6\n"
                    "Open note: Figure 2 and Section 3 method comparison are still pending author response.\n"
                ),
            )
        ],
        timestamp_ms=utc_ms(2026, 9, 30, 17),
        read=True,
    )
    author_reply_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Paper Coordinator",
        from_email="papers@example.com",
        to=[account.email],
        subject="Author reply folded into Oct 6 packet",
        body=(
            "The author reply has been folded into the Oct 6 packet. The attached rev-b file keeps the same paper title, "
            "refreshes Figure 2, and makes Section 3 method comparison the right opener before failure cases."
        ),
        attachments=[MailAttachment(filename=PAPER_FILE, mime_type="text/plain", text_content=PAPER_TEXT)],
        timestamp_ms=utc_ms(2026, 10, 1, 9),
        read=False,
    )
    library_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Library Desk",
        from_email="library@example.com",
        to=[account.email],
        subject="Screen-share rooms for Tuesday groups",
        body="For Tuesday study groups, Library Room 204 has the large display and quiet-discussion setup. Ask the group to stay within the reserved hour.",
        timestamp_ms=utc_ms(2026, 10, 1, 10, 30),
        read=False,
    )
    catering_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Campus Cafe",
        from_email="cafe@example.com",
        to=[account.email],
        subject="Coffee urn pickup window",
        body="Coffee urn pickup is 13:00-14:00 on Tuesday. This is separate from room access.",
        timestamp_ms=utc_ms(2026, 10, 1, 11),
        read=False,
    )

    prior_week_agenda = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="prior-week-agenda.txt",
        mime_type="text/plain",
        text_content="Prior week agenda: representation drift recap, Section 2 examples, short wrap-up.\n",
    )
    prior_week_notes = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="prior-week-reading-notes.txt",
        mime_type="text/plain",
        text_content="Notes from the September packet. Most examples refer to Section 2 and the archive file.\n",
    )
    current_notes = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="method-comparison-notes.txt",
        mime_type="text/plain",
        text_content=(
            "Oct 6 prep notes: Section 3 method comparison connects the new Figure 2 to the agent trace examples. "
            "Failure cases should follow while the comparison table is still fresh.\n"
        ),
    )
    room_holds = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="oct6-room-holds.txt",
        mime_type="text/plain",
        text_content=(
            "Oct 6 room holds: Library Room 201 14:00-15:00; Lab Annex 15:00-16:00; "
            "Library Room 204 16:00-17:00 with screen-share and quiet-discussion setup.\n"
        ),
    )
    playlist_note = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="quiet-study-track-card.txt",
        mime_type="text/plain",
        text_content=(
            "Reading-session playlist card: keep the playlist private and use the three quiet + album tracks: "
            "The A Team, Lego House, Grade 8. Leave the rehearsal-energy mix for talks.\n"
        ),
    )
    summary_template = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="reading-group-summary-template.txt",
        mime_type="text/plain",
        text_content="Agenda template: session time, room, paper title and packet marker, priority topics, shared material, playlist.\n",
    )
    seminar_notes = DeviceFileAsset(
        app="Files",
        storage_dir="Download",
        filename="seminar-speaker-notes.txt",
        mime_type="text/plain",
        text_content="Seminar notes for a different group: invited talk prep in Lab Annex, demo rehearsal first, Q&A second.\n",
    )
    expected_download = DeviceFileAsset(app="Files", storage_dir="Download", filename=PAPER_FILE, mime_type="text/plain", text_content=PAPER_TEXT)

    member_alex = ElementXUserAsset(username="v2-17-alex", password="password", display_name="Alex Reader")
    member_morgan = ElementXUserAsset(username="v2-17-morgan", password="password", display_name="Morgan Reader")
    member_priya = ElementXUserAsset(username="v2-17-priya", password="password", display_name="Priya Methods")
    member_taylor = ElementXUserAsset(username="v2-17-taylor", password="password", display_name="Taylor Host")
    member_jules = ElementXUserAsset(username="v2-17-jules", password="password", display_name="Jules Seminar")

    target_room = ElementXRoomAsset(
        name="Tuesday Paper Circle",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=["v2-17-alex", "v2-17-morgan", "v2-17-priya", "v2-17-taylor"],
        alias_localpart=TARGET_ROOM_ALIAS,
        topic="Oct 6 reading materials and discussion order",
    )
    seminar_room = ElementXRoomAsset(
        name="Seminar Logistics",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=["v2-17-jules", "v2-17-taylor"],
        alias_localpart=SEMINAR_ROOM_ALIAS,
        topic="Invited talk rehearsal logistics",
    )
    book_room = ElementXRoomAsset(
        name="Book Notes",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=["v2-17-alex", "v2-17-morgan"],
        alias_localpart=BOOK_ROOM_ALIAS,
        topic="Informal book-club notes",
    )
    target_messages = (
        ElementXMessageAsset(
            room=TARGET_ROOM_ALIAS,
            sender_username="v2-17-alex",
            sender_password="password",
            text="For Oct 6, I am done with the Section 2 recap unless someone needs one slide of background.",
            created_at_ms=utc_ms(2026, 10, 1, 11),
        ),
        ElementXMessageAsset(
            room=TARGET_ROOM_ALIAS,
            sender_username="v2-17-morgan",
            sender_password="password",
            text="I can lead the method-comparison pass. It will make more sense before we debate failure cases.",
            created_at_ms=utc_ms(2026, 10, 1, 11, 8),
        ),
        ElementXMessageAsset(
            room=TARGET_ROOM_ALIAS,
            sender_username="v2-17-priya",
            sender_password="password",
            text="Agree: Section 3 method comparison first, failure cases second. The representation recap can be a backup only.",
            created_at_ms=utc_ms(2026, 10, 1, 11, 14),
        ),
        ElementXMessageAsset(
            room=TARGET_ROOM_ALIAS,
            sender_username="v2-17-taylor",
            sender_password="password",
            text="Room 204 at 16:00 works for me if that is the screen-share hold we can keep.",
            created_at_ms=utc_ms(2026, 10, 1, 11, 20),
        ),
    )
    seminar_messages = (
        ElementXMessageAsset(
            room=SEMINAR_ROOM_ALIAS,
            sender_username="v2-17-jules",
            sender_password="password",
            text="For the invited talk rehearsal, use Lab Annex at 15:00 and start with the demo walkthrough.",
            created_at_ms=utc_ms(2026, 10, 1, 9, 5),
        ),
        ElementXMessageAsset(
            room=SEMINAR_ROOM_ALIAS,
            sender_username="v2-17-taylor",
            sender_password="password",
            text="That rehearsal can use the faster energy playlist from last month.",
            created_at_ms=utc_ms(2026, 10, 1, 9, 12),
        ),
    )
    book_messages = (
        ElementXMessageAsset(
            room=BOOK_ROOM_ALIAS,
            sender_username="v2-17-alex",
            sender_password="password",
            text="Book-club note: Chapter 4 discussion moved to next week; no paper packet needed.",
            created_at_ms=utc_ms(2026, 10, 1, 12),
        ),
    )

    calendar_hold_one = CalendarEventAsset(title="Advisor check-in", start_ms=utc_ms(2026, 10, 6, 14), end_ms=utc_ms(2026, 10, 6, 15), timezone="UTC")
    calendar_hold_two = CalendarEventAsset(title="Office hours", start_ms=utc_ms(2026, 10, 6, 15), end_ms=utc_ms(2026, 10, 6, 16), timezone="UTC")
    calendar_hold_three = CalendarEventAsset(title="Coffee urn pickup", start_ms=utc_ms(2026, 10, 6, 13), end_ms=utc_ms(2026, 10, 6, 14), timezone="UTC")
    session_event = CalendarEventAsset(
        title="Reading Group - Contrastive Learning",
        start_ms=utc_ms(2026, 10, 6, 16),
        end_ms=utc_ms(2026, 10, 6, 17),
        location="Library Room 204",
        description="Paper: Contrastive Learning for Mobile Agents (rev B). Priority: section 3 method comparison, then failure cases.",
        timezone="UTC",
        reminder_minutes=(30,),
    )

    seminar_playlist = TempusPlaylistAsset(
        name="Seminar Energy Draft",
        owner_username="testuserfjx",
        visibility="private",
        track_titles=["The A Team", "Lego House"],
        track_albums={"The A Team": "+", "Lego House": "+"},
    )
    old_reading_playlist = TempusPlaylistAsset(
        name="Quiet Reading Archive",
        owner_username="testuserfjx",
        visibility="private",
        track_titles=["The A Team"],
        track_albums={"The A Team": "+"},
    )
    playlist = TempusPlaylistAsset(
        name="Quiet Reading Focus",
        owner_username="testuserfjx",
        visibility="private",
        track_titles=QUIET_TRACKS,
        track_albums=QUIET_TRACK_ALBUMS,
    )
    expected_file_share = ElementXFileAsset(
        room=TARGET_ROOM_ALIAS,
        sender_username="testuser",
        sender_password="testpass123",
        filename=PAPER_FILE,
        mime_type="text/plain",
        text_content=PAPER_TEXT,
    )
    expected_agenda = ElementXMessageAsset(room=TARGET_ROOM_ALIAS, sender_username="testuser", sender_password="testpass123", text=AGENDA_TEXT)

    assets = (
        account,
        paper_archive_mail,
        draft_packet_mail,
        author_reply_mail,
        library_mail,
        catering_mail,
        prior_week_agenda,
        prior_week_notes,
        current_notes,
        room_holds,
        playlist_note,
        summary_template,
        seminar_notes,
        member_alex,
        member_morgan,
        member_priya,
        member_taylor,
        member_jules,
        target_room,
        seminar_room,
        book_room,
        ElementXSessionAsset(username="testuser", password="testpass123"),
        *target_messages,
        *seminar_messages,
        *book_messages,
        calendar_hold_one,
        calendar_hold_two,
        calendar_hold_three,
        TempusSessionAsset(username="testuserfjx", password="testpass123"),
        seminar_playlist,
        old_reading_playlist,
    )
    goal = (
        "Please prepare the next reading group session. Use Mail, Files, ElementX, Calendar, and Tempus. "
        "Find the latest Paper Coordinator Mail attachment that should be used for the Oct 6 reading group, determine the discussion order and room/time "
        "from the available evidence, and use the quiet-study track guidance for the playlist. Save the selected paper to Files "
        "and share that same file to the ElementX room whose topic/messages coordinate Oct 6 reading materials. Schedule a Calendar event titled "
        "'Reading Group - <paper short title>' with the selected room/time, description 'Paper: <paper title> (<packet marker>). "
        "Priority: <first topic>, then <second topic>.', and a 30-minute reminder. Write <first topic> and <second topic> in all lowercase. "
        "Use the first two words of the paper title for "
        "<paper short title>. Create a private Tempus playlist exactly named "
        "'Quiet Reading Focus' using the tracks named in Files. "
        "Send the ElementX group exactly using the format 'Reading group set for <date> at <time> in <room>. "
        "Paper: <paper title> (<packet marker>). Agenda priority: <first topic>, then <second topic>. Quiet Reading Focus playlist is ready.'."
        " Use these examples for formatting only: <date> 'Sep 14'; <time> '09:30'; <packet marker> 'rev C'."
    )

    def criteria(self):
        return [
            AssetExists(self.expected_download, task=self),
            AssetExists(self.session_event, task=self),
            AssetExists(self.playlist, task=self),
            AssetExists(self.expected_file_share, task=self),
            AssetExists(self.expected_agenda, task=self),
        ]
