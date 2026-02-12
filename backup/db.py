# -*- coding: utf-8 -*-
"""SQLite database for Premium Showcase"""
import json
import os
import sqlite3
import threading
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "products.db")
_db_lock = threading.Lock()


def _ensure_data_dir():
    d = os.path.dirname(DB_PATH)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


@contextmanager
def _get_conn(timeout=30.0):
    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH, timeout=timeout)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 5000")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def get_db():
    """Return a new connection (for compatibility). Prefer using _get_conn()."""
    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database and create tables if needed."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                detailedDescription TEXT,
                code TEXT,
                image TEXT NOT NULL,
                specs TEXT,
                features TEXT,
                price TEXT,
                downloadUrl TEXT,
                createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur = conn.execute("SELECT COUNT(*) as c FROM products")
        count = cur.fetchone()[0]
        if count == 0:
            _insert_sample_products(conn)
        cur = conn.execute("PRAGMA table_info(products)")
        cols = [row[1] for row in cur.fetchall()]
        if "downloadUrl" not in cols:
            conn.execute("ALTER TABLE products ADD COLUMN downloadUrl TEXT")


def _insert_sample_products(conn):
    samples = [
        {
            "name": "Mythic Legends",
            "category": "Mobile Game",
            "description": "3D 액션 RPG 모바일 게임. 화려한 그래픽과 몰입감 있는 스토리로 전 세계 수백만 명의 플레이어를 사로잡았습니다.",
            "detailedDescription": "Mythic Legends는 최신 언리얼 엔진으로 제작된 3D 액션 RPG입니다. 100명 이상의 영웅을 수집하고, 다양한 던전을 탐험하며, 실시간 PvP 전투를 즐길 수 있습니다.",
            "code": "ML-001",
            "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&h=600&fit=crop",
            "specs": ["Android 6.0+", "iOS 12.0+", "3GB RAM", "2GB Storage"],
            "features": ["100+ 수집 가능한 영웅", "실시간 PvP 전투", "자동 전투 시스템", "길드 시스템", "정기 이벤트", "고품질 3D 그래픽"],
            "price": "무료 (인앱 구매)",
        },
        {
            "name": "Puzzle Quest Adventure",
            "category": "Mobile Game",
            "description": "퍼즐과 어드벤처가 결합된 캐주얼 게임. 간단한 조작으로 누구나 즐길 수 있으며, 중독성 있는 게임플레이를 제공합니다.",
            "detailedDescription": "Puzzle Quest Adventure는 매칭 퍼즐과 어드벤처 요소를 결합한 혁신적인 모바일 게임입니다.",
            "code": "PQA-002",
            "image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&h=600&fit=crop",
            "specs": ["Android 5.0+", "iOS 11.0+", "1GB RAM", "500MB Storage"],
            "features": ["500+ 레벨", "다양한 캐릭터 수집", "일일 퀘스트", "주간 이벤트", "소셜 기능", "오프라인 플레이 가능"],
            "price": "무료 (광고 지원)",
        },
        {
            "name": "Racing Champions",
            "category": "Mobile Game",
            "description": "고속 레이싱 게임. 현실적인 물리 엔진과 다양한 차량 커스터마이징으로 나만의 레이싱 경험을 만들어보세요.",
            "detailedDescription": "Racing Champions는 모바일에서 최고의 레이싱 경험을 제공하는 게임입니다.",
            "code": "RC-003",
            "image": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&h=600&fit=crop",
            "specs": ["Android 7.0+", "iOS 13.0+", "2GB RAM", "1.5GB Storage"],
            "features": ["50+ 실제 차량", "실시간 멀티플레이어", "리그 시스템", "차량 커스터마이징", "다양한 트랙", "현실적인 물리 엔진"],
            "price": "무료 (인앱 구매)",
        },
        {
            "name": "Idle Empire Builder",
            "category": "Mobile Game",
            "description": "방치형 제국 건설 게임. 자동으로 자원을 수집하고 제국을 확장하며 강력한 군대를 육성하세요.",
            "detailedDescription": "Idle Empire Builder는 전략과 방치형 게임플레이를 결합한 게임입니다.",
            "code": "IEB-004",
            "image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&h=600&fit=crop",
            "specs": ["Android 5.0+", "iOS 11.0+", "1GB RAM", "800MB Storage"],
            "features": ["방치형 게임플레이", "오프라인 보상", "다양한 건물", "영웅 시스템", "제국 전쟁", "길드 협력"],
            "price": "무료 (인앱 구매)",
        },
    ]
    for p in samples:
        conn.execute(
            """
            INSERT INTO products (name, category, description, detailedDescription, code, image, specs, features, price, downloadUrl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                p["name"], p["category"], p["description"], p.get("detailedDescription"),
                p.get("code"), p["image"], json.dumps(p["specs"]), json.dumps(p["features"]), p.get("price", ""),
                p.get("downloadUrl") or None,
            ),
        )


def load_products():
    """Load all products from database."""
    with _db_lock:
        with _get_conn() as conn:
            cur = conn.execute("SELECT * FROM products ORDER BY id")
            rows = cur.fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["specs"] = json.loads(d["specs"]) if d.get("specs") else []
        d["features"] = json.loads(d["features"]) if d.get("features") else []
        result.append(d)
    return result


def save_product(data):
    """Create or update a product. data는 security.validate_product_data()로 검증된 객체여야 함."""
    pid = data.get("id")
    specs = data.get("specs") or []
    features = data.get("features") or []
    if isinstance(specs, list):
        specs = json.dumps(specs)
    if isinstance(features, list):
        features = json.dumps(features)

    with _db_lock:
        with _get_conn() as conn:
            download_url = (data.get("downloadUrl") or "").strip() or None
            if pid:
                conn.execute(
                    """
                    UPDATE products SET
                        name=?, category=?, description=?, detailedDescription=?,
                        code=?, image=?, specs=?, features=?, price=?, downloadUrl=?,
                        updatedAt=CURRENT_TIMESTAMP
                    WHERE id=?
                    """,
                    (
                        data.get("name"), data.get("category"), data.get("description"),
                        data.get("detailedDescription") or None, data.get("code") or None,
                        data.get("image", ""), specs, features, data.get("price") or None,
                        download_url, pid,
                    ),
                )
                return {**data, "id": pid}
            else:
                cur = conn.execute(
                    """
                    INSERT INTO products (name, category, description, detailedDescription, code, image, specs, features, price, downloadUrl)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data.get("name"), data.get("category"), data.get("description"),
                        data.get("detailedDescription") or None, data.get("code") or None,
                        data.get("image", ""), specs, features, data.get("price") or None,
                        download_url,
                    ),
                )
                new_id = cur.lastrowid
                return {**data, "id": new_id}


def delete_product(product_id):
    """Delete a product. Returns True if deleted. product_id는 반드시 int."""
    if not isinstance(product_id, int) or product_id <= 0:
        return False
    with _db_lock:
        with _get_conn() as conn:
            cur = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            return cur.rowcount > 0
