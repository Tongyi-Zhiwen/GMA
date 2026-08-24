from __future__ import annotations

from pathlib import Path

from gma.apps.xiaoshiliu import XIAOSHILIU_DEFAULT_AVATAR, XIAOSHILIU_LOGIN_USER_ID
from gma.assets import (
    ContactAsset,
    DeviceFileAsset,
    ElementXMessageAsset,
    ElementXRoomAsset,
    ElementXUserAsset,
    ImageContentExpectation,
    MastodonAccountAsset,
    MastodonFollowAsset,
    MastodonMediaAttachment,
    MastodonMediaStatusAsset,
    MastodonSessionAsset,
    MastodonStatusAsset,
    SmsMessageAsset,
    TempusPlaylistAsset,
    XiaoShiLiuCommentAsset,
    XiaoShiLiuPostAsset,
    XiaoShiLiuUserAsset,
)
from gma.evaluation import AssetExists
from gma.tasks.base import BaseTask


ROOM_ALIAS = "v2-05-music-planning-group"
PLAYLIST_TITLE = "Acoustic Night Recap"
TOP_SONG = "Lego House"
FINAL_POST_CONTENT = "Top song: Lego House. Mood: warm and acoustic. Highlight: final chorus singalong."
ELEMENTX_RECAP = (
    "Acoustic Night recap: top recommendation Lego House. Playlist Acoustic Night Recap includes "
    "Lego House, The A Team, and Drunk. Mood: warm and acoustic. Highlight: final chorus singalong."
)
SMS_TEXT = "The Acoustic Night Recap playlist is ready. Top song: Lego House."
STAGE_IMAGE = "acoustic_stage.png"
DINNER_IMAGE = "dinner_table.png"
XSL_AUTHOR_ID = "v2-05-acoustic-notes"
XSL_COMMENTER_ID = "v2-05-campus-listener"
XSL_DISTRACTOR_ID = "v2-05-campus-life-notes"


class SocialEventRecapPlaylistTask(BaseTask):
    apps = {"Mastodon", "XiaoShiLiu", "Tempus", "Gallery", "ElementX", "Messages"}
    difficulty = "realistic"
    category = ['Information-Gathering Tasks', 'Selection / Optimization Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    max_steps = 190

    mastodon_accounts = (
        MastodonAccountAsset(username="campus-events", email="campus.events@example.com", display_name="Campus Events"),
        MastodonAccountAsset(username="music-club", email="music.club@example.com", display_name="Music Club"),
        MastodonAccountAsset(username="stage-crew", email="stage.crew@example.com", display_name="Stage Crew"),
        MastodonAccountAsset(username="student-union", email="student.union@example.com", display_name="Student Union"),
    )
    mastodon_follows = (
        MastodonFollowAsset(follower_username="owner", followed_username="campus-events"),
        MastodonFollowAsset(follower_username="owner", followed_username="music-club"),
        MastodonFollowAsset(follower_username="owner", followed_username="stage-crew"),
        MastodonFollowAsset(follower_username="owner", followed_username="student-union"),
    )
    main_mastodon_prompt = "Acoustic Night recap team: which song should anchor the follow-up playlist, and what mood should the recap carry?"
    dance_mastodon_prompt = "Dance Showcase crew: which afterparty tracks kept people moving?"
    mastodon_posts = (
        MastodonStatusAsset(username="campus-events", text=main_mastodon_prompt, visibility="public"),
        MastodonStatusAsset(
            username="music-club",
            text="My vote is Lego House. The room leaned into that chorus, and it still feels like the warmest acoustic pick for the recap.",
            visibility="public",
            reply_to_username="campus-events",
            reply_to_text=main_mastodon_prompt,
        ),
        MastodonStatusAsset(
            username="stage-crew",
            text="The A Team belongs on the follow-up playlist too; it fit the stripped-down set even if it was not the loudest singalong.",
            visibility="public",
            reply_to_username="campus-events",
            reply_to_text=main_mastodon_prompt,
        ),
        MastodonStatusAsset(
            username="student-union",
            text="Seconding Lego House for the top recommendation. It was the song people were still humming on the way out.",
            visibility="public",
            reply_to_username="campus-events",
            reply_to_text=main_mastodon_prompt,
        ),
        MastodonStatusAsset(
            username="campus-events",
            text="Photograph had a nice quiet pause, but I would treat it as a softer mention rather than the anchor track.",
            visibility="public",
            reply_to_username="campus-events",
            reply_to_text=main_mastodon_prompt,
        ),
        MastodonStatusAsset(
            username="student-union",
            text="For the written recap, Student Union notes the Acoustic Night mood as warm and acoustic; please keep that wording.",
            visibility="public",
        ),
        MastodonStatusAsset(username="campus-events", text="Book swap volunteers can pick up badges at the library desk after lunch; the first table is for fiction trades.", visibility="public"),
        MastodonStatusAsset(username="music-club", text="Practice room 2 has the upright piano tuned again for this week's lessons, so please leave the bench height where you found it.", visibility="public"),
        MastodonStatusAsset(username="stage-crew", text="After debate rehearsal we found a spare HDMI adapter by the sound board; message stage crew if it is yours.", visibility="public"),
        MastodonStatusAsset(username="student-union", text="The cafeteria survey closes Friday night. Please vote before the form locks so dining can count the breakfast notes.", visibility="public"),
        MastodonStatusAsset(username="campus-events", text=dance_mastodon_prompt, visibility="public"),
        MastodonStatusAsset(
            username="music-club",
            text="Blinding Lights worked for the Dance Showcase afterparty because people wanted something bright and fast after cleanup.",
            visibility="public",
            reply_to_username="campus-events",
            reply_to_text=dance_mastodon_prompt,
        ),
        MastodonStatusAsset(
            username="student-union",
            text="Levitating got the most dance-floor energy there, but that is a different event from Acoustic Night.",
            visibility="public",
            reply_to_username="campus-events",
            reply_to_text=dance_mastodon_prompt,
        ),
    )
    xsl_author = XiaoShiLiuUserAsset(
        user_id=XSL_AUTHOR_ID,
        nickname="Acoustic Notes",
        email="acoustic.notes@example.com",
        avatar=XIAOSHILIU_DEFAULT_AVATAR,
    )
    xsl_commenter = XiaoShiLiuUserAsset(
        user_id=XSL_COMMENTER_ID,
        nickname="Campus Listener",
        email="campus.listener@example.com",
        avatar=XIAOSHILIU_DEFAULT_AVATAR,
    )
    xsl_distractor_author = XiaoShiLiuUserAsset(
        user_id=XSL_DISTRACTOR_ID,
        nickname="Campus Life Notes",
        email="campus.life.notes@example.com",
        avatar=XIAOSHILIU_DEFAULT_AVATAR,
    )
    xsl_posts = (
        XiaoShiLiuPostAsset(
            author_user_id=xsl_distractor_author.user_id,
            title="Practice Room Sign-Up Notes",
            content="Practice room 2 has the piano again, and the late slot is easier to book after club rehearsal.",
            category="Campus Life",
            tags=["practice", "rooms"],
            image_urls=[f"/assets/{DINNER_IMAGE}"],
            min_image_count=1,
            created_at_ms=1790846500000,
        ),
        XiaoShiLiuPostAsset(
            author_user_id=xsl_distractor_author.user_id,
            title="Campus Market Table Photos",
            content="The campus market table looked better with the small string lights than with the old banner.",
            category="Campus Life",
            tags=["market", "photos"],
            image_urls=[f"/assets/{DINNER_IMAGE}"],
            min_image_count=1,
            created_at_ms=1790846420000,
        ),
        XiaoShiLiuPostAsset(
            author_user_id=xsl_distractor_author.user_id,
            title="Rainy Library Study Corner",
            content="The quiet corner near the west windows was perfect for rainy-day study notes and tea.",
            category="Campus Life",
            tags=["library", "study"],
            image_urls=[f"/assets/{DINNER_IMAGE}"],
            min_image_count=1,
            created_at_ms=1790846360000,
        ),
        XiaoShiLiuPostAsset(
            author_user_id=xsl_author.user_id,
            title="Acoustic Night Highlights",
            content="For the recap post, the highlight should be the final chorus singalong. Lego House came up again in the notes, but keep the highlight wording focused on that closing chorus.",
            category="Music",
            tags=["Acoustic Night"],
            image_urls=[f"/assets/{STAGE_IMAGE}"],
            min_image_count=1,
            created_at_ms=1790845800000,
        ),
        XiaoShiLiuPostAsset(
            author_user_id=xsl_author.user_id,
            title="Campus Playlist Ideas",
            content="My Acoustic Night short list was Perfect, The A Team, and Lego House. Lego House is the one I heard people mention after the show.",
            category="Music",
            tags=["playlist"],
            image_urls=[f"/assets/{STAGE_IMAGE}"],
            min_image_count=1,
            created_at_ms=1790845200000,
        ),
        XiaoShiLiuPostAsset(
            author_user_id=xsl_author.user_id,
            title="Acoustic Night Afterthoughts",
            content="The stripped-down set made the room feel close and warm. The cleanup snacks were a nice ending, but the last songs are what people kept talking about afterward.",
            category="Music",
            tags=["Acoustic Night"],
            created_at_ms=1790844600000,
        ),
        XiaoShiLiuPostAsset(
            author_user_id=xsl_author.user_id,
            title="Acoustic Night Recap Details",
            content=(
                "I think Acoustic Night Recap has the right romantic feel as the follow-up playlist title. "
                "Tempus note for this recap: use the album + versions when adding songs to the playlist."
            ),
            category="Music",
            tags=["notes"],
            image_urls=[f"/assets/{STAGE_IMAGE}"],
            min_image_count=1,
            created_at_ms=1790844000000,
        ),
        XiaoShiLiuPostAsset(
            author_user_id=xsl_distractor_author.user_id,
            title="Dance Showcase Notes",
            content="Dance Showcase afterparty notes: Stage Lights Mix sounded like a good title, with Blinding Lights for the opener.",
            category="Music",
            tags=["dance", "showcase"],
            image_urls=[f"/assets/{DINNER_IMAGE}"],
            min_image_count=1,
            created_at_ms=1790843400000,
        ),
        XiaoShiLiuPostAsset(
            author_user_id=xsl_distractor_author.user_id,
            title="Dorm Plant Swap Photos",
            content="The plant swap table looked best next to the window. I saved the fern close-up for the campus life album.",
            category="Campus Life",
            tags=["plants"],
            image_urls=[f"/assets/{DINNER_IMAGE}"],
            min_image_count=1,
            created_at_ms=1790843000000,
        ),
        XiaoShiLiuPostAsset(
            author_user_id=xsl_distractor_author.user_id,
            title="Late Study Snack Board",
            content="The dinner table photo works for the snack board recap, especially with the tea cups and notebooks in frame.",
            category="Campus Life",
            tags=["food", "study"],
            image_urls=[f"/assets/{DINNER_IMAGE}"],
            min_image_count=1,
            created_at_ms=1790842600000,
        ),
    )
    xsl_comments = (
        XiaoShiLiuCommentAsset(
            post_title="Acoustic Night Highlights",
            post_author_user_id=xsl_author.user_id,
            author_user_id=xsl_commenter.user_id,
            content="That last chorus was the part everyone kept talking about on the walk out.",
            created_at_ms=1790845900000,
        ),
        XiaoShiLiuCommentAsset(
            post_title="Campus Playlist Ideas",
            post_author_user_id=xsl_author.user_id,
            author_user_id=xsl_commenter.user_id,
            content="I also saw The A Team come up in the Mastodon replies, but Lego House seemed to show up everywhere.",
            created_at_ms=1790845300000,
        ),
        XiaoShiLiuCommentAsset(
            post_title="Acoustic Night Afterthoughts",
            post_author_user_id=xsl_author.user_id,
            author_user_id=xsl_commenter.user_id,
            content="Same feeling here; the music felt more memorable than the cleanup chatter.",
            created_at_ms=1790844700000,
        ),
        XiaoShiLiuCommentAsset(
            post_title="Dance Showcase Notes",
            post_author_user_id=xsl_distractor_author.user_id,
            author_user_id=xsl_commenter.user_id,
            content="Stage Lights Mix fits the dance team, but it has a totally different mood from the acoustic set.",
            created_at_ms=1790843500000,
        ),
        XiaoShiLiuCommentAsset(
            post_title="Late Study Snack Board",
            post_author_user_id=xsl_distractor_author.user_id,
            author_user_id=xsl_commenter.user_id,
            content="This table shot is cozy, just more snack-table than stage recap.",
            created_at_ms=1790842700000,
        ),
    )
    stage_photo = DeviceFileAsset(
        app="Gallery",
        storage_dir="DCIM/Camera",
        filename=STAGE_IMAGE,
        mime_type="image/png",
        source_path=f"assets/{STAGE_IMAGE}",
    )
    dinner_photo = DeviceFileAsset(
        app="Gallery",
        storage_dir="DCIM/Camera",
        filename=DINNER_IMAGE,
        mime_type="image/png",
        source_path=f"assets/{DINNER_IMAGE}",
    )
    group_member = ElementXUserAsset(username="v2-05-music-member", display_name="Music Planner")
    music_room = ElementXRoomAsset(
        name="Music Planning Group",
        room_type="group",
        creator_username="testuser",
        creator_password="testpass123",
        members=[group_member.username],
        alias_localpart=ROOM_ALIAS,
        topic="Music planning",
    )
    casey = ContactAsset(name="Casey Morgan", phone_number="+15550100860")
    expected_playlist = TempusPlaylistAsset(
        name=PLAYLIST_TITLE,
        owner_username="testuserfjx",
        track_titles=["Lego House", "The A Team", "Drunk"],
        track_albums={"Lego House": "+", "The A Team": "+", "Drunk": "+"},
    )
    expected_post = XiaoShiLiuPostAsset(
        author_user_id=XIAOSHILIU_LOGIN_USER_ID,
        title=PLAYLIST_TITLE,
        content=FINAL_POST_CONTENT,
        category="Music",
        tags=["Acoustic Night", "recap"],
        min_image_count=1,
        expected_images=(ImageContentExpectation(filename=STAGE_IMAGE, source_path=str(Path(__file__).with_name("assets") / STAGE_IMAGE)),),
    )
    expected_mastodon = MastodonMediaStatusAsset(
        username="owner",
        text=FINAL_POST_CONTENT,
        visibility="public",
        media_attachments=(
            MastodonMediaAttachment(filename=STAGE_IMAGE, mime_type="image/png", source_path=f"assets/{STAGE_IMAGE}"),
        ),
    )
    assets = (
        MastodonSessionAsset(username="owner"),
        *mastodon_accounts,
        *mastodon_follows,
        *mastodon_posts,
        xsl_author,
        xsl_commenter,
        xsl_distractor_author,
        *xsl_posts,
        *xsl_comments,
        stage_photo,
        dinner_photo,
        group_member,
        music_room,
        casey,
    )

    goal = (
        "Use Mastodon to collect the Acoustic Night song recommendations and recap mood. Use XiaoShiLiu to collect the playlist title, highlight, and Tempus album-version note. "
        "Use this song-selection rule: choose the song "
        "that appears in both Mastodon and XiaoShiLiu Acoustic Night discussions; if more than one song appears in both, choose the one "
        "with the highest total mentions across those Acoustic Night discussions. "
        "Create a Tempus playlist using the collected playlist title and add exactly the songs <top song>, The A Team, and Drunk; use the XiaoShiLiu album-version note to resolve which album versions to add. "
        "Use the Gallery image that best fits the Acoustic Night recap post for both recap uploads. "
        "Publish a XiaoShiLiu post in the Music category with title <playlist title>, tags Acoustic Night and recap, attach the selected Gallery image, and use content format "
        "`Top song: <top song>. Mood: <mood>. Highlight: <highlight>.` Publish a public Mastodon post with the same content and attach the selected Gallery image. "
        "Notify Music Planning Group in ElementX using the format "
        "`Acoustic Night recap: top recommendation <top song>. Playlist <playlist title> includes <top song>, The A Team, and Drunk. Mood: <mood>. Highlight: <highlight>.` "
        "Send Casey Morgan an SMS using the format `The <playlist title> playlist is ready. Top song: <top song>.`"
    )

    user_interaction = (
        "If the agent asks which Gallery image to use for the Acoustic Night recap uploads, answer exactly: "
        "Use the stage image."
    )

    def criteria(self):
        return [
            AssetExists(self.expected_playlist, task=self),
            AssetExists(self.expected_post, task=self),
            AssetExists(self.expected_mastodon, task=self),
            AssetExists(
                ElementXMessageAsset(
                    room=ROOM_ALIAS,
                    sender_username="testuser",
                    sender_password="testpass123",
                    text=ELEMENTX_RECAP,
                ),
                task=self,
            ),
            AssetExists(SmsMessageAsset(address=self.casey.phone_number, body=SMS_TEXT, box="sent", read=True), task=self),
        ]
