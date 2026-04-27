import json
import mimetypes
import re
import sqlite3
import unicodedata
import uuid
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import streamlit as st

try:
    import fitz
except Exception:
    fitz = None

APP_DIR = Path(__file__).parent
UPLOAD_FOLDER = APP_DIR / "uploads_streamlit"
DB_PATH = APP_DIR / "blancos_primavera.db"
GRAPH_API = "https://graph.facebook.com/v21.0"

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

CATEGORIES = ["Catalogos", "Promociones", "Producto", "Marketing", "Operacion"]
SECTIONS = ["Recamara", "Bano", "Hoteleria", "Infantil", "Tienda"]
BRANDS = ["Blancos Primavera", "Linea Casa", "Linea Premium", "Linea Hotel"]
CATALOG_KINDS = ["image", "pdf"]

CATEGORY_RULES: dict[str, list[str]] = {
    "Catalogos": ["catalogo", "catalog", "lookbook", "coleccion", "temporada"],
    "Promociones": ["promo", "oferta", "descuento", "campana", "hot", "sale"],
    "Producto": ["producto", "sku", "ficha", "medida", "modelo", "textura"],
    "Marketing": ["instagram", "facebook", "tiktok", "banner", "story", "reel"],
    "Operacion": ["manual", "proceso", "inventario", "embarque", "factura", "guia"],
}

SECTION_RULES: dict[str, list[str]] = {
    "Recamara": ["recamara", "sabanas", "edredon", "almohada", "duvet"],
    "Bano": ["bano", "toalla", "tapete", "cortina", "bata"],
    "Hoteleria": ["hotel", "hospedaje", "institucional"],
    "Infantil": ["kids", "infantil", "bebe", "junior"],
    "Tienda": ["sucursal", "vitrina", "aparador", "display"],
}

BRAND_RULES: dict[str, list[str]] = {
    "Blancos Primavera": ["primavera", "bp", "blancos"],
    "Linea Casa": ["casa", "home", "hogar"],
    "Linea Premium": ["premium", "lux", "deluxe"],
    "Linea Hotel": ["hotel", "hosteleria", "institutional"],
}

DEFAULT_ACCESS_TOKEN = (
    "EAAXyxW6E7nABQ38lddubKfDadICgCEiAHA1mszd25a8gtEmbgAiaZBve6cOBWZBiYPamETxsZAKsBZCYBrqy4IWt0XeN9"
    "ZBYJpAppqXpGtyQ4JpWkL4suvaYZAz9YgqLuoEXRYVI4AVZAnUXXiRuMUdx9ZAO7ZBkVp0KpWmkCw4m7ayuRNolef7bvlcozp9v"
    "WGiLhrgZDZD"
)
DEFAULT_PHONE_NUMBER_ID = "1002988366233141"
DEFAULT_TEMPLATE_NAME = "nueva_plantilla_de_whatsapp_05_03_2026_01_39_ajhk6i"
DEFAULT_TEMPLATE_LANGUAGE = "es_MX"


def db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(db_connect()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS media_items (
                id TEXT PRIMARY KEY,
                original_name TEXT NOT NULL,
                stored_name TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                kind TEXT NOT NULL,
                size INTEGER NOT NULL,
                category TEXT NOT NULL,
                section TEXT NOT NULL,
                brand TEXT NOT NULL,
                tags_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS wa_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                access_token TEXT NOT NULL,
                phone_number_id TEXT NOT NULL,
                template_name TEXT NOT NULL,
                template_language_code TEXT NOT NULL
            )
            """
        )
        conn.commit()


def ensure_default_wa_config() -> None:
    defaults = {
        "access_token": DEFAULT_ACCESS_TOKEN,
        "phone_number_id": DEFAULT_PHONE_NUMBER_ID,
        "template_name": DEFAULT_TEMPLATE_NAME,
        "template_language_code": DEFAULT_TEMPLATE_LANGUAGE,
    }

    if "whatsapp" in st.secrets:
        secret_cfg = st.secrets["whatsapp"]
        defaults["access_token"] = secret_cfg.get("access_token", defaults["access_token"])
        defaults["phone_number_id"] = secret_cfg.get("phone_number_id", defaults["phone_number_id"])
        defaults["template_name"] = secret_cfg.get("template_name", defaults["template_name"])
        defaults["template_language_code"] = secret_cfg.get("template_language_code", defaults["template_language_code"])

    with closing(db_connect()) as conn:
        row = conn.execute("SELECT id FROM wa_config WHERE id = 1").fetchone()
        if row is None:
            conn.execute(
                """
                INSERT INTO wa_config (id, access_token, phone_number_id, template_name, template_language_code)
                VALUES (1, ?, ?, ?, ?)
                """,
                (
                    defaults["access_token"],
                    defaults["phone_number_id"],
                    defaults["template_name"],
                    defaults["template_language_code"],
                ),
            )
            conn.commit()


def load_wa_config() -> dict[str, str]:
    with closing(db_connect()) as conn:
        row = conn.execute(
            """
            SELECT access_token, phone_number_id, template_name, template_language_code
            FROM wa_config
            WHERE id = 1
            """
        ).fetchone()

    if not row:
        return {
            "access_token": DEFAULT_ACCESS_TOKEN,
            "phone_number_id": DEFAULT_PHONE_NUMBER_ID,
            "template_name": DEFAULT_TEMPLATE_NAME,
            "template_language_code": DEFAULT_TEMPLATE_LANGUAGE,
        }

    return {
        "access_token": row["access_token"],
        "phone_number_id": row["phone_number_id"],
        "template_name": row["template_name"],
        "template_language_code": row["template_language_code"],
    }


def save_wa_config(config: dict[str, str]) -> None:
    with closing(db_connect()) as conn:
        conn.execute(
            """
            INSERT INTO wa_config (id, access_token, phone_number_id, template_name, template_language_code)
            VALUES (1, ?, ?, ?, ?)
            ON CONFLICT(id)
            DO UPDATE SET
                access_token = excluded.access_token,
                phone_number_id = excluded.phone_number_id,
                template_name = excluded.template_name,
                template_language_code = excluded.template_language_code
            """,
            (
                config["access_token"].strip(),
                config["phone_number_id"].strip(),
                config["template_name"].strip(),
                config["template_language_code"].strip() or DEFAULT_TEMPLATE_LANGUAGE,
            ),
        )
        conn.commit()


def parse_tags(tags_json: str) -> list[str]:
    try:
        tags = json.loads(tags_json)
        if isinstance(tags, list):
            return [str(t) for t in tags if str(t).strip()]
    except Exception:
        pass
    return []


def fetch_all_media() -> list[dict[str, Any]]:
    with closing(db_connect()) as conn:
        rows = conn.execute(
            """
            SELECT id, original_name, stored_name, mime_type, kind, size,
                   category, section, brand, tags_json, created_at
            FROM media_items
            ORDER BY created_at DESC
            """
        ).fetchall()

    result: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["tags"] = parse_tags(item["tags_json"])
        item["file_path"] = str(UPLOAD_FOLDER / item["stored_name"])
        result.append(item)
    return result


def update_media_metadata(item_id: str, category: str, section: str, brand: str, tags: list[str]) -> None:
    with closing(db_connect()) as conn:
        conn.execute(
            """
            UPDATE media_items
            SET category = ?, section = ?, brand = ?, tags_json = ?
            WHERE id = ?
            """,
            (category, section, brand, json.dumps(tags, ensure_ascii=True), item_id),
        )
        conn.commit()


def update_media_name(item_id: str, new_name: str) -> None:
    clean_name = new_name.strip()
    if not clean_name:
        raise ValueError("El nombre no puede estar vacio")

    with closing(db_connect()) as conn:
        row = conn.execute(
            "SELECT original_name FROM media_items WHERE id = ?",
            (item_id,),
        ).fetchone()

        if not row:
            raise ValueError("No se encontro el catalogo a renombrar")

        current_name = str(row["original_name"])
        current_ext = Path(current_name).suffix
        new_ext = Path(clean_name).suffix
        normalized_name = clean_name if new_ext else f"{clean_name}{current_ext}"

        conn.execute(
            "UPDATE media_items SET original_name = ? WHERE id = ?",
            (normalized_name, item_id),
        )
        conn.commit()


def delete_media_item(item_id: str) -> None:
    with closing(db_connect()) as conn:
        row = conn.execute("SELECT stored_name FROM media_items WHERE id = ?", (item_id,)).fetchone()
        if row:
            file_path = UPLOAD_FOLDER / row["stored_name"]
            if file_path.exists():
                file_path.unlink()
        conn.execute("DELETE FROM media_items WHERE id = ?", (item_id,))
        conn.commit()


def normalize_name(name: str) -> str:
    stem = Path(name).stem
    ascii_stem = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode("ascii")
    ascii_stem = re.sub(r"[^a-zA-Z0-9_-]+", "_", ascii_stem).strip("_")
    return ascii_stem or "archivo"


def dedupe(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = value.strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        out.append(clean)
    return out


def infer_kind(mime_type: str, filename: str) -> str:
    mime = (mime_type or "").lower()
    name = filename.lower()
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("video/"):
        return "video"
    if mime.startswith("audio/"):
        return "audio"
    if mime == "application/pdf" or name.endswith(".pdf"):
        return "pdf"
    return "other"


def score_name(name: str, rules: dict[str, list[str]], fallback: str) -> tuple[str, int, list[str]]:
    winner = fallback
    best_score = 0
    best_hits: list[str] = []
    for label, keywords in rules.items():
        hits = [word for word in keywords if word in name]
        if len(hits) > best_score:
            best_score = len(hits)
            winner = label
            best_hits = hits
    return winner, best_score, best_hits


def suggest_classification(filename: str, mime_type: str) -> dict[str, Any]:
    name = filename.lower()
    kind = infer_kind(mime_type, filename)

    base_category = "Catalogos" if kind == "pdf" else "Marketing" if kind == "video" else "Producto"
    base_section = "Tienda"
    base_brand = "Blancos Primavera"

    category, cat_score, cat_hits = score_name(name, CATEGORY_RULES, base_category)
    section, sec_score, sec_hits = score_name(name, SECTION_RULES, base_section)
    brand, brand_score, brand_hits = score_name(name, BRAND_RULES, base_brand)

    tags = dedupe([kind, *cat_hits, *sec_hits, *brand_hits])
    confidence = min(100, 35 + cat_score * 20 + sec_score * 20 + brand_score * 15)

    return {
        "category": category,
        "section": section,
        "brand": brand,
        "tags": tags,
        "confidence": confidence,
        "kind": kind,
    }


def store_uploaded_file(
    uploaded_file: Any,
    smart_mode: bool,
    manual_category: str,
    manual_section: str,
    manual_brand: str,
    manual_tags: list[str],
) -> dict[str, Any]:
    raw_name = uploaded_file.name
    mime_type = uploaded_file.type or mimetypes.guess_type(raw_name)[0] or "application/octet-stream"
    suggestion = suggest_classification(raw_name, mime_type)

    category = suggestion["category"] if smart_mode else manual_category
    section = suggestion["section"] if smart_mode else manual_section
    brand = suggestion["brand"] if smart_mode else manual_brand
    tags = dedupe([*suggestion["tags"], *manual_tags, f"ia:{suggestion['confidence']}"])
    kind = suggestion["kind"]

    ext = Path(raw_name).suffix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    stored_name = f"blancos_{timestamp}_{normalize_name(raw_name)}{ext}"
    file_path = UPLOAD_FOLDER / stored_name

    content = uploaded_file.getvalue()
    if not content:
        raise ValueError(f"{raw_name}: archivo vacio o no legible")

    with open(file_path, "wb") as f:
        f.write(content)

    record_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"

    with closing(db_connect()) as conn:
        conn.execute(
            """
            INSERT INTO media_items (
                id, original_name, stored_name, mime_type, kind, size,
                category, section, brand, tags_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                raw_name,
                stored_name,
                mime_type,
                kind,
                len(content),
                category,
                section,
                brand,
                json.dumps(tags, ensure_ascii=True),
                created_at,
            ),
        )
        conn.commit()

    return {
        "id": record_id,
        "original_name": raw_name,
        "stored_name": stored_name,
        "category": category,
        "section": section,
        "brand": brand,
        "tags": tags,
        "kind": kind,
        "size": len(content),
        "created_at": created_at,
    }


def normalize_phone(input_value: str) -> str:
    digits = re.sub(r"\D", "", input_value)
    if not re.match(r"^\d{8,15}$", digits):
        raise ValueError("Numero invalido. Debe tener entre 8 y 15 digitos en formato E.164 sin +")
    return digits


def graph_error_text(response: requests.Response) -> str:
    try:
        payload = response.json()
    except Exception:
        return response.text or f"HTTP {response.status_code}"

    if "error" not in payload:
        return response.text or f"HTTP {response.status_code}"

    err = payload["error"]
    parts = [
        err.get("message"),
        f"type={err.get('type')}" if err.get("type") else None,
        f"code={err.get('code')}" if err.get("code") else None,
        err.get("error_data", {}).get("details") if isinstance(err.get("error_data"), dict) else None,
    ]
    clean = [p for p in parts if p]
    return " | ".join(clean) if clean else response.text or f"HTTP {response.status_code}"


def language_fallbacks(language_code: str) -> list[str]:
    base = language_code.strip() or DEFAULT_TEMPLATE_LANGUAGE
    variants = [
        base,
        base.split("_")[0] if "_" in base else f"{base}_MX",
        "es_MX",
        "es",
        "en",
        "en_US",
    ]
    return dedupe([v for v in variants if v])


def send_template_and_text(config: dict[str, str], destination: str, text: str) -> dict[str, str]:
    token = config["access_token"].strip()
    phone_number_id = config["phone_number_id"].strip()
    template_name = config["template_name"].strip()
    language_code = config["template_language_code"].strip() or DEFAULT_TEMPLATE_LANGUAGE
    to = normalize_phone(destination)

    if not token or not phone_number_id or not template_name:
        raise ValueError("Configura token, phone_number_id y template_name antes de enviar")

    url = f"{GRAPH_API}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    template_ack: dict[str, str] | None = None
    last_error = ""

    for lang in language_fallbacks(language_code):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": lang},
            },
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.ok:
            data = response.json()
            message_id = (data.get("messages") or [{}])[0].get("id")
            wa_id = (data.get("contacts") or [{}])[0].get("wa_id")
            if message_id:
                template_ack = {
                    "template_message_id": message_id,
                    "wa_id": wa_id or "",
                }
                break

        last_error = f"idioma={lang}: {graph_error_text(response)}"

    if template_ack is None:
        raise RuntimeError(f"No se pudo enviar plantilla en ningun idioma. Ultimo intento: {last_error}")

    body_text = text.strip()
    if not body_text:
        template_ack["text_message_id"] = template_ack["template_message_id"]
        return template_ack

    text_payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": body_text,
            "preview_url": False,
        },
    }

    response = requests.post(url, headers=headers, json=text_payload, timeout=30)
    if not response.ok:
        raise RuntimeError(f"Error enviando texto: {graph_error_text(response)}")

    data = response.json()
    text_message_id = (data.get("messages") or [{}])[0].get("id")
    if not text_message_id:
        raise RuntimeError(f"WhatsApp respondio sin message id en texto: {response.text}")

    template_ack["text_message_id"] = text_message_id
    return template_ack


def send_text_only(config: dict[str, str], destination: str, text: str) -> str:
    token = config["access_token"].strip()
    phone_number_id = config["phone_number_id"].strip()
    to = normalize_phone(destination)
    body_text = text.strip()

    if not token or not phone_number_id:
        raise ValueError("Configura token y phone_number_id antes de enviar")
    if not body_text:
        raise ValueError("El mensaje no puede estar vacio para envio de texto sin plantilla")

    url = f"{GRAPH_API}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": body_text,
            "preview_url": False,
        },
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if not response.ok:
        raise RuntimeError(f"Error enviando texto sin plantilla: {graph_error_text(response)}")

    message_id = (response.json().get("messages") or [{}])[0].get("id")
    if not message_id:
        raise RuntimeError(f"WhatsApp no devolvio message id en texto: {response.text}")

    return message_id


def upload_media_to_whatsapp(config: dict[str, str], item: dict[str, Any]) -> str:
    token = config["access_token"].strip()
    phone_number_id = config["phone_number_id"].strip()
    if not token or not phone_number_id:
        raise ValueError("Configura token y phone_number_id")

    file_path = Path(item["file_path"])
    if not file_path.exists():
        raise FileNotFoundError(f"No existe el archivo local: {file_path}")

    url = f"{GRAPH_API}/{phone_number_id}/media"
    headers = {
        "Authorization": f"Bearer {token}",
    }

    mime_type = item["mime_type"] or "application/octet-stream"
    data = {
        "messaging_product": "whatsapp",
        "type": mime_type,
    }

    with open(file_path, "rb") as file_handle:
        files = {
            "file": (item["original_name"], file_handle, mime_type),
        }
        response = requests.post(url, headers=headers, data=data, files=files, timeout=90)

    if not response.ok:
        raise RuntimeError(f"Error subiendo media a WhatsApp: {graph_error_text(response)}")

    media_id = response.json().get("id")
    if not media_id:
        raise RuntimeError(f"WhatsApp no devolvio media id: {response.text}")

    return media_id


def send_media_message(config: dict[str, str], destination: str, item: dict[str, Any], media_id: str) -> str:
    token = config["access_token"].strip()
    phone_number_id = config["phone_number_id"].strip()
    to = normalize_phone(destination)

    url = f"{GRAPH_API}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    caption = f"{item['original_name']} - Blancos Primavera"
    kind = item["kind"]

    if kind == "image":
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {
                "id": media_id,
                "caption": caption,
            },
        }
    elif kind == "video":
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "video",
            "video": {
                "id": media_id,
                "caption": caption,
            },
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": {
                "id": media_id,
                "filename": item["original_name"],
                "caption": caption,
            },
        }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if not response.ok:
        raise RuntimeError(f"Error enviando mensaje multimedia: {graph_error_text(response)}")

    message_id = (response.json().get("messages") or [{}])[0].get("id")
    if not message_id:
        raise RuntimeError(f"WhatsApp no devolvio message id: {response.text}")

    return message_id


def send_catalog_from_card(
    config: dict[str, str],
    item: dict[str, Any],
    destination: str,
    bootstrap_mode: str,
    message: str,
) -> str:
    steps: list[str] = []

    if bootstrap_mode == "Plantilla + mensaje + catalogo":
        ack = send_template_and_text(config, destination, message)
        steps.append(f"Template: {ack['template_message_id']}")
    elif bootstrap_mode == "Mensaje + catalogo (sin plantilla)":
        body = message.strip()
        if not body:
            raise ValueError("Escribe un mensaje para el modo 'Mensaje + catalogo (sin plantilla)'")
        text_id = send_text_only(config, destination, body)
        steps.append(f"Texto: {text_id}")

    media_id = upload_media_to_whatsapp(config, item)
    message_id = send_media_message(config, destination, item, media_id)
    steps.append(f"Catalogo: {message_id}")
    return " | ".join(steps)


def matches_query(item: dict[str, Any], query: str) -> bool:
    q = query.strip().lower()
    if not q:
        return True
    haystack = " ".join(
        [
            item["original_name"],
            item["category"],
            item["section"],
            item["brand"],
            " ".join(item["tags"]),
        ]
    ).lower()
    return q in haystack


def filter_media(
    items: list[dict[str, Any]],
    query: str = "",
    category: str = "Todas",
    section: str = "Todas",
    brand: str = "Todas",
    kinds: list[str] | None = None,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in items:
        if kinds and item["kind"] not in kinds:
            continue
        if category != "Todas" and item["category"] != category:
            continue
        if section != "Todas" and item["section"] != section:
            continue
        if brand != "Todas" and item["brand"] != brand:
            continue
        if not matches_query(item, query):
            continue
        result.append(item)
    return result


def bytes_to_text(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def format_date(value: str) -> str:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return value


def build_summary(items: list[dict[str, Any]], title: str, context: str) -> str:
    if not items:
        return "\n".join([x for x in [title, context, "No hay archivos seleccionados."] if x])

    category_counts: dict[str, int] = {}
    section_counts: dict[str, int] = {}
    for item in items:
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1
        section_counts[item["section"]] = section_counts.get(item["section"], 0) + 1

    top_categories = " | ".join(
        [f"{name}: {qty}" for name, qty in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]]
    )
    top_sections = " | ".join(
        [f"{name}: {qty}" for name, qty in sorted(section_counts.items(), key=lambda x: x[1], reverse=True)[:3]]
    )
    previews = "\n".join(
        [
            f"- {item['original_name']} ({item['category']}/{item['section']}/{item['brand']})"
            for item in items[:8]
        ]
    )

    lines = [
        title,
        context,
        f"Total archivos: {len(items)}",
        f"Categorias clave: {top_categories or 'N/A'}",
        f"Secciones clave: {top_sections or 'N/A'}",
        "Listado:",
        previews,
    ]
    return "\n".join([x for x in lines if x])


def unique_options(base: list[str], items: list[dict[str, Any]], key: str) -> list[str]:
    values = base + [str(item[key]) for item in items]
    return dedupe(values)


def show_media_preview(item: dict[str, Any], key_suffix: str) -> None:
    file_path = Path(item["file_path"])
    if not file_path.exists():
        st.warning("Archivo no encontrado en disco")
        return

    if item["kind"] == "image":
        st.image(str(file_path), use_container_width=True)
        return

    if item["kind"] == "video":
        st.video(str(file_path))
        return

    with open(file_path, "rb") as f:
        st.download_button(
            label="Descargar archivo",
            data=f.read(),
            file_name=item["original_name"],
            key=f"download_{item['id']}_{key_suffix}",
            use_container_width=True,
        )


@st.cache_data(show_spinner=False, ttl=1800)
def build_pdf_thumbnail(file_path_str: str) -> bytes | None:
    if fitz is None:
        return None

    file_path = Path(file_path_str)
    if not file_path.exists():
        return None

    try:
        doc = fitz.open(file_path)
        if doc.page_count == 0:
            return None
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(0.9, 0.9), alpha=False)
        data = pix.tobytes("png")
        doc.close()
        return data
    except Exception:
        return None


def show_catalog_thumbnail(item: dict[str, Any]) -> None:
    file_path = Path(item["file_path"])
    if not file_path.exists():
        st.warning("Archivo no encontrado")
        return

    if item["kind"] == "image":
        st.image(str(file_path), use_container_width=True)
        return

    if item["kind"] == "pdf":
        thumb_data = build_pdf_thumbnail(str(file_path))
        if thumb_data:
            st.image(thumb_data, use_container_width=True)
        else:
            st.markdown('<div class="pdf-fallback">PDF<br/>Sin miniatura</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="pdf-fallback">Archivo no visualizable</div>', unsafe_allow_html=True)


def chunk_items(items: list[dict[str, Any]], chunk_size: int) -> list[list[dict[str, Any]]]:
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


st.set_page_config(
    page_title="Blancos Primavera | Multimedia",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .header {
        background: linear-gradient(135deg, #ff5ecf 0%, #ff98e8 100%);
        padding: 20px;
        border-radius: 12px;
        color: #2b0620;
        margin-bottom: 18px;
    }
    .header h1, .header p {
        margin: 0;
    }
    .header p {
        margin-top: 8px;
    }
    .pdf-fallback {
        min-height: 210px;
        border-radius: 12px;
        border: 1px dashed rgba(255, 94, 207, 0.35);
        background: linear-gradient(180deg, rgba(255, 94, 207, 0.12), rgba(23, 9, 23, 0.55));
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-weight: 700;
        color: #ffd7f5;
        padding: 14px;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(180deg, rgba(255, 94, 207, 0.08), rgba(13, 7, 15, 0.72));
        border: 1px solid rgba(255, 94, 207, 0.24) !important;
        border-radius: 14px !important;
        padding: 0.55rem;
        min-height: 100%;
    }
    .card-title {
        min-height: 2.8rem;
        font-weight: 700;
        color: #ffe9fb;
        margin-bottom: 0.2rem;
        word-break: break-word;
    }
    div[class*="st-key-catalog_send_"] button {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 999px !important;
        box-shadow: 0 10px 26px rgba(18, 140, 126, 0.35) !important;
    }
    div[class*="st-key-catalog_send_"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 30px rgba(18, 140, 126, 0.45) !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

init_db()
ensure_default_wa_config()

if "wa_message" not in st.session_state:
    st.session_state["wa_message"] = ""

st.markdown(
    """
<div class="header">
    <h1>Blancos Primavera | Plataforma Multimedia Unificada</h1>
    <p>Catalogo, gestion de archivos y envios WhatsApp en una sola app Streamlit con base de datos.</p>
</div>
""",
    unsafe_allow_html=True,
)

all_media = fetch_all_media()
categories = unique_options(CATEGORIES, all_media, "category")
sections = unique_options(SECTIONS, all_media, "section")
brands = unique_options(BRANDS, all_media, "brand")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Total archivos", len(all_media))
col_m2.metric("Catalogo (PDF/IMG)", len([m for m in all_media if m["kind"] in CATALOG_KINDS]))
col_m3.metric("Videos", len([m for m in all_media if m["kind"] == "video"]))
col_m4.metric("Espacio", f"{sum(m['size'] for m in all_media) / (1024 * 1024):.1f} MB")

tab_catalog, tab_manage, tab_send, tab_info = st.tabs(
    ["Catalogos", "Gestion", "Envios WhatsApp", "Info"]
)

with tab_catalog:
    col_q, col_cat = st.columns([2, 1])
    catalog_query = col_q.text_input("Buscar en catalogos", placeholder="Nombre, categoria, marca, tags")
    catalog_category = col_cat.selectbox("Categoria", ["Todas", *categories], index=0)

    st.markdown("#### Envio rapido desde cada card")
    quick_col_1, quick_col_2, quick_col_3 = st.columns([1.2, 1.4, 2.0])
    quick_destination = quick_col_1.text_input(
        "Numero destino",
        placeholder="5215512345678",
        key="catalog_quick_destination",
    )
    quick_send_mode = quick_col_2.selectbox(
        "Modo",
        options=[
            "Solo catalogo (sin plantilla)",
            "Mensaje + catalogo (sin plantilla)",
            "Plantilla + mensaje + catalogo",
        ],
        key="catalog_quick_mode",
    )
    quick_message = quick_col_3.text_input(
        "Mensaje opcional",
        value="Te comparto este catalogo de Blancos Primavera.",
        key="catalog_quick_message",
    )
    st.caption(
        "Tip: fuera de la ventana de 24h, usa 'Plantilla + mensaje + catalogo' para asegurar entrega."
    )

    catalog_items = filter_media(
        all_media,
        query=catalog_query,
        category=catalog_category,
        kinds=CATALOG_KINDS,
    )

    if not catalog_items:
        st.info("No hay catalogos visibles. Sube archivos en Gestion.")
    else:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for item in catalog_items:
            grouped.setdefault(item["category"], []).append(item)

        for group_name in sorted(grouped.keys()):
            group_items = grouped[group_name]
            st.markdown(f"### {group_name} ({len(group_items)})")
            for row_items in chunk_items(group_items, 4):
                row_cols = st.columns(4, gap="large")
                for col, item in zip(row_cols, row_items):
                    with col:
                        with st.container(border=True):
                            show_catalog_thumbnail(item)
                            st.markdown(f"<div class='card-title'>{item['original_name']}</div>", unsafe_allow_html=True)
                            st.caption(
                                f"{bytes_to_text(item['size'])} | {item['category']} / {item['section']} / {item['brand']}"
                            )

                            rename_value = st.text_input(
                                "Editar nombre",
                                value=item["original_name"],
                                key=f"catalog_name_{item['id']}",
                            )

                            action_col_1, action_col_2 = st.columns(2)
                            if action_col_1.button(
                                "Guardar",
                                key=f"catalog_save_{item['id']}",
                                use_container_width=True,
                            ):
                                try:
                                    update_media_name(item["id"], rename_value)
                                    st.success("Nombre actualizado")
                                    st.rerun()
                                except Exception as rename_error:
                                    st.error(str(rename_error))

                            if action_col_2.button(
                                "🟢 WhatsApp",
                                key=f"catalog_send_{item['id']}",
                                use_container_width=True,
                            ):
                                if not quick_destination.strip():
                                    st.error("Ingresa un numero destino para envio rapido")
                                else:
                                    try:
                                        cfg_now = load_wa_config()
                                        with st.spinner("Enviando catalogo por WhatsApp..."):
                                            send_detail = send_catalog_from_card(
                                                cfg_now,
                                                item,
                                                quick_destination,
                                                quick_send_mode,
                                                quick_message,
                                            )
                                        st.success(f"Catalogo enviado: {send_detail}")
                                    except Exception as send_error:
                                        error_text = str(send_error)
                                        st.error(error_text)
                                        if (
                                            "code=131" in error_text
                                            or "window" in error_text.lower()
                                            or "plantilla" in error_text.lower()
                                        ):
                                            st.warning(
                                                "El chat puede estar fuera de 24h. Prueba el modo 'Plantilla + mensaje + catalogo'."
                                            )

                            with st.expander("Opciones"):
                                show_media_preview(item, f"catalog_{item['id']}")

with tab_manage:
    st.subheader("Carga y clasificacion")

    smart_mode = st.checkbox("Modo inteligente (clasifica por nombre/tipo)", value=True)

    manual_col_1, manual_col_2, manual_col_3 = st.columns(3)
    manual_category = manual_col_1.selectbox("Categoria manual", categories, index=0)
    manual_section = manual_col_2.selectbox("Seccion manual", sections, index=min(4, len(sections) - 1))
    manual_brand = manual_col_3.selectbox("Marca manual", brands, index=0)
    manual_tags_input = st.text_input("Tags manuales (separados por coma)")

    uploaded_files = st.file_uploader(
        "Subir archivos multimedia",
        type=["pdf", "png", "jpg", "jpeg", "gif", "webp", "mp4", "mov", "avi", "mp3", "wav"],
        accept_multiple_files=True,
    )

    if st.button("Guardar archivos", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("Selecciona al menos un archivo")
        else:
            manual_tags = dedupe([t.strip().lower() for t in manual_tags_input.split(",") if t.strip()])
            saved = 0
            errors: list[str] = []
            for uploaded in uploaded_files:
                try:
                    store_uploaded_file(
                        uploaded,
                        smart_mode=smart_mode,
                        manual_category=manual_category,
                        manual_section=manual_section,
                        manual_brand=manual_brand,
                        manual_tags=manual_tags,
                    )
                    saved += 1
                except Exception as exc:
                    errors.append(f"{uploaded.name}: {exc}")

            if saved:
                st.success(f"Se guardaron {saved} archivo(s) en base de datos")
            if errors:
                for msg in errors:
                    st.error(msg)
            if saved:
                st.rerun()

    st.divider()
    st.markdown("### Archivos en base de datos")

    f_col_1, f_col_2, f_col_3, f_col_4 = st.columns(4)
    query_manage = f_col_1.text_input("Buscar", key="query_manage")
    filter_category = f_col_2.selectbox("Categoria", ["Todas", *categories], key="filter_category")
    filter_section = f_col_3.selectbox("Seccion", ["Todas", *sections], key="filter_section")
    filter_brand = f_col_4.selectbox("Marca", ["Todas", *brands], key="filter_brand")

    filtered_manage = filter_media(
        all_media,
        query=query_manage,
        category=filter_category,
        section=filter_section,
        brand=filter_brand,
    )

    if not filtered_manage:
        st.info("No hay archivos para los filtros seleccionados")
    else:
        for item in filtered_manage:
            with st.expander(f"{item['original_name']} | {item['category']} / {item['section']} / {item['brand']}"):
                st.caption(
                    f"{bytes_to_text(item['size'])} | {item['mime_type']} | cargado {format_date(item['created_at'])}"
                )
                show_media_preview(item, "manage")

                c1, c2, c3 = st.columns(3)
                edit_category = c1.selectbox(
                    "Categoria",
                    categories,
                    index=max(categories.index(item["category"]), 0) if item["category"] in categories else 0,
                    key=f"cat_{item['id']}",
                )
                edit_section = c2.selectbox(
                    "Seccion",
                    sections,
                    index=max(sections.index(item["section"]), 0) if item["section"] in sections else 0,
                    key=f"sec_{item['id']}",
                )
                edit_brand = c3.selectbox(
                    "Marca",
                    brands,
                    index=max(brands.index(item["brand"]), 0) if item["brand"] in brands else 0,
                    key=f"brand_{item['id']}",
                )
                edit_tags = st.text_input(
                    "Tags",
                    value=", ".join(item["tags"]),
                    key=f"tags_{item['id']}",
                )

                b1, b2 = st.columns(2)
                if b1.button("Guardar metadata", key=f"save_{item['id']}", use_container_width=True):
                    tags = dedupe([t.strip() for t in edit_tags.split(",") if t.strip()])
                    update_media_metadata(item["id"], edit_category, edit_section, edit_brand, tags)
                    st.success("Metadata actualizada")
                    st.rerun()

                if b2.button("Eliminar archivo", key=f"delete_{item['id']}", use_container_width=True):
                    delete_media_item(item["id"])
                    st.warning("Archivo eliminado")
                    st.rerun()

with tab_send:
    st.subheader("Envio por WhatsApp desde Streamlit")

    wa_cfg = load_wa_config()

    with st.expander("Configuracion de WhatsApp", expanded=True):
        cfg_1, cfg_2 = st.columns(2)
        cfg_3, cfg_4 = st.columns(2)

        wa_token = cfg_1.text_input("Access Token", value=wa_cfg["access_token"], type="password")
        wa_phone_id = cfg_2.text_input("Phone Number ID", value=wa_cfg["phone_number_id"])
        wa_template = cfg_3.text_input("Template Name", value=wa_cfg["template_name"])
        wa_lang = cfg_4.text_input("Template Language", value=wa_cfg["template_language_code"])

        if st.button("Guardar configuracion WhatsApp"):
            save_wa_config(
                {
                    "access_token": wa_token,
                    "phone_number_id": wa_phone_id,
                    "template_name": wa_template,
                    "template_language_code": wa_lang,
                }
            )
            st.success("Configuracion guardada")
            st.rerun()

    mode = st.radio("Modo de envio", options=["Album", "Archivos especificos"], horizontal=True)

    selected_items: list[dict[str, Any]] = []
    context_text = ""
    title_text = ""

    if mode == "Album":
        a1, a2, a3, a4 = st.columns(4)
        album_name = a1.text_input("Nombre del album", value="Cortinas")
        album_category = a2.selectbox("Categoria", ["Todas", *categories], key="album_category")
        album_section = a3.selectbox("Seccion", ["Todas", *sections], key="album_section")
        album_brand = a4.selectbox("Marca", ["Todas", *brands], key="album_brand")

        selected_items = filter_media(
            all_media,
            category=album_category,
            section=album_section,
            brand=album_brand,
        )

        title_text = f"Blancos Primavera | Album {album_name.strip() or 'Sin nombre'}"
        context_text = f"Categoria={album_category} | Seccion={album_section} | Marca={album_brand}"
    else:
        options = {
            f"{item['original_name']} ({item['category']}/{item['section']}/{item['brand']})": item
            for item in all_media
        }
        selected_labels = st.multiselect("Selecciona archivos", options=list(options.keys()))
        selected_items = [options[label] for label in selected_labels]
        title_text = "Blancos Primavera | Seleccion de archivos"
        context_text = "Seleccion manual de archivos"

    st.caption(f"Archivos seleccionados: {len(selected_items)}")

    send_bootstrap_mode = st.radio(
        "Inicio de envio",
        options=[
            "Plantilla + mensaje + catalogos",
            "Solo catalogos (sin plantilla)",
            "Solo mensaje + catalogos (sin plantilla)",
        ],
        horizontal=False,
    )

    st.info(
        "Sin plantilla solo funciona si el chat esta dentro de la ventana de 24h. "
        "Si esta fuera de ventana, WhatsApp exige plantilla."
    )

    destination = st.text_input("Numero destino (E.164 sin +)", placeholder="5215512345678")

    if st.button("Generar resumen"):
        st.session_state["wa_message"] = build_summary(selected_items, title_text, context_text)

    message_text = st.text_area(
        "Mensaje",
        key="wa_message",
        height=220,
        placeholder="Resumen multimedia para cliente",
    )

    if st.button("Enviar por WhatsApp", type="primary", use_container_width=True):
        if not selected_items:
            st.error("Selecciona al menos un archivo")
        elif not destination.strip():
            st.error("Ingresa numero destino")
        else:
            cfg_now = load_wa_config()
            try:
                ack_summary = "Sin mensaje inicial"

                with st.spinner("Enviando por WhatsApp..."):
                    if send_bootstrap_mode == "Plantilla + mensaje + catalogos":
                        ack = send_template_and_text(cfg_now, destination, message_text)
                        ack_summary = (
                            f"Template ID: {ack['template_message_id']} | "
                            f"Texto ID: {ack['text_message_id']}"
                        )
                    elif send_bootstrap_mode == "Solo mensaje + catalogos (sin plantilla)":
                        text_message_id = send_text_only(cfg_now, destination, message_text)
                        ack_summary = f"Texto sin plantilla ID: {text_message_id}"
                    else:
                        # Solo catalogos: no se envia plantilla ni texto, solo archivos.
                        ack_summary = "Solo catalogos"

                    results: list[dict[str, str]] = []
                    progress = st.progress(0.0)
                    for idx, item in enumerate(selected_items):
                        try:
                            media_id = upload_media_to_whatsapp(cfg_now, item)
                            msg_id = send_media_message(cfg_now, destination, item, media_id)
                            results.append({
                                "nombre": item["original_name"],
                                "estado": "OK",
                                "detalle": msg_id,
                            })
                        except Exception as file_error:
                            results.append({
                                "nombre": item["original_name"],
                                "estado": "ERROR",
                                "detalle": str(file_error),
                            })
                        progress.progress((idx + 1) / len(selected_items))

                    ok_count = len([r for r in results if r["estado"] == "OK"])
                    bad_count = len([r for r in results if r["estado"] == "ERROR"])

                st.success(
                    f"Envio completado. {ack_summary} | "
                    f"Archivos OK: {ok_count}/{len(selected_items)}"
                )
                if bad_count:
                    st.warning(f"Archivos con error: {bad_count}")

                for row in results:
                    if row["estado"] == "OK":
                        st.success(f"{row['nombre']}: {row['detalle']}")
                    else:
                        st.error(f"{row['nombre']}: {row['detalle']}")
            except Exception as send_error:
                error_text = str(send_error)
                st.error(error_text)
                if "code=131" in error_text or "plantilla" in error_text.lower() or "window" in error_text.lower():
                    st.warning(
                        "WhatsApp probablemente bloqueo el envio sin plantilla por ventana de 24h. "
                        "Prueba el modo 'Plantilla + mensaje + catalogos'."
                    )

with tab_info:
    st.subheader("Informacion de la plataforma")
    st.markdown(
        """
### Arquitectura unificada
- Una sola app Streamlit
- Base de datos SQLite para metadata
- Almacenamiento local para archivos
- Envio WhatsApp directo usando media_id (sin URL publica)

### Rutas locales
"""
    )
    st.code(f"DB: {DB_PATH}\nUploads: {UPLOAD_FOLDER}")

    st.markdown(
        """
### Notas de persistencia en Streamlit Cloud
- SQLite y archivos pueden perderse si el contenedor se reinicia o se redeploya.
- Para persistencia fuerte en produccion: usar S3/Cloudinary para archivos y Postgres para metadata.
- La app actual ya queda funcional en una sola pieza para operar sin React + servidor aparte.
"""
    )

    st.markdown("---")
    st.write("Blancos Primavera | Streamlit unificado | 2026")
