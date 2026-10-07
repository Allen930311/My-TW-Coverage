#!/usr/bin/env python3
"""Incremental event census for Taiwan coverage.

R0 is deliberately read-only: it discovers affected tickers and recommended
refresh actions. It never rewrites Pilot_Reports by itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "freshness" / "source_registry.json"
TZ = ZoneInfo("Asia/Taipei")
USER_AGENT = "AllenCoverageFreshness/0.1 (source-census; contact via GitHub Allen930311)"


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def source(registry: dict[str, Any], source_id: str) -> dict[str, Any]:
    for item in registry["sources"]:
        if item["id"] == source_id:
            return item
    raise KeyError(f"source not registered: {source_id}")


def fetch_json(url: str) -> list[dict[str, Any]]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"expected JSON array from {url}")
    return payload


def normalized(record: dict[str, Any]) -> dict[str, Any]:
    return {str(key).strip(): value for key, value in record.items()}


def parse_roc_date(raw: Any) -> date | None:
    digits = "".join(ch for ch in str(raw or "") if ch.isdigit())
    if len(digits) != 7:
        return None
    year = int(digits[:3]) + 1911
    month = int(digits[3:5])
    day = int(digits[5:7])
    try:
        return date(year, month, day)
    except ValueError:
        return None


def parse_roc_month(raw: Any) -> str | None:
    digits = "".join(ch for ch in str(raw or "") if ch.isdigit())
    if len(digits) != 5:
        return None
    return f"{int(digits[:3]) + 1911:04d}-{digits[3:5]}"


def event_fingerprint(event: dict[str, Any]) -> str:
    stable = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


FINANCIAL_KEYWORDS = ("財務", "營收", "盈餘", "獲利", "財報", "會計", "股利")
SUPPLY_CHAIN_KEYWORDS = ("客戶", "供應", "合作", "策略聯盟", "產品", "產能", "訂單", "採購", "合約", "擴廠", "投資")


def actions_for_material_event(subject: str, detail: str) -> list[str]:
    text = f"{subject}\n{detail}"
    actions = {"revalidate_company_profile"}
    if any(keyword in text for keyword in FINANCIAL_KEYWORDS):
        actions.add("refresh_financials")
    if any(keyword in text for keyword in SUPPLY_CHAIN_KEYWORDS):
        actions.add("revalidate_supply_chain")
    return sorted(actions)


def material_events(registry: dict[str, Any], since: date) -> list[dict[str, Any]]:
    src = source(registry, "twse_material_events")
    rows = fetch_json(src["url"])
    events = []
    for raw in rows:
        row = normalized(raw)
        published = parse_roc_date(row.get("發言日期"))
        if not published or published < since:
            continue
        ticker = str(row.get("公司代號", "")).strip()
        if not ticker:
            continue
        subject = str(row.get("主旨", "")).strip()
        detail = str(row.get("說明", "")).strip()
        fact_date = parse_roc_date(row.get("事實發生日"))
        event = {
            "event_type": "material_event",
            "ticker": ticker,
            "company": str(row.get("公司名稱", "")).strip(),
            "published_at": published.isoformat(),
            "fact_date": fact_date.isoformat() if fact_date else None,
            "subject": subject,
            "source_id": src["id"],
            "actions": actions_for_material_event(subject, detail),
        }
        event["fingerprint"] = event_fingerprint(event)
        events.append(event)
    return events


def monthly_revenue_events(registry: dict[str, Any], since: date) -> list[dict[str, Any]]:
    src = source(registry, "mops_monthly_revenue_public")
    rows = fetch_json(src["url"])
    events = []
    for raw in rows:
        row = normalized(raw)
        released = parse_roc_date(row.get("出表日期"))
        if not released or released < since:
            continue
        ticker = str(row.get("公司代號", "")).strip()
        if not ticker:
            continue
        event = {
            "event_type": "monthly_revenue_batch",
            "ticker": ticker,
            "company": str(row.get("公司名稱", "")).strip(),
            "published_at": released.isoformat(),
            "period": parse_roc_month(row.get("資料年月")),
            "source_id": src["id"],
            "actions": ["refresh_monthly_revenue", "refresh_valuation_if_publishing"],
        }
        event["fingerprint"] = event_fingerprint(event)
        events.append(event)
    return events


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only incremental event census for My-TW-Coverage")
    parser.add_argument("--since", help="YYYY-MM-DD. Default: two calendar days ago in Asia/Taipei.")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args()

    now = datetime.now(TZ)
    since = date.fromisoformat(args.since) if args.since else (now.date() - timedelta(days=2))
    registry = load_registry()

    events: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    checked: list[str] = []
    for source_id, loader in (
        ("twse_material_events", material_events),
        ("mops_monthly_revenue_public", monthly_revenue_events),
    ):
        try:
            events.extend(loader(registry, since))
            checked.append(source_id)
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as exc:
            errors.append({"source_id": source_id, "error": str(exc)})

    deduped = {event["fingerprint"]: event for event in events}
    events = sorted(deduped.values(), key=lambda x: (x["published_at"], x["ticker"], x["event_type"], x["fingerprint"]))
    affected = sorted({event["ticker"] for event in events})

    payload = {
        "schema_version": "coverage-event-census-v1",
        "market": "TW",
        "generated_at": now.isoformat(),
        "since": since.isoformat(),
        "complete": not errors,
        "sources_checked": checked,
        "source_errors": errors,
        "affected_tickers": affected,
        "event_count": len(events),
        "events": events,
    }

    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return 0 if payload["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
