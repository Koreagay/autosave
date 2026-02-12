# -*- coding: utf-8 -*-
"""Flask Premium Showcase App - 보안 강화"""
import os
import secrets
import threading
import time
from collections import defaultdict
from flask import Flask, jsonify, make_response, redirect, render_template, request

from db import init_db, load_products, save_product, delete_product
from security import validate_product_data

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# Admin credentials (환경변수로 오버라이드 권장)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin1234")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "xdayoungx1234")

sessions = {}
_sessions_lock = threading.Lock()

# Rate limit: 로그인 시도 (IP별, 5회/분)
_login_attempts = defaultdict(list)
_login_lock = threading.Lock()
LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 60


def _get_client_ip():
    return request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or request.remote_addr or ""


def _check_login_rate_limit():
    ip = _get_client_ip()
    now = time.time()
    with _login_lock:
        _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < LOGIN_RATE_WINDOW]
        if len(_login_attempts[ip]) >= LOGIN_RATE_LIMIT:
            return False
        _login_attempts[ip].append(now)
        return True


def require_auth():
    """API 전용: Authorization Bearer 또는 쿠키 admin_session 검증. 로그인된 경우에만 통과."""
    session_id = None
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        session_id = auth.replace("Bearer ", "").strip()
    if not session_id:
        session_id = request.cookies.get("admin_session") or ""
    if not session_id or len(session_id) > 128:
        return None
    with _sessions_lock:
        session = sessions.get(session_id)
        if not session or session["expires"] < int(time.time() * 1000):
            if session_id in sessions:
                del sessions[session_id]
            return None
        return session_id


def _is_admin_logged_in():
    """페이지 렌더 시 로그인 여부 (쿠키 기준)."""
    return require_auth() is not None


@app.context_processor
def inject_client_info():
    ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or request.remote_addr or "—"
    ua = (request.headers.get("User-Agent") or "")[:80]
    return {
        "client_ip": ip,
        "user_agent": ua,
        "is_admin": _is_admin_logged_in(),
    }


@app.after_request
def add_security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-XSS-Protection"] = "1; mode=block"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' https: http: data:; "
        "connect-src 'self'"
    )
    return resp


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
def admin_login_page():
    return render_template("admin/login.html")


@app.route("/admin/dashboard")
def admin_dashboard_page():
    if not _is_admin_logged_in():
        return redirect("/admin")
    return render_template("admin/dashboard.html")


# === API Routes ===

@app.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    if not _check_login_rate_limit():
        return jsonify({"error": "Too many attempts. Try again later."}), 429

    data = request.get_json(force=True, silent=True) or {}
    username = str(data.get("username", "")).strip()[:64]
    password = str(data.get("password", ""))[:128]

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session_id = secrets.token_urlsafe(32)
        with _sessions_lock:
            sessions[session_id] = {
                "username": username,
                "expires": int(time.time() * 1000) + 24 * 60 * 60 * 1000,
            }
        resp = make_response(jsonify({"success": True, "sessionId": session_id}))
        resp.set_cookie(
            "admin_session",
            session_id,
            max_age=24 * 60 * 60,
            path="/",
            samesite="Lax",
            httponly=True,
        )
        return resp
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/products", methods=["GET"])
def api_products_list():
    try:
        products = load_products()
        return jsonify(products)
    except Exception as e:
        app.logger.error("Error loading products: %s", e)
        return jsonify({"error": "Failed to load products"}), 500


@app.route("/api/products", methods=["POST"])
def api_products_create():
    if not require_auth():
        return jsonify({"error": "Unauthorized"}), 401
    try:
        raw = request.get_json(force=True, silent=True) or {}
        data = validate_product_data(raw)
        if not data:
            return jsonify({"error": "Invalid product data"}), 400
        product = save_product(data)
        return jsonify(product)
    except Exception as e:
        app.logger.error("Error creating product: %s", e)
        return jsonify({"error": "Failed to create product"}), 500


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def api_products_update(product_id):
    if not require_auth():
        return jsonify({"error": "Unauthorized"}), 401
    if product_id <= 0:
        return jsonify({"error": "Invalid product id"}), 400
    try:
        raw = request.get_json(force=True, silent=True) or {}
        raw["id"] = product_id
        data = validate_product_data(raw)
        if not data:
            return jsonify({"error": "Invalid product data"}), 400
        product = save_product(data)
        return jsonify(product)
    except Exception as e:
        app.logger.error("Error updating product: %s", e)
        return jsonify({"error": "Failed to update product"}), 500


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def api_products_delete(product_id):
    if not require_auth():
        return jsonify({"error": "Unauthorized"}), 401
    try:
        success = delete_product(product_id)
        if not success:
            return jsonify({"error": "Product not found"}), 404
        return jsonify({"success": True})
    except Exception as e:
        app.logger.error("Error deleting product: %s", e)
        return jsonify({"error": "Failed to delete product"}), 500


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 80))
    app.run(host="0.0.0.0", port=port, debug=True)
