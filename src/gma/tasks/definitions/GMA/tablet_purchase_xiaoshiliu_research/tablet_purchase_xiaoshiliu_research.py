from __future__ import annotations

from gma.apps.mall import MALL_LOGIN_CITY, MALL_LOGIN_NICKNAME, MALL_LOGIN_PHONE, MALL_LOGIN_USERNAME
from gma.apps.xiaoshiliu import XIAOSHILIU_DEFAULT_AVATAR
from gma.assets import (
    ContactAsset,
    MailAccountAsset,
    MailMessageAsset,
    MallAddressAsset,
    MallMemberAsset,
    SmsMessageAsset,
    XiaoShiLiuCommentAsset,
    XiaoShiLiuPostAsset,
    XiaoShiLiuUserAsset,
)
from gma.evaluation import AssetExists
from gma.evaluation.checks.mall import MallCheckoutOrderCreated
from gma.tasks.base import BaseTask


PRODUCT_NAME = "Lenovo Legion Y700 tablet 5th generation"
PRODUCT_SN = "ZAH20041CN"
AUTHOR_ID = "v2-03-compact-tablet-research"
SIDE_PRODUCT_AUTHOR_ID = "v2-03-side-product-distractors"
PDF_COMMENTER_ID = "v2-03-pdf-annotation-commenter"
YOGA_COMMENTER_ID = "v2-03-large-tablet-commenter"
COMMUTE_COMMENTER_ID = "v2-03-commute-study-commenter"
SURFACE_COMMENTER_ID = "v2-03-surface-go-commenter"
ACCESSORY_COMMENTER_ID = "v2-03-accessory-commenter"
REASON = "Y700 is an 8.8-inch compact tablet that is usable for PDF annotation and paperless note-taking"
CONTACT_BEFORE = ContactAsset(name="Younger Sister", phone_number="+15550152004")
CONTACT_AFTER = ContactAsset(
    name="Younger Sister",
    phone_number="+15550152004",
    notes=f"Selected: {PRODUCT_NAME}. Reason: {REASON}.",
)
SMS_TEXT = f"Bought {PRODUCT_NAME}. Reason: {REASON}."
SIZE_POST_TITLE = "Compact Tablet Size Comparison"
EVIDENCE_POST_TITLE = "Y700 PDF Annotation Notes"
WORKFLOW_POST_TITLE = "Paperless Study Workflow Tradeoffs"

POSTS = (
    XiaoShiLiuPostAsset(
        author_user_id=SIDE_PRODUCT_AUTHOR_ID,
        title="Dorm Desk Cable Reset",
        content="I finally labeled the charging cables on my dorm desk. The useful part was separating laptop, phone, and tablet chargers before midterms.",
        category="Technology",
        tags=["desk", "cables"],
        image_urls=["/assets/student-laptop.png"],
        min_image_count=1,
        created_at_ms=1790846500000,
    ),
    XiaoShiLiuPostAsset(
        author_user_id=AUTHOR_ID,
        title="Library Lamp Brightness Notes",
        content="The adjustable desk lamp made evening reading easier in the library corner, but it did not change which device I use for PDF notes.",
        category="Technology",
        tags=["study", "desk"],
        image_urls=["/assets/student-laptop.png"],
        min_image_count=1,
        created_at_ms=1790846480000,
    ),
    XiaoShiLiuPostAsset(
        author_user_id=SIDE_PRODUCT_AUTHOR_ID,
        title="Noise-Canceling Earbuds for Commute",
        content="Earbuds helped on the bus this week. They are useful study accessories, though they are not part of my tablet comparison notes.",
        category="Technology",
        tags=["audio", "commute"],
        image_urls=["/assets/phone-notes.png"],
        min_image_count=1,
        created_at_ms=1790846460000,
    ),
    XiaoShiLiuPostAsset(
        author_user_id=AUTHOR_ID,
        title=SIZE_POST_TITLE,
        content=(
            "Size notes for tablets I saw in Mall: Lenovo Legion Y700 tablet 5th generation is the 8.8-inch option; "
            "Surface Go 4 for Business feels more like a small Windows desk slate; "
            "Lenovo tablet YOGA Pad Pro 14.5 is a 14.5-inch large tablet. This post is only my size notebook before comparing study workflow."
        ),
        category="Technology",
        tags=["tablet", "size"],
        image_urls=["/assets/compact-tablet-study.png"],
        min_image_count=1,
        created_at_ms=1790845900000,
    ),
    XiaoShiLiuPostAsset(
        author_user_id=AUTHOR_ID,
        title=EVIDENCE_POST_TITLE,
        content=REASON,
        category="Technology",
        tags=["tablet", "study", "pdf"],
        image_urls=["/assets/compact-tablet-study.png"],
        min_image_count=1,
        created_at_ms=1790845850000,
    ),
    XiaoShiLiuPostAsset(
        author_user_id=AUTHOR_ID,
        title=WORKFLOW_POST_TITLE,
        content=(
            "Paperless study tradeoffs: large tablets are comfortable for drawing and desk use, while Windows-style tablets are better for desktop workflows. "
            "For commuting, PDF reading, and quick notes, I prefer a compact Android tablet when annotation feels responsive enough."
        ),
        category="Technology",
        tags=["tablet", "study", "pdf"],
        image_urls=["/assets/compact-tablet-study.png"],
        min_image_count=1,
        created_at_ms=1790845700000,
    ),
    XiaoShiLiuPostAsset(
        author_user_id=AUTHOR_ID,
        title="Large Tablets for Drawing",
        content="Lenovo tablet YOGA Pad Pro 14.5 is a 14.5-inch tablet with a roomy canvas for drawing and desk review sessions.",
        category="Technology",
        tags=["tablet", "drawing"],
        image_urls=["/assets/large-tablet-drawing.png"],
        min_image_count=1,
        created_at_ms=1790845200000,
    ),
    XiaoShiLiuPostAsset(
        author_user_id=SIDE_PRODUCT_AUTHOR_ID,
        title="Surface Go Lecture Desk Setup",
        content=(
            "Surface Go 4 for Business works well with a keyboard for desktop-style notes; "
            "I use it more like a tiny laptop than a handheld reading tablet."
        ),
        category="Technology",
        tags=["tablet", "windows", "study"],
        image_urls=["/assets/student-laptop.png"],
        min_image_count=1,
        created_at_ms=1790845000000,
    ),
    XiaoShiLiuPostAsset(
        author_user_id=SIDE_PRODUCT_AUTHOR_ID,
        title="E Reader Article Workflow",
        content="An e-reader is comfortable for long articles and quiet reading, though handwritten PDF markup feels limited in class.",
        category="Technology",
        tags=["ereader", "pdf"],
        image_urls=["/assets/compact-tablet-study.png"],
        min_image_count=1,
        created_at_ms=1790844850000,
    ),
    XiaoShiLiuPostAsset(
        author_user_id=SIDE_PRODUCT_AUTHOR_ID,
        title="Tablet Keyboard Accessory Notes",
        content="A Bluetooth keyboard can improve typing after someone already has a tablet, especially for summaries and longer class notes.",
        category="Technology",
        tags=["accessory", "keyboard"],
        image_urls=["/assets/student-laptop.png"],
        min_image_count=1,
        created_at_ms=1790844750000,
    ),
    XiaoShiLiuPostAsset(
        author_user_id=AUTHOR_ID,
        title="Student Laptop Recommendations",
        content="Lenovo Legion Y7000P 2025 is a laptop for heavy coursework, and the price climbs above what I would call a student tablet budget.",
        category="Technology",
        tags=["laptop", "study"],
        image_urls=["/assets/student-laptop.png"],
        min_image_count=1,
        created_at_ms=1790844600000,
    ),
    XiaoShiLiuPostAsset(
        author_user_id=AUTHOR_ID,
        title="Phone Note-Taking Setup",
        content="A phone note-taking setup can work in a pinch, but long PDF pages feel cramped on a phone screen.",
        category="Technology",
        tags=["phone", "notes"],
        image_urls=["/assets/phone-notes.png"],
        min_image_count=1,
        created_at_ms=1790844000000,
    ),
)
COMMENTS = (
    XiaoShiLiuCommentAsset(
        post_title=SIZE_POST_TITLE,
        post_author_user_id=AUTHOR_ID,
        author_user_id=PDF_COMMENTER_ID,
        content="I agree this compact model is still comfortable enough to carry for class notes.",
        created_at_ms=1790846150000,
    ),
    XiaoShiLiuCommentAsset(
        post_title=SIZE_POST_TITLE,
        post_author_user_id=AUTHOR_ID,
        author_user_id=SURFACE_COMMENTER_ID,
        content="Surface Go 4 is easy enough to carry, but with the keyboard I think of it more as a small desk setup than a one-hand tablet.",
        created_at_ms=1790846170000,
    ),
    XiaoShiLiuCommentAsset(
        post_title=EVIDENCE_POST_TITLE,
        post_author_user_id=AUTHOR_ID,
        author_user_id=COMMUTE_COMMENTER_ID,
        content="This was the compact option I saw people use for PDF margin notes without feeling like they were studying on a phone.",
        created_at_ms=1790846180000,
    ),
    XiaoShiLiuCommentAsset(
        post_title=WORKFLOW_POST_TITLE,
        post_author_user_id=AUTHOR_ID,
        author_user_id=YOGA_COMMENTER_ID,
        content="The YOGA Pad Pro is nice for drawing at a desk, but 14.5 inches felt too large for compact commute study.",
        created_at_ms=1790846200000,
    ),
    XiaoShiLiuCommentAsset(
        post_title="Large Tablets for Drawing",
        post_author_user_id=AUTHOR_ID,
        author_user_id=COMMUTE_COMMENTER_ID,
        content="Great canvas, but I would not carry a 14.5-inch tablet to every lecture just for PDF notes.",
        created_at_ms=1790846210000,
    ),
    XiaoShiLiuCommentAsset(
        post_title="Surface Go Lecture Desk Setup",
        post_author_user_id=SIDE_PRODUCT_AUTHOR_ID,
        author_user_id=SURFACE_COMMENTER_ID,
        content="I like Surface Go with a keyboard on a desk; I would reach for it when typing docs, less when reading PDFs between classes.",
        created_at_ms=1790846220000,
    ),
    XiaoShiLiuCommentAsset(
        post_title="Tablet Keyboard Accessory Notes",
        post_author_user_id=SIDE_PRODUCT_AUTHOR_ID,
        author_user_id=ACCESSORY_COMMENTER_ID,
        content="Keyboard cases are useful after choosing the screen size, especially if you type summaries after marking up PDFs.",
        created_at_ms=1790846230000,
    ),
    XiaoShiLiuCommentAsset(
        post_title="Phone Note-Taking Setup",
        post_author_user_id=AUTHOR_ID,
        author_user_id=ACCESSORY_COMMENTER_ID,
        content="Phone notes are fine for quick captures, but I get tired of zooming around full PDF pages.",
        created_at_ms=1790846240000,
    ),
    XiaoShiLiuCommentAsset(
        post_title=SIZE_POST_TITLE,
        post_author_user_id=AUTHOR_ID,
        author_user_id=COMMUTE_COMMENTER_ID,
        content="The Y700 and Y7000P names are easy to mix up; one is the little tablet line and the other is the laptop line.",
        created_at_ms=1790846250000,
    ),
    XiaoShiLiuCommentAsset(
        post_title=SIZE_POST_TITLE,
        post_author_user_id=AUTHOR_ID,
        author_user_id=ACCESSORY_COMMENTER_ID,
        content="For a backpack tablet, the 8.8-inch entry is the one that still fits the compact range.",
        created_at_ms=1790846260000,
    ),
    XiaoShiLiuCommentAsset(
        post_title=EVIDENCE_POST_TITLE,
        post_author_user_id=AUTHOR_ID,
        author_user_id=PDF_COMMENTER_ID,
        content="I used this kind of compact tablet for marked-up slides and it was much easier than doing the same work on a phone.",
        created_at_ms=1790846270000,
    ),
    XiaoShiLiuCommentAsset(
        post_title=EVIDENCE_POST_TITLE,
        post_author_user_id=AUTHOR_ID,
        author_user_id=SURFACE_COMMENTER_ID,
        content="For pure desktop typing I would still use a Windows device, but this is the note I would trust for PDF markup on a small tablet.",
        created_at_ms=1790846280000,
    ),
    XiaoShiLiuCommentAsset(
        post_title=WORKFLOW_POST_TITLE,
        post_author_user_id=AUTHOR_ID,
        author_user_id=PDF_COMMENTER_ID,
        content="The key split is carrying and reading versus drawing at a desk; commute study feels much better with something smaller.",
        created_at_ms=1790846290000,
    ),
    XiaoShiLiuCommentAsset(
        post_title="Large Tablets for Drawing",
        post_author_user_id=AUTHOR_ID,
        author_user_id=YOGA_COMMENTER_ID,
        content="This is the one I would choose for drawing practice at home, especially if it mostly stays on the desk.",
        created_at_ms=1790846300000,
    ),
    XiaoShiLiuCommentAsset(
        post_title="Surface Go Lecture Desk Setup",
        post_author_user_id=SIDE_PRODUCT_AUTHOR_ID,
        author_user_id=PDF_COMMENTER_ID,
        content="Useful with the keyboard on a desk, but it feels like a different study setup from a compact Android tablet.",
        created_at_ms=1790846310000,
    ),
    XiaoShiLiuCommentAsset(
        post_title="E Reader Article Workflow",
        post_author_user_id=SIDE_PRODUCT_AUTHOR_ID,
        author_user_id=COMMUTE_COMMENTER_ID,
        content="Great for reading articles, but handwritten PDF notes are not the main strength here.",
        created_at_ms=1790846320000,
    ),
    XiaoShiLiuCommentAsset(
        post_title="Tablet Keyboard Accessory Notes",
        post_author_user_id=SIDE_PRODUCT_AUTHOR_ID,
        author_user_id=SURFACE_COMMENTER_ID,
        content="This belongs on the accessory list after the screen choice is settled; it is mainly a typing add-on.",
        created_at_ms=1790846330000,
    ),
    XiaoShiLiuCommentAsset(
        post_title="Student Laptop Recommendations",
        post_author_user_id=AUTHOR_ID,
        author_user_id=ACCESSORY_COMMENTER_ID,
        content="Good performance laptop for coding or CAD, though handwritten notes are not the reason I would buy it.",
        created_at_ms=1790846340000,
    ),
    XiaoShiLiuCommentAsset(
        post_title="Phone Note-Taking Setup",
        post_author_user_id=AUTHOR_ID,
        author_user_id=PDF_COMMENTER_ID,
        content="Phones are fine for quick reminders, but long PDF pages and class handouts get cramped fast.",
        created_at_ms=1790846350000,
    ),
)


class TabletPurchaseXiaoShiLiuResearchTask(BaseTask):
    apps = {"Mail", "XiaoShiLiu", "Mall", "Contacts", "Messages"}
    difficulty = "realistic"
    category = ['Information-Gathering Tasks', 'Selection / Optimization Tasks', 'Multi-Step Workflow Tasks']
    snapshot = "gma_ready_state"
    max_steps = 190

    mail_account = MailAccountAsset(display_name="Taylor Nguyen", email="taylor.nguyen@example.com")
    request_mail = MailMessageAsset(
        mailbox="inbox",
        from_name="Younger Sister",
        from_email="younger.sister@example.com",
        to=[mail_account.email],
        subject="Please buy a study tablet",
        body=(
            "Please buy a tablet for paperless studying, note-taking, and reading PDFs. Do not buy a phone or laptop. "
            "I prefer a compact tablet around 8 to 9 inches and the budget is under 5200. "
            "I saw compact study tablet comparisons on XiaoShiLiu, so please check the posts and comments there before buying. "
            "Pay with Alipay at checkout. After buying it, update my contact note with what you chose and why, and text me. "
            "Use contact note format: Selected: <product>. Reason: <copied supporting post content>. "
            "Use SMS format: Bought <product>. Reason: <copied supporting post content>. "
            "Copy the supporting post content exactly as written, preserving capitalization, spacing, and punctuation."
        ),
        timestamp_ms=1790846400000,
        read=False,
    )
    research_author = XiaoShiLiuUserAsset(
        user_id=AUTHOR_ID,
        nickname="Compact Study Desk",
        email="compact.study.desk@example.com",
        avatar=XIAOSHILIU_DEFAULT_AVATAR,
        bio="Tablet and paperless study notes.",
    )
    side_product_author = XiaoShiLiuUserAsset(
        user_id=SIDE_PRODUCT_AUTHOR_ID,
        nickname="Adjacent Gear Desk",
        email="adjacent.gear.desk@example.com",
        avatar=XIAOSHILIU_DEFAULT_AVATAR,
        bio="Study accessories and adjacent devices.",
    )
    pdf_commenter = XiaoShiLiuUserAsset(
        user_id=PDF_COMMENTER_ID,
        nickname="PDF Annotation Student",
        email="pdf.annotation.student@example.com",
        avatar=XIAOSHILIU_DEFAULT_AVATAR,
        bio="Paperless study workflow notes.",
    )
    yoga_commenter = XiaoShiLiuUserAsset(
        user_id=YOGA_COMMENTER_ID,
        nickname="Commute Study Notes",
        email="commute.study.notes@example.com",
        avatar=XIAOSHILIU_DEFAULT_AVATAR,
        bio="Compact school commute setups.",
    )
    commute_commenter = XiaoShiLiuUserAsset(
        user_id=COMMUTE_COMMENTER_ID,
        nickname="Lecture Bag Tester",
        email="lecture.bag.tester@example.com",
        avatar=XIAOSHILIU_DEFAULT_AVATAR,
        bio="Everyday carry and classroom notes.",
    )
    surface_commenter = XiaoShiLiuUserAsset(
        user_id=SURFACE_COMMENTER_ID,
        nickname="Windows Tablet Notes",
        email="windows.tablet.notes@example.com",
        avatar=XIAOSHILIU_DEFAULT_AVATAR,
        bio="Surface and keyboard study setups.",
    )
    accessory_commenter = XiaoShiLiuUserAsset(
        user_id=ACCESSORY_COMMENTER_ID,
        nickname="Accessory Shelf",
        email="accessory.shelf@example.com",
        avatar=XIAOSHILIU_DEFAULT_AVATAR,
        bio="Study accessories and note-taking add-ons.",
    )
    mall_user = MallMemberAsset(
        username=MALL_LOGIN_USERNAME,
        password="123456",
        nickname=MALL_LOGIN_NICKNAME,
        phone=MALL_LOGIN_PHONE,
        city=MALL_LOGIN_CITY,
        status=1,
    )
    default_address = MallAddressAsset(
        member_username=MALL_LOGIN_USERNAME,
        name="Taylor Nguyen",
        phone_number="5550101126",
        province="New York State",
        city="New York City",
        region="Queens Borough",
        detail_address="18 Queens Plaza Apt 7",
        post_code="100080",
        default_status=True,
    )
    campus_address = MallAddressAsset(
        member_username=MALL_LOGIN_USERNAME,
        name="Taylor Campus Mailroom",
        phone_number="5550101127",
        province="New York State",
        city="New York City",
        region="Manhattan Borough",
        detail_address="North Campus Mailroom 12",
        post_code="100081",
        default_status=False,
    )
    assets = (
        mail_account,
        request_mail,
        research_author,
        side_product_author,
        pdf_commenter,
        yoga_commenter,
        commute_commenter,
        surface_commenter,
        accessory_commenter,
        *POSTS,
        *COMMENTS,
        mall_user,
        default_address,
        campus_address,
        CONTACT_BEFORE,
    )

    goal = (
        "Open Mail and read the purchase request from Younger Sister. Research XiaoShiLiu posts and comments to find which existing Mall tablet satisfies "
        "the requested compact size, budget, and paperless-study needs. Then buy the matching product in Mall and pay with Alipay. "
        "Update Younger Sister's contact note using the format `Selected: <product>. Reason: <copied supporting post content>.` and send her an SMS using the format "
        "`Bought <product>. Reason: <copied supporting post content>.` For the reason, copy the full content of the XiaoShiLiu post that most strongly supports the selected product "
        "exactly as written, preserving capitalization, spacing, and punctuation."
    )

    user_interaction = (
        "If the agent asks which Mall shipping address to use for the study tablet, answer exactly: "
        "Use Taylor Nguyen at 18 Queens Plaza Apt 7."
    )

    def criteria(self):
        return [
            MallCheckoutOrderCreated(
                member_username=MALL_LOGIN_USERNAME,
                product_sn=PRODUCT_SN,
                quantity=1,
                expected_status=1,
                receiver_name="Taylor Nguyen",
            ),
            AssetExists(CONTACT_AFTER, task=self),
            AssetExists(SmsMessageAsset(address=CONTACT_BEFORE.phone_number, body=SMS_TEXT, box="sent", read=True), task=self),
        ]
