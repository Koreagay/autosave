# -*- coding: utf-8 -*-
"""보안 유틸리티: 입력 검증, XSS 방지 등"""

# 필드별 최대 길이
MAX_LEN = {
    "name": 200,
    "category": 100,
    "description": 5000,
    "detailedDescription": 10000,
    "code": 50,
    "image": 8000,  # data URL 포함
    "price": 100,
    "downloadUrl": 2048,
    "spec_item": 500,
    "feature_item": 500,
    "specs_count": 20,
    "features_count": 30,
}


def _truncate(s, max_len):
    if s is None:
        return ""
    s = str(s).strip()
    return s[:max_len] if len(s) > max_len else s


def _safe_str(val, max_len=1000):
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    return s[:max_len]


def validate_product_data(data):
    """
    제품 데이터 검증. 위험한 값 제거/차단.
    SQL Injection은 파라미터화로 방지되지만, 추가로 입력 정규화 수행.
    """
    if not isinstance(data, dict):
        return None

    name = _safe_str(data.get("name"), MAX_LEN["name"])
    category = _safe_str(data.get("category"), MAX_LEN["category"])
    description = _safe_str(data.get("description"), MAX_LEN["description"])
    if not name or not category or not description:
        return None

    detailed_description = _safe_str(data.get("detailedDescription"), MAX_LEN["detailedDescription"])
    code = _safe_str(data.get("code"), MAX_LEN["code"])
    raw_price = data.get("price")
    if raw_price is None:
        price = "0"
    else:
        digits = "".join(c for c in str(raw_price) if c.isdigit())
        price = digits[:15] if digits else "0"

    # 이미지 URL 검증: https, http, data:image/ 만 허용
    raw_image = data.get("image")
    image = ""
    if raw_image and isinstance(raw_image, str):
        u = raw_image.strip().lower()
        if u.startswith("https://") or u.startswith("http://"):
            image = _truncate(raw_image, MAX_LEN["image"])
        elif u.startswith("data:image/"):
            image = _truncate(raw_image, MAX_LEN["image"])

    specs = data.get("specs")
    if not isinstance(specs, list):
        specs = []
    specs = [
        _truncate(str(s), MAX_LEN["spec_item"])
        for s in specs[: MAX_LEN["specs_count"]]
        if s is not None
    ]

    features = data.get("features")
    if not isinstance(features, list):
        features = []
    features = [
        _truncate(str(f), MAX_LEN["feature_item"])
        for f in features[: MAX_LEN["features_count"]]
        if f is not None
    ]

    raw_download = data.get("downloadUrl")
    download_url = ""
    if raw_download and isinstance(raw_download, str):
        u = raw_download.strip().lower()
        if u.startswith("https://") or u.startswith("http://"):
            download_url = _truncate(raw_download.strip(), MAX_LEN["downloadUrl"])

    return {
        "name": name,
        "category": category,
        "description": description,
        "detailedDescription": detailed_description or "",
        "code": code or "",
        "image": image,
        "price": price or "",
        "downloadUrl": download_url,
        "specs": specs,
        "features": features,
        "id": data.get("id") if isinstance(data.get("id"), int) else None,
    }
