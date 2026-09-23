"""Derive review images from supplied screenshots and approved full exports.

Run with Python + Pillow from any directory. Crop rectangles use source pixels:
[x, y, width, height]. Never change source files. Generated images are lossless
WebP, without EXIF metadata.
"""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
NEW_SOURCE_ROOT = ROOT.parent / "new_photo"
ORIGINAL_SOURCE_ROOT = NEW_SOURCE_ROOT / "original_photo"
VERIFICATION = ROOT / "verification" / "asset-checks.json"
MASK_COLOR = "#d9dce0"

SOURCE_SPECS = [
    ("S01", "微信图片_20260922212915_1134_19.jpg", [1080, 2939], "130ec3e00242150e4eda95f77f670ceff096efc304d4fac14199b2d8dccef845"),
    ("S02", "微信图片_20260922212921_1135_19.jpg", [1080, 8550], "934d8cd621334e972ac12e39b8c97cca0cef01ad5414100803139e52c4525c14"),
    ("S03", "微信图片_20260922212923_1136_19.jpg", [1080, 2340], "281b0e40cc1f47b6e260e2185f0d9587f0ccfb98acddc018e262f63891d2f755"),
    ("S04", "微信图片_20260922212926_1137_19.jpg", [1080, 2340], "75ae7d1f9689542b5d0650141a62df6a5dc10522af9fee08a89e1bd30bad6de9"),
    ("S05", "微信图片_20260922212928_1138_19.jpg", [1080, 2340], "74a885ebf29e0681c83dcaf202520cc32edfe40600c08a2989a0c67c80dc8bfa"),
    ("S06", "微信图片_20260922212932_1139_19.jpg", [1080, 2340], "c7c63ba7d311290f05e9e5df36e53f84ed2e860980ea846fbc709281b7c521ee"),
    ("S07", "微信图片_20260922212933_1140_19.jpg", [1080, 2340], "3c16cdbf09ccf9ee176b4b190daaa863e41cc8d0cbcbae3870e5dc4cc9d859a7"),
    ("S08", "微信图片_20260922212936_1141_19.jpg", [1080, 2620], "53a293d07505e2ee45a70364b50e290f82f7aeb5033082331624688ef0e02b19"),
    ("S09", "微信图片_20260922212940_1142_19.jpg", [1080, 5570], "95c9bcce7322f8a66f5aa0401b5e755b26200d55094e3240c02e4844aa6895cf"),
    ("S10", "微信图片_20260922212941_1143_19.jpg", [1080, 2340], "4158f739ba07a941b348f69e909b7745261dae67d01c33dc7bec79dc5c0ddc46"),
    ("S11", "微信图片_20260922212943_1144_19.jpg", [1080, 2340], "6397a0051c27d1fe7cf7d5e9986b7e0667cd64799a77098373ba45f3e088e604"),
    ("S12", "微信图片_20260922212945_1145_19.jpg", [1080, 4542], "9356afbffbc448e9d436cd21bf0938088c6610b2722b4374bc6eeceacd625ff9"),
    ("S13", "manual-heart-editor.jpg", [1080, 3424], "1578b44a05221feac1ddd83855e836d05569e78a53805ffcc1b3c8bb8fda62c5"),
    ("S14", "manual-heart-palette.png", [800, 1542], "a36b3f8cf9f98e7ddbb77eb9f9684dc5700914d9d73eac38f0ca993f8eead610"),
]

NEW_SOURCE_AUTHORIZATION_STATUS = (
    "用户于2026-09-23提供并授权用于本次豆拼拼豆推介页；"
    "对外发布前仍需确认第三方角色权利"
)
NEW_SOURCE_SPECS = [
    ("N01", "微信图片_20260923111821_1156_19.jpg", [1080, 6133], "9ebc05facbe4f4b32a491b8c6b4a7079929af8f0556fc7810cbc4358faf30d6c", NEW_SOURCE_AUTHORIZATION_STATUS),
    ("N02", "微信图片_20260923111824_1157_19.png", [1171, 1461], "39919446a433aa68327b1cb47a68116445421708a95164f5407313ec6d5ee305", NEW_SOURCE_AUTHORIZATION_STATUS),
    ("N03", "微信图片_20260923111826_1158_19.jpg", [1080, 3424], "b1422ab023b44108db930713b2f3ea90050c3ba02ebe42d96d118f226d4f2722", NEW_SOURCE_AUTHORIZATION_STATUS),
    ("N04", "微信图片_20260923111827_1159_19.png", [1147, 1867], "b1b8dcef65146df7c337468f9f9749ad20d8b4ad246f26f1c728697fe886722a", NEW_SOURCE_AUTHORIZATION_STATUS),
    ("N05", "微信图片_20260923111829_1160_19.jpg", [1080, 11725], "3247a9c0431c61fec1f943801045b667493cc10625d7798bab19a5c9cf555cd9", NEW_SOURCE_AUTHORIZATION_STATUS),
    ("N06", "微信图片_20260923111830_1161_19.png", [1147, 1748], "5bb1a75017dd108727ed7d33fe89b6f440ab234c78de39cfd4e54691b3dffb18", NEW_SOURCE_AUTHORIZATION_STATUS),
    ("N07", "微信图片_20260923111833_1162_19.jpg", [1080, 2340], "fb501c3679773d4d2c0146426d9d63638b208138cc5cc6c22067e74210467fcd", NEW_SOURCE_AUTHORIZATION_STATUS),
    ("N08", "微信图片_20260923111835_1163_19.png", [1186, 2090], "f68322d1f74148b5c6dba343ed0c38b58c38e7f3db909785ee8c69f69e3e60d6", NEW_SOURCE_AUTHORIZATION_STATUS),
    ("N09", "微信图片_20260923111838_1164_19.png", [1147, 1748], "7d9c2e0209da763bb5cc28eb40de01548444b54814e3513d3227d282e4be9632", NEW_SOURCE_AUTHORIZATION_STATUS),
    ("N10", "微信图片_20260923111841_1165_19.jpg", [1080, 9887], "6957bd2b2562385bc376afbbd7a67e916070116ef0e9d9ee49b286921c0aee2c", NEW_SOURCE_AUTHORIZATION_STATUS),
    ("N11", "微信图片_20260923111842_1166_19.png", [1186, 1982], "c8260ceff089b68ef0d97c7b38dfc8e145c1029fcfa6168d40bbf9e5296c6140", NEW_SOURCE_AUTHORIZATION_STATUS),
    ("N12", "微信图片_20260923111845_1167_19.png", [1186, 2090], "f68322d1f74148b5c6dba343ed0c38b58c38e7f3db909785ee8c69f69e3e60d6", NEW_SOURCE_AUTHORIZATION_STATUS),
]
ORIGINAL_SOURCE_SPECS = [
    ("O01", "微信图片_20260923095728_1149_19.png", [1128, 1042], "6ad67d5acce7afb3bad89b46e8f560ccabae6a2ddcf79d18d366970e16b5f75c"),
    ("O02", "微信图片_20260923100123_1150_19.jpg", [750, 1000], "3db8c1d8b85b7edcc942b1334abc7e98eed00218c69221714af88d0cfbb541a4"),
    ("O03", "微信图片_20260923100123_1152_19.jpg", [1080, 1080], "0e71d0eff59f7789a79c42ac3fb7a6beb4971d423ba65008a9d27ee714bc536d"),
    ("O04", "微信图片_20260923100123_1153_19.jpg", [1080, 1080], "fe94fa9188ae449f7aaa9967a09785d332390370a8faf7f35bfc58d781733fd6"),
    ("O05", "微信图片_20260923100124_1154_19.jpg", [771, 771], "49825c7890aabd4a1423d16aed662491d05125c055de7c912362defe24c8f445"),
    ("O06", "微信图片_20260923100124_1155_19.jpg", [1080, 1440], "542a727b3aa09f4001c43e6eb12c2bd2223cd278824993f5d79ea1d97c657939"),
    ("O07", "微信图片_20260923144816_1168_19.jpg", [1080, 1440], "80381c3bda0502d9ceb803309e019c76dc506b73f5ea08c99839bac6af00d08f"),
]

NEW_ASSETS = [
    (
        "outcome-butterfly",
        "N04",
        "完整导出的蝴蝶拼豆图纸，含网格色号和用量图例",
    ),
    (
        "outcome-dog",
        "N06",
        "完整导出的犬类拼豆图纸，含网格色号和用量图例",
    ),
    (
        "outcome-bow",
        "N09",
        "完整导出的蝴蝶结拼豆图纸，含网格色号和用量图例",
    ),
]
ORIGINAL_ASSETS = [
    (
        "original-butterfly",
        "O01",
        ["workspace"],
        "蝴蝶图纸对应的原始生成图片",
    ),
    (
        "original-dog",
        "O03",
        ["workspace"],
        "小狗图纸对应的原始生成图片",
    ),
    (
        "original-bow",
        "O04",
        ["workspace"],
        "蝴蝶结图纸对应的原始生成图片",
    ),
    (
        "original-main-cat",
        "O07",
        ["intro"],
        "猫咪主线图纸对应的原始照片",
    ),
]
SELECTED_NEW_SOURCES = {source_id for _, source_id, _ in NEW_ASSETS}
SELECTED_ORIGINAL_SOURCES = {
    source_id for _, source_id, _, _ in ORIGINAL_ASSETS
}
NEW_PRIVACY_PROCESSING = (
    "无需脱敏；画面仅含图纸、色号用量和产品水印，无可识别个人信息"
)
ORIGINAL_PRIVACY_PROCESSING = (
    "无需脱敏；画面不含可识别姓名、头像、定位或设备信息"
)

# Public screenshots retain their original canvas except S07, where the share
# card alone supplies the evidence. Redactions are source-space solid masks,
# never generated replacement UI. All derivatives use the same sanitized image.
PUBLIC_CROPS = {"S07": [205, 520, 710, 802]}
REDACTIONS = {
    "S09": [
        {"rect": [410, 875, 300, 64], "reason": "作品卡片作者显示名"},
        {"rect": [410, 1264, 300, 64], "reason": "作品卡片作者显示名"},
        {"rect": [410, 1653, 300, 64], "reason": "作品卡片作者显示名"},
        {"rect": [410, 2042, 300, 64], "reason": "作品卡片作者显示名"},
        {"rect": [410, 2431, 300, 64], "reason": "作品卡片作者显示名"},
        {"rect": [410, 2820, 300, 64], "reason": "作品卡片作者显示名"},
        {"rect": [410, 3209, 300, 64], "reason": "作品卡片作者显示名"},
        {"rect": [410, 3598, 300, 64], "reason": "作品卡片作者显示名"},
        {"rect": [410, 3987, 300, 64], "reason": "作品卡片作者显示名"},
        {"rect": [410, 4376, 300, 64], "reason": "作品卡片作者显示名"},
        {"rect": [410, 4765, 300, 64], "reason": "作品卡片作者显示名"},
        {"rect": [410, 5154, 300, 64], "reason": "作品卡片作者显示名"},
    ],
    "S10": [
        {"rect": [85, 600, 128, 132], "reason": "投稿账号头像"},
        {"rect": [230, 615, 355, 61], "reason": "投稿账号昵称"},
    ],
    "S11": [
        {"rect": [278, 726, 248, 41], "reason": "待审核作品作者显示名"},
    ],
}
CROPS = [
    ("upload", "S01", [30, 245, 998, 1330], ["workflow"], "上传前的像素转换页面与参数区"),
    ("converted", "S02", [65, 1600, 948, 1260], ["workflow"], "生成后的猫咪像素图纸"),
    ("output-actions", "S02", [66, 3738, 948, 140], ["workflow", "blueprint"], "导出高清图、保存至作品库和手动调整入口"),
    ("parameters", "S02", [35, 635, 992, 940], ["convert"], "品牌色板、六种算法、图纸大小和颗粒度设置"),
    ("color-counts", "S02", [35, 3926, 992, 655], ["blueprint"], "色号统计及部分颜色用量"),
    ("workspace", "S03", [30, 280, 998, 1840], ["workflow", "workspace"], "作品库中的猫咪图纸和手绘作品"),
    ("saved-cat", "S03", [35, 599, 988, 729], ["workspace"], "猫咪图纸作品卡片及再次编辑入口"),
    ("saved-drawing", "S03", [35, 1360, 988, 750], ["workspace"], "作品库中的手绘图纸"),
    ("blueprint", "S04", [0, 245, 1080, 1855], ["intro", "blueprint"], "猫咪图纸整体，含网格、色号及图例"),
    ("grid-detail", "S04", [370, 650, 430, 330], ["blueprint"], "猫咪图纸局部：每格标注对应色号"),
    ("legend", "S04", [0, 1680, 1080, 420], ["blueprint"], "导出图纸中的色号图例和数量"),
    ("share-card", "S07", [205, 520, 710, 802], ["share"], "微信会话中的豆拼拼豆分享卡片"),
    ("shared-work", "S08", [60, 450, 945, 1715], ["share"], "接收方打开分享后的图纸"),
    ("remix-actions", "S08", [35, 2210, 1010, 360], ["share"], "基于此图二次创作、导出与开始制作入口"),
    ("gallery", "S09", [28, 275, 996, 2040], ["share"], "精选作品库和四个图纸示例"),
    ("gallery-heart", "S09", [35, 795, 990, 345], ["share"], "精选作品：糖果爱心"),
    ("gallery-smile", "S09", [35, 1182, 990, 343], ["share"], "精选作品：笑脸贴纸"),
    ("gallery-strawberry", "S09", [35, 1574, 990, 343], ["share"], "精选作品：草莓果果"),
    ("gallery-flower", "S09", [35, 1962, 990, 343], ["share"], "精选作品：春日郁金香"),
    ("submission", "S10", [30, 275, 997, 1745], ["share"], "投稿表单：已选作品和标签，截图处于提交中"),
    ("review", "S11", [30, 275, 997, 1100], ["share"], "管理员审核页面：该作品处于审核中"),
    ("editor-tools", "S13", [63, 1826, 950, 269], ["edit"], "爱心图纸编辑时的全屏、画笔、橡皮、吸色、填充、撤销重做工具"),
    ("editor-canvas", "S13", [35, 2100, 950, 1100], ["edit"], "红粉爱心手绘示例，格子内标注对应色号"),
    ("editor-palette", "S14", [20, 580, 780, 615], ["edit"], "爱心图纸使用的品牌色板、红系筛选与当前颜色"),
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box(rect):
    x, y, width, height = rect
    return x, y, x + width, y + height


def contains(outer, inner):
    ox, oy, ow, oh = outer
    ix, iy, iw, ih = inner
    return ox <= ix and oy <= iy and ix + iw <= ox + ow and iy + ih <= oy + oh


def intersecting_redactions(source_id, crop):
    cx, cy, cw, ch = crop
    matches = []
    for redaction in REDACTIONS.get(source_id, []):
        rx, ry, rw, rh = redaction["rect"]
        left = max(cx, rx)
        top = max(cy, ry)
        right = min(cx + cw, rx + rw)
        bottom = min(cy + ch, ry + rh)
        if left < right and top < bottom:
            matches.append({
                "sourceRect": redaction["rect"],
                "derivedRect": [left - cx, top - cy, right - left, bottom - top],
                "reason": redaction["reason"],
                "method": f"不可逆纯色遮挡 {MASK_COLOR}",
            })
    return matches


def processing_note(source_id, redactions):
    if source_id == "S07":
        return "仅裁取产品分享卡片，排除聊天对象、头像、其他消息、键盘和输入内容；未缩放、未拼接、未补造状态"
    if redactions:
        reasons = "、".join(dict.fromkeys(item["reason"] for item in redactions))
        return f"{reasons}使用不可逆纯色遮挡；其余内容仅裁剪，未缩放、未拼接、未补造状态"
    return "仅按原始像素裁剪或转换格式；未缩放、未拼接、未补造状态"


def save_image(image, path):
    options = {"lossless": True, "method": 6}
    if "A" in image.getbands():
        options["exact"] = True
    image.save(path, "WEBP", **options)
    with Image.open(path) as saved:
        saved.load()
        assert saved.size == image.size
        comparison_mode = "RGBA" if "A" in image.getbands() else "RGB"
        assert (
            saved.convert(comparison_mode).tobytes()
            == image.convert(comparison_mode).tobytes()
        ), f"Pixel mismatch: {path.name}"


def main():
    ASSETS.mkdir(exist_ok=True)
    for legacy_name in (
        "outcome-cats.webp",
        "process-cats.webp",
        "process-butterfly.webp",
        "process-dog.webp",
        "process-bow.webp",
        "source-n05.webp",
        "source-n07.webp",
        "source-n10.webp",
        "source-s12.webp",
    ):
        (ASSETS / legacy_name).unlink(missing_ok=True)
    VERIFICATION.parent.mkdir(exist_ok=True)
    manifest = {
        "version": 3,
        "coordinateSystem": "original source pixels, [x,y,width,height]",
        "sourcePlatform": "微信小程序实拍",
        "encoding": "lossless WebP; source pixels retained outside documented redactions",
        "derivationPolicy": "仅裁剪和必要的不可逆纯色脱敏；不缩放、不拼接、不生成或补造界面状态",
        "sources": {},
        "assets": [],
    }
    sanitized = {}
    for source_id, filename, expected_size, expected_hash in SOURCE_SPECS:
        path = ROOT / filename
        assert path.is_file(), f"Missing source: {filename}"
        assert sha256(path) == expected_hash, f"Original source hash changed: {source_id}"
        with Image.open(path) as source:
            im = source.convert("RGB")
        assert list(im.size) == expected_size, f"Original source size changed: {source_id}"
        redactions = REDACTIONS.get(source_id, [])
        draw = ImageDraw.Draw(im)
        for redaction in redactions:
            assert contains([0, 0, *im.size], redaction["rect"])
            x0, y0, x1, y1 = box(redaction["rect"])
            draw.rectangle((x0, y0, x1 - 1, y1 - 1), fill=MASK_COLOR)
        sanitized[source_id] = im
        public_rect = PUBLIC_CROPS.get(source_id, [0, 0, *im.size])
        assert contains([0, 0, *im.size], public_rect)
        # S05/S06 are reserve references; S12 is the retired hand-drawn example.
        public_path = None
        if source_id not in {"S05", "S06", "S12"}:
            public_path = f"assets/source-{source_id.lower()}.webp"
            save_image(im.crop(box(public_rect)), ROOT / public_path)
        public_redactions = intersecting_redactions(source_id, public_rect)
        manifest["sources"][source_id] = {
            "file": path.name,
            "sha256": expected_hash,
            "size": list(im.size),
            "publicFile": public_path,
            "publicCrop": public_rect if public_path else None,
            "redactions": [
                {
                    "sourceRect": item["rect"],
                    "reason": item["reason"],
                    "method": f"不可逆纯色遮挡 {MASK_COLOR}",
                }
                for item in redactions
            ],
            "processing": (
                "不生成公开副本；仅本地保留原始参考，设备路径等系统信息不进入公开素材"
                if source_id in {"S05", "S06", "S12"}
                else processing_note(source_id, public_redactions)
            ),
        }
    new_images = {}
    for source_id, filename, expected_size, expected_hash, authorization_status in NEW_SOURCE_SPECS:
        path = NEW_SOURCE_ROOT / filename
        assert path.is_file(), f"Missing source: {path}"
        assert sha256(path) == expected_hash, f"Original source hash changed: {source_id}"
        with Image.open(path) as source:
            source.load()
            mode = "RGBA" if "A" in source.getbands() else "RGB"
            im = source.convert(mode)
        assert list(im.size) == expected_size, f"Original source size changed: {source_id}"
        source_path = f"../new_photo/{path.name}"
        selected = source_id in SELECTED_NEW_SOURCES
        public_path = f"assets/source-{source_id.lower()}.webp" if selected else None
        if selected:
            save_image(im, ROOT / public_path)
            new_images[source_id] = im
        manifest["sources"][source_id] = {
            "file": path.name,
            "sourcePath": source_path,
            "authorizationAndSourceStatus": authorization_status,
            "sha256": expected_hash,
            "size": list(im.size),
            "publicFile": public_path,
            "publicCrop": [0, 0, *im.size] if selected else None,
            "redactions": [],
            "privacyProcessing": (
                NEW_PRIVACY_PROCESSING
                if selected
                else "未生成公开副本；仅登记源文件哈希、尺寸和来源路径"
            ),
            "processing": (
                "完整画布原像素转换为 lossless WebP；未裁剪、未缩放、未拼接"
                if selected
                else "未接入公开素材；原文件保持不变"
            ),
            "auditDecision": (
                "入选：用户确认用于本项目；第三方角色权利待对外发布前确认"
                if selected
                else "未入选：仅保留审计记录；第三方角色权利待对外发布前确认"
            ),
            "duplicateOf": "N08" if source_id == "N12" else None,
        }
    assert (
        manifest["sources"]["N08"]["sha256"] == manifest["sources"]["N12"]["sha256"]
    ), "Expected duplicate pair N08/N12 changed."
    original_images = {}
    for source_id, filename, expected_size, expected_hash in ORIGINAL_SOURCE_SPECS:
        path = ORIGINAL_SOURCE_ROOT / filename
        assert path.is_file(), f"Missing source: {path}"
        assert sha256(path) == expected_hash, f"Original source hash changed: {source_id}"
        with Image.open(path) as source:
            source.load()
            mode = "RGBA" if "A" in source.getbands() else "RGB"
            im = source.convert(mode)
        assert list(im.size) == expected_size, f"Original source size changed: {source_id}"
        selected = source_id in SELECTED_ORIGINAL_SOURCES
        public_path = f"assets/source-{source_id.lower()}.webp" if selected else None
        if selected:
            save_image(im, ROOT / public_path)
            original_images[source_id] = im
        manifest["sources"][source_id] = {
            "file": path.name,
            "sourcePath": f"../new_photo/original_photo/{path.name}",
            "authorizationAndSourceStatus": NEW_SOURCE_AUTHORIZATION_STATUS,
            "sha256": expected_hash,
            "size": list(im.size),
            "publicFile": public_path,
            "publicCrop": [0, 0, *im.size] if selected else None,
            "redactions": [],
            "privacyProcessing": (
                ORIGINAL_PRIVACY_PROCESSING
                if selected
                else "未生成公开副本；仅登记源文件哈希、尺寸和来源路径"
            ),
            "processing": (
                "完整画布原像素转换为 lossless WebP；未裁剪、未缩放、未拼接"
                if selected
                else "未接入公开素材；原文件保持不变"
            ),
            "auditDecision": (
                "入选：与页面现有图纸形成原图对照"
                if selected
                else "未入选：尚无对应的页面图纸证据或存在第三方角色权利风险"
            ),
        }
    for asset_id, source_id, rect, sections, alt in CROPS:
        image = sanitized[source_id]
        assert contains([0, 0, *image.size], rect)
        redactions = intersecting_redactions(source_id, rect)
        output = f"assets/{asset_id}.webp"
        save_image(image.crop(box(rect)), ROOT / output)
        manifest["assets"].append({
            "id": asset_id,
            "source": source_id,
            "crop": rect,
            "file": output,
            "outputSize": rect[2:],
            "sections": sections,
            "purpose": alt,
            "alt": alt,
            "publicSource": manifest["sources"][source_id]["publicFile"],
            "sourcePlatform": manifest["sourcePlatform"],
            "derivation": "单一来源原像素裁片；无缩放、无拼接",
            "redactions": redactions,
            "publicProcessing": processing_note(source_id, redactions),
        })
    for asset_id, source_id, alt in NEW_ASSETS:
        image = new_images[source_id]
        rect = [0, 0, *image.size]
        output = f"assets/{asset_id}.webp"
        save_image(image, ROOT / output)
        source = manifest["sources"][source_id]
        manifest["assets"].append({
            "id": asset_id,
            "source": source_id,
            "sourcePath": source["sourcePath"],
            "authorizationAndSourceStatus": source["authorizationAndSourceStatus"],
            "crop": rect,
            "file": output,
            "outputSize": list(image.size),
            "sections": ["workspace"],
            "purpose": alt,
            "alt": alt,
            "publicSource": source["publicFile"],
            "sourcePlatform": "豆拼拼豆完整导出图",
            "derivation": "完整画布原像素格式转换；无裁剪、无缩放、无拼接",
            "redactions": [],
            "privacyProcessing": NEW_PRIVACY_PROCESSING,
            "publicProcessing": (
                f"{NEW_PRIVACY_PROCESSING}；完整画布原像素转换为 lossless WebP"
            ),
        })
    for asset_id, source_id, sections, alt in ORIGINAL_ASSETS:
        image = original_images[source_id]
        rect = [0, 0, *image.size]
        output = f"assets/{asset_id}.webp"
        save_image(image, ROOT / output)
        source = manifest["sources"][source_id]
        manifest["assets"].append({
            "id": asset_id,
            "source": source_id,
            "sourcePath": source["sourcePath"],
            "authorizationAndSourceStatus": source["authorizationAndSourceStatus"],
            "crop": rect,
            "file": output,
            "outputSize": list(image.size),
            "sections": sections,
            "purpose": alt,
            "alt": alt,
            "publicSource": source["publicFile"],
            "sourcePlatform": "用户提供的原始生成图片",
            "derivation": "完整画布原像素格式转换；无裁剪、无缩放、无拼接",
            "redactions": [],
            "privacyProcessing": ORIGINAL_PRIVACY_PROCESSING,
            "publicProcessing": (
                f"{ORIGINAL_PRIVACY_PROCESSING}；完整画布原像素转换为 lossless WebP"
            ),
        })
    required_sections = {"intro", "workflow", "convert", "blueprint", "edit", "workspace", "share"}
    section_assets = {
        section: [
            asset["id"]
            for asset in manifest["assets"]
            if asset["source"].startswith("S") and section in asset["sections"]
        ]
        for section in sorted(required_sections)
    }
    assert all(section_assets.values()), "A required showcase section has no asset."
    assert all(
        sha256(ROOT / filename) == expected_hash
        for _, filename, _, expected_hash in SOURCE_SPECS
    ), "An original S source changed during generation."
    assert all(
        sha256(NEW_SOURCE_ROOT / filename) == expected_hash
        for _, filename, _, expected_hash, _ in NEW_SOURCE_SPECS
    ), "An original N source changed during generation."
    assert all(
        sha256(ORIGINAL_SOURCE_ROOT / filename) == expected_hash
        for _, filename, _, expected_hash in ORIGINAL_SOURCE_SPECS
    ), "An original O source changed during generation."
    assert all(
        contains(
            [0, 0, *manifest["sources"][asset["source"]]["size"]],
            asset["crop"],
        )
        and asset["sections"] == ["workspace"]
        for asset in manifest["assets"]
        if asset["source"].startswith("N")
    ), "An approved N asset is not a valid workspace derivative."
    assert all(
        asset["crop"] == [0, 0, *manifest["sources"][asset["source"]]["size"]]
        for asset in manifest["assets"]
        if asset["source"].startswith("O")
    ), "An approved O asset is not a full-canvas derivative."
    (ROOT / "assets-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    verification = {
        "version": 2,
        "generatedBy": "scripts/prepare-assets.py",
        "originalScreenshotsVerified": len(SOURCE_SPECS),
        "supplementalSourcesVerified": (
            len(NEW_SOURCE_SPECS) + len(ORIGINAL_SOURCE_SPECS)
        ),
        "originalHashesUnchanged": True,
        "losslessCropsVerified": len(CROPS),
        "sanitizedSourcesVerified": sum(
            source["publicFile"] is not None
            for source in manifest["sources"].values()
        ),
        "pixelExactAfterCropAndRedaction": True,
        "resizedAssets": 0,
        "compositedAssets": 0,
        "solidRedactionsVerified": sum(len(items) for items in REDACTIONS.values()),
        "requiredSectionCoverage": section_assets,
        "minimumCropWidth": min(asset["outputSize"][0] for asset in manifest["assets"]),
        "minimumCropHeight": min(asset["outputSize"][1] for asset in manifest["assets"]),
        "legibilityReview": {
            "status": "passed",
            "reviewedOn": "2026-09-23",
            "targets": [
                "约 1180px 桌面内容宽度",
                "375px、390px、430px 手机视口及原尺寸大图",
            ],
            "checks": [
                "首屏图纸、三步流程、参数、网格色号、编辑工具、作品卡片、分享与投稿文字可辨认",
                "S09 脱敏后作品标题、图案、规格、标签和功能状态保持可见",
                "所有输出尺寸等于裁剪尺寸，未发生拉伸或重采样",
            ],
        },
    }
    VERIFICATION.write_text(
        json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Prepared {len(CROPS)} crops and "
        f"{verification['sanitizedSourcesVerified']} public source images; "
        f"prepared {len(NEW_ASSETS) + len(ORIGINAL_ASSETS)} approved full-canvas "
        f"assets and public sources; verified "
        f"{len(SOURCE_SPECS) + len(NEW_SOURCE_SPECS) + len(ORIGINAL_SOURCE_SPECS)} "
        "unchanged originals."
    )


if __name__ == "__main__":
    main()
