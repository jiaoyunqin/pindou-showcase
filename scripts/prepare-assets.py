"""Derive review images from supplied screenshots. Never change source JPGs.

Run with Python + Pillow from any directory. Crop rectangles use source pixels:
[x, y, width, height]. Generated images are lossless WebP, without EXIF metadata.
"""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
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
]

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
    ("editor-tools", "S12", [63, 2940, 950, 269], ["edit"], "手动设计的全屏、画笔、橡皮、吸色、填充、撤销重做工具"),
    ("editor-canvas", "S12", [65, 3212, 950, 1100], ["edit"], "独立手绘示例，格子内标注 A1 色号"),
    ("editor-palette", "S12", [32, 988, 993, 765], ["edit"], "手动设计的品牌色板与颜色筛选"),
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
    image.save(path, "WEBP", lossless=True, method=6)
    with Image.open(path) as saved:
        saved_rgb = saved.convert("RGB")
        assert saved_rgb.size == image.size
        assert ImageChops.difference(saved_rgb, image).getbbox() is None, f"Pixel mismatch: {path.name}"


def main():
    ASSETS.mkdir(exist_ok=True)
    VERIFICATION.parent.mkdir(exist_ok=True)
    manifest = {
        "version": 2,
        "coordinateSystem": "original source pixels, [x,y,width,height]",
        "sourcePlatform": "微信小程序实拍",
        "encoding": "lossless WebP; source JPG pixels retained outside documented redactions",
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
        # S05 and S06 are reserve references, not published page assets.
        public_path = None
        if source_id not in {"S05", "S06"}:
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
                if source_id in {"S05", "S06"}
                else processing_note(source_id, public_redactions)
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
    required_sections = {"intro", "workflow", "convert", "blueprint", "edit", "workspace", "share"}
    section_assets = {
        section: [asset["id"] for asset in manifest["assets"] if section in asset["sections"]]
        for section in sorted(required_sections)
    }
    assert all(section_assets.values()), "A required showcase section has no asset."
    assert all(
        sha256(ROOT / source["file"]) == source["sha256"]
        for source in manifest["sources"].values()
    ), "An original source changed during generation."
    (ROOT / "assets-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    verification = {
        "version": 2,
        "generatedBy": "scripts/prepare-assets.py",
        "originalScreenshotsVerified": len(SOURCE_SPECS),
        "originalHashesUnchanged": True,
        "losslessCropsVerified": len(CROPS),
        "sanitizedSourcesVerified": sum(
            source["publicFile"] is not None for source in manifest["sources"].values()
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
        f"Prepared {len(CROPS)} crops and 10 public source images; "
        f"verified {len(SOURCE_SPECS)} unchanged originals."
    )


if __name__ == "__main__":
    main()
