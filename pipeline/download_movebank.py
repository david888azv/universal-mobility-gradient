#!/usr/bin/env python3
# =============================================================================
# Author:      David L. Azevedo
# Affiliation: Instituto de Física, Universidade de Brasília (UnB), Brazil
# E-mail:      david888azv@unb.br
# ORCID:       0000-0002-3456-554X
# Project:     Universal Phenomenology, Divergent Mechanism — A Behavioural
#              Gradient of Mobility from Foraging to Commute
#              (Azevedo 2026, submitted to Nature)
# Repository:  https://github.com/david888azv/universal-mobility-gradient
# Licence:     CC BY 4.0
# =============================================================================

"""
download_movebank.py — fetch GPS tracks from Movebank with license/size check.

The Movebank REST API returns event tables as CSV. License-controlled studies
require the caller to accept the licence once (by sending its MD5 hash on the
following request). This script wraps that flow and adds:

  * credential loading from env vars or ~/.movebank_credentials
  * a curated CANDIDATES table for the species we want to add to the
    universal-mobility-gradient analysis
  * --search        : list public studies matching a species name
  * --probe         : per-study metadata + license terms + size estimate (MB)
  * --download      : interactive confirmation, then chunked CSV download
  * resilient retries on 5xx / network errors

Examples
--------
    # see the curated candidate list
    python download_movebank.py --list-candidates

    # search Movebank for studies of a given species
    python download_movebank.py --search "Procapra gutturosa"

    # probe specific study IDs (no download — just metadata + size)
    python download_movebank.py --probe 1172256099 1109031555

    # actually download (asks for confirmation before each)
    python download_movebank.py --download 1172256099 --out ../data_raw

    # MDR (Data Repository) DOI — uses public DSpace API, no auth needed
    python download_movebank.py --mdr 10.5441/001/1.f3550b4f --out ../data_raw

Credentials
-----------
Provide credentials in one of:
  * env vars MOVEBANK_USER and MOVEBANK_PASS
  * file ~/.movebank_credentials (line 1 = user, line 2 = password, chmod 600)

Sign up for a free Movebank account at https://www.movebank.org/

The --mdr mode does NOT require credentials — it fetches CC0/CC-BY items
from the Movebank Data Repository via its public DSpace 7 REST API.
"""

from __future__ import annotations

import argparse
import csv
import getpass
import hashlib
import io
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    sys.exit("This script needs the 'requests' package: pip install requests")


MOVEBANK_BASE = "https://www.movebank.org/movebank/service/direct-read"
MDR_BASE = "https://datarepository.movebank.org"
DEFAULT_TIMEOUT = 60
CHUNK_BYTES = 1024 * 256  # 256 kB chunks for streaming downloads
ESTIMATED_BYTES_PER_EVENT = 90  # empirical rough average for a Movebank CSV row


# ---------------------------------------------------------------------------
# Curated candidate species for the universal-mobility-gradient extension
#
# NOTE: study_id is intentionally None for entries the maintainer should
# resolve interactively via `--search` and confirm before downloading.
# Movebank study IDs change over time and licence terms vary per study, so
# any hard-coded ID would risk getting stale; the search step is the source
# of truth.
# ---------------------------------------------------------------------------
CANDIDATES = {
    "gazelle": {
        "common": "Mongolian gazelle",
        "latin":  "Procapra gutturosa",
        "search": "Procapra gutturosa",
        "role":   "low γ_CP — nomadic ungulate",
        "study_id": None,
    },
    "bat": {
        "common": "Egyptian fruit bat",
        "latin":  "Rousettus aegyptiacus",
        "search": "Rousettus aegyptiacus",
        "role":   "high γ_CP — extreme central-place forager",
        "study_id": None,
    },
    "albatross": {
        "common": "Wandering albatross",
        "latin":  "Diomedea exulans",
        "search": "Diomedea exulans",
        "role":   "ocean-scale marine forager",
        "study_id": None,
    },
    "zebra": {
        "common": "Plains zebra",
        "latin":  "Equus quagga",
        "search": "Equus quagga",
        "role":   "terrestrial migratory ungulate",
        "study_id": None,
    },
    "turtle": {
        "common": "Loggerhead sea turtle",
        "latin":  "Caretta caretta",
        "search": "Caretta caretta",
        "role":   "ocean-scale reptile",
        "study_id": None,
    },
}


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------
def load_credentials() -> Tuple[str, str]:
    user = os.environ.get("MOVEBANK_USER")
    pwd  = os.environ.get("MOVEBANK_PASS")
    if user and pwd:
        return user, pwd

    cred_file = Path.home() / ".movebank_credentials"
    if cred_file.exists():
        lines = [l.strip() for l in cred_file.read_text().splitlines() if l.strip()]
        if len(lines) >= 2:
            return lines[0], lines[1]

    print("Movebank credentials not found in env or ~/.movebank_credentials.",
          file=sys.stderr)
    user = input("Movebank username: ").strip()
    pwd  = getpass.getpass("Movebank password: ")
    return user, pwd


# ---------------------------------------------------------------------------
# Low-level API helpers
# ---------------------------------------------------------------------------
@dataclass
class StudyMeta:
    study_id: int
    name: str
    species: str
    license_type: str
    license_terms: str
    number_of_events: Optional[int]
    timestamp_first: Optional[str]
    timestamp_last: Optional[str]
    raw: Dict

    @property
    def estimated_mb(self) -> Optional[float]:
        if self.number_of_events is None:
            return None
        return self.number_of_events * ESTIMATED_BYTES_PER_EVENT / (1024 * 1024)


def _request(session: requests.Session, params: Dict[str, str],
             stream: bool = False, retries: int = 3) -> requests.Response:
    last_exc = None
    for attempt in range(retries):
        try:
            r = session.get(MOVEBANK_BASE, params=params, stream=stream,
                            timeout=DEFAULT_TIMEOUT)
            if r.status_code in (500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            return r
        except requests.exceptions.RequestException as exc:
            last_exc = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Movebank request failed after {retries} retries: {last_exc}")


def _parse_csv(text: str) -> List[Dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def fetch_study_metadata(session: requests.Session, study_id: int) -> StudyMeta:
    """Get the study row from Movebank; works for any study you can see."""
    params = {"entity_type": "study", "study_id": str(study_id)}
    r = _request(session, params)
    if r.status_code != 200:
        raise RuntimeError(f"study {study_id}: HTTP {r.status_code} — {r.text[:400]}")
    rows = _parse_csv(r.text)
    if not rows:
        raise RuntimeError(f"study {study_id}: empty metadata response")
    row = rows[0]

    return StudyMeta(
        study_id        = int(row.get("id", study_id) or study_id),
        name            = row.get("name", "") or "",
        species         = row.get("taxon_ids", "") or row.get("main_location_lat_long", "") or "",
        license_type    = row.get("license_type", "") or "",
        license_terms   = row.get("license_terms", "") or "",
        number_of_events= int(row["number_of_deployed_locations"]) if row.get("number_of_deployed_locations", "").isdigit() else None,
        timestamp_first = row.get("timestamp_first_deployed_location", None),
        timestamp_last  = row.get("timestamp_last_deployed_location", None),
        raw             = row,
    )


def search_studies(session: requests.Session, term: str) -> List[Dict[str, str]]:
    """Best-effort search — Movebank has no direct search endpoint, so we
    pull the studies index and filter client-side. The full index is large
    (~MB); cached on first call within the same process."""
    if not hasattr(search_studies, "_cache"):
        params = {"entity_type": "study"}
        r = _request(session, params)
        r.raise_for_status()
        search_studies._cache = _parse_csv(r.text)
    term_l = term.lower()
    hits = []
    for row in search_studies._cache:
        haystack = " ".join([
            row.get("name", "") or "",
            row.get("taxon_ids", "") or "",
            row.get("study_objective", "") or "",
        ]).lower()
        if term_l in haystack:
            hits.append(row)
    return hits


def accept_license_and_download(session: requests.Session, study_id: int,
                                out_path: Path) -> None:
    """Stream events CSV; if licence acceptance is required, compute MD5 of
    the licence text Movebank returns and re-issue the request with that
    parameter, then save to disk in chunks."""
    params = {"entity_type": "event", "study_id": str(study_id)}

    # First request — may return either CSV or licence-acceptance instructions
    r = _request(session, params, stream=True)
    if r.status_code != 200:
        raise RuntimeError(f"study {study_id}: HTTP {r.status_code} — {r.text[:400]}")

    head = r.raw.read(4096, decode_content=True)
    looks_like_license = (b"License Terms:" in head) or (b"By accepting this licence" in head)

    if looks_like_license:
        # Read full text, compute MD5, re-request with license-md5
        rest = r.raw.read(decode_content=True)
        license_text = (head + rest).decode("utf-8", errors="replace")
        # Movebank's instructions: hash the licence string verbatim
        md5 = hashlib.md5(license_text.encode("utf-8")).hexdigest()
        print(f"[license] study {study_id} requires acceptance.")
        print("---- terms (first 800 chars) ----")
        print(license_text[:800])
        print("---- end ----")
        ans = input(f"Accept licence for study {study_id}? [y/N] ").strip().lower()
        if ans != "y":
            raise RuntimeError("licence not accepted; aborting download")

        params["license-md5"] = md5
        r = _request(session, params, stream=True)
        if r.status_code != 200:
            raise RuntimeError(f"study {study_id}: HTTP {r.status_code} after licence — {r.text[:400]}")
        head = b""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with out_path.open("wb") as fh:
        if head:
            fh.write(head)
            total += len(head)
        for chunk in r.iter_content(chunk_size=CHUNK_BYTES):
            if chunk:
                fh.write(chunk)
                total += len(chunk)
                if total // (1024 * 1024) != (total - len(chunk)) // (1024 * 1024):
                    print(f"  ...{total / (1024*1024):.1f} MB", end="\r", flush=True)
    print(f"  ...{total / (1024*1024):.1f} MB written -> {out_path}")


# ---------------------------------------------------------------------------
# Movebank Data Repository (DSpace 7) — public, no-auth path
# ---------------------------------------------------------------------------
def mdr_resolve_doi(doi: str) -> Tuple[str, str]:
    """Resolve a Movebank DOI to (item_uuid, handle) via the DSpace REST API.

    `doi` may be passed as `10.5441/001/1.f3550b4f` or with a leading
    `doi:` / `https://doi.org/` — they are all normalised."""
    doi = doi.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix):]
    # DSpace's full-text search indexes the DOI string directly; using
    # a `doi:` prefix tries to interpret it as a fielded query and misses.
    url = f"{MDR_BASE}/server/api/discover/search/objects"
    r = requests.get(url, params={"query": doi}, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    objs = (data.get("_embedded", {})
                .get("searchResult", {})
                .get("_embedded", {})
                .get("objects", []))
    if not objs:
        raise RuntimeError(f"DOI {doi} not found in MDR")
    item = objs[0].get("_embedded", {}).get("indexableObject", {})
    uuid   = item.get("uuid", "")
    handle = item.get("handle", "")
    if not uuid:
        raise RuntimeError(f"DOI {doi} resolved but no UUID returned")
    return uuid, handle


def mdr_list_bitstreams(uuid: str) -> List[Dict]:
    """Return [{'name':..., 'sizeBytes':..., 'href':..., 'mimetype':...}, ...]
    for every downloadable file of the item."""
    url = f"{MDR_BASE}/server/api/core/items/{uuid}/bundles"
    r = requests.get(url, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    bundles = r.json().get("_embedded", {}).get("bundles", [])
    out = []
    for b in bundles:
        if b.get("name") not in ("ORIGINAL", None):
            continue
        bs_url = b.get("_links", {}).get("bitstreams", {}).get("href", "")
        if not bs_url:
            continue
        rb = requests.get(bs_url, params={"size": 200}, timeout=DEFAULT_TIMEOUT)
        rb.raise_for_status()
        for bs in rb.json().get("_embedded", {}).get("bitstreams", []):
            content = bs.get("_links", {}).get("content", {}).get("href", "")
            out.append({
                "name":      bs.get("name", ""),
                "sizeBytes": bs.get("sizeBytes", 0),
                "href":      content,
                "mimetype":  bs.get("metadata", {})
                              .get("dc.format.mimetype", [{}])[0].get("value", ""),
            })
    return out


def mdr_probe(doi: str) -> Dict:
    """One-shot: DOI → list of downloadable bitstreams with sizes."""
    uuid, handle = mdr_resolve_doi(doi)
    bs = mdr_list_bitstreams(uuid)
    total = sum(b["sizeBytes"] for b in bs)
    return {"doi": doi, "uuid": uuid, "handle": handle,
            "bitstreams": bs, "total_bytes": total}


def _is_acc_file(name: str) -> bool:
    """Heuristic: skip files that are clearly accelerometer-only ACC tracks."""
    n = name.lower()
    return ("-acc" in n) or n.endswith("acc.csv") or "acceleration" in n


def mdr_download(doi: str, out_dir: Path, gps_only: bool = False) -> List[Path]:
    """Download every bitstream of the MDR item under `out_dir/<doi-safe>/`.
    With gps_only=True, skip accelerometer-only files (huge & unused here)."""
    info = mdr_probe(doi)
    safe = doi.replace("/", "_").replace(":", "_")
    target_dir = out_dir / safe
    target_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for bs in info["bitstreams"]:
        if not bs["href"]:
            continue
        if gps_only and _is_acc_file(bs["name"]):
            print(f"  ~~ skip ACC: {bs['name']} ({bs['sizeBytes']/1024/1024:.1f} MB)")
            continue
        out_path = target_dir / bs["name"]
        print(f"  -> {bs['name']} ({bs['sizeBytes']/1024/1024:.1f} MB)")
        with requests.get(bs["href"], stream=True, timeout=DEFAULT_TIMEOUT) as r:
            r.raise_for_status()
            written = 0
            with out_path.open("wb") as fh:
                for chunk in r.iter_content(chunk_size=CHUNK_BYTES):
                    if chunk:
                        fh.write(chunk)
                        written += len(chunk)
        paths.append(out_path)
    return paths


# ---------------------------------------------------------------------------
# Pretty printing
# ---------------------------------------------------------------------------
def fmt_meta_table(metas: List[StudyMeta]) -> str:
    lines = []
    lines.append(f"{'study_id':>10}  {'license':<20}  {'events':>10}  {'≈MB':>7}  name")
    lines.append("-" * 100)
    for m in metas:
        ev = "?" if m.number_of_events is None else f"{m.number_of_events:,}"
        mb = "?" if m.estimated_mb is None else f"{m.estimated_mb:7.1f}"
        lines.append(f"{m.study_id:>10}  {m.license_type[:20]:<20}  {ev:>10}  {mb:>7}  {m.name[:60]}")
    return "\n".join(lines)


def list_candidates() -> None:
    print(f"{'key':<10}  {'common name':<28}  {'role':<40}  status")
    print("-" * 100)
    for k, v in CANDIDATES.items():
        sid = v["study_id"] or "(resolve via --search)"
        print(f"{k:<10}  {v['common']:<28}  {v['role']:<40}  {sid}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list-candidates", action="store_true",
                   help="print the curated candidate species list")
    g.add_argument("--search", metavar="TERM",
                   help="search Movebank study index for TERM (species name etc.)")
    g.add_argument("--probe", nargs="+", metavar="STUDY_ID", type=int,
                   help="fetch metadata + size estimate for one or more study IDs")
    g.add_argument("--download", nargs="+", metavar="STUDY_ID", type=int,
                   help="download events CSV for one or more study IDs")
    g.add_argument("--mdr", nargs="+", metavar="DOI",
                   help="download MDR (Data Repository) items by DOI — no auth needed")
    g.add_argument("--mdr-probe", nargs="+", metavar="DOI",
                   help="probe MDR DOIs: list bitstreams + sizes, no download")
    ap.add_argument("--out", default="../data_raw",
                    help="output directory for downloads (default: ../data_raw)")
    ap.add_argument("--yes", action="store_true",
                    help="skip per-study confirmation in --download / --mdr mode")
    ap.add_argument("--gps-only", action="store_true",
                    help="MDR mode: skip accelerometer-only files (saves GB)")
    args = ap.parse_args()

    if args.list_candidates:
        list_candidates()
        return 0

    # MDR probe / download — no credentials needed
    if args.mdr_probe:
        for doi in args.mdr_probe:
            try:
                info = mdr_probe(doi)
            except Exception as exc:
                print(f"  {doi}: {exc}", file=sys.stderr); continue
            print(f"\nDOI {info['doi']}  (handle {info['handle']})")
            for b in info["bitstreams"]:
                print(f"   {b['sizeBytes']/1024/1024:>7.2f} MB  {b['name']}")
            print(f"   {'─'*40}\n   {info['total_bytes']/1024/1024:>7.2f} MB  TOTAL")
        return 0

    if args.mdr:
        out_dir = Path(args.out).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        # show sizes first
        infos = []
        for doi in args.mdr:
            try:
                infos.append(mdr_probe(doi))
            except Exception as exc:
                print(f"  {doi}: probe failed: {exc}", file=sys.stderr)
        if not infos:
            return 2
        grand = sum(i["total_bytes"] for i in infos)
        print("Queued for MDR download:")
        for i in infos:
            print(f"  {i['total_bytes']/1024/1024:>8.2f} MB  {i['doi']}")
        print(f"  {'─'*40}\n  {grand/1024/1024:>8.2f} MB  TOTAL")
        if not args.yes:
            ans = input("\nProceed? [y/N] ").strip().lower()
            if ans != "y":
                print("aborted."); return 0
        for i in infos:
            print(f"\n[{i['doi']}]")
            try:
                mdr_download(i["doi"], out_dir, gps_only=args.gps_only)
            except Exception as exc:
                print(f"  FAILED: {exc}", file=sys.stderr)
        print("\nDone.")
        return 0

    user, pwd = load_credentials()
    session = requests.Session()
    session.auth = (user, pwd)

    if args.search:
        try:
            hits = search_studies(session, args.search)
        except Exception as exc:
            print(f"search failed: {exc}", file=sys.stderr)
            return 2
        print(f"{len(hits)} study/studies match '{args.search}':\n")
        print(f"{'id':>10}  {'license':<20}  name")
        print("-" * 100)
        for r in hits:
            print(f"{(r.get('id') or ''):>10}  {(r.get('license_type') or '')[:20]:<20}  {(r.get('name') or '')[:70]}")
        return 0

    if args.probe:
        metas = []
        for sid in args.probe:
            try:
                metas.append(fetch_study_metadata(session, sid))
            except Exception as exc:
                print(f"  study {sid}: {exc}", file=sys.stderr)
        print(fmt_meta_table(metas))
        for m in metas:
            if m.license_terms:
                print(f"\n--- licence terms (study {m.study_id}, type={m.license_type}) ---")
                print(m.license_terms[:800])
        return 0

    # --download
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    metas = []
    for sid in args.download:
        try:
            metas.append(fetch_study_metadata(session, sid))
        except Exception as exc:
            print(f"  study {sid}: metadata fetch failed: {exc}", file=sys.stderr)
    if not metas:
        return 2
    print("Studies queued for download:")
    print(fmt_meta_table(metas))

    if not args.yes:
        ans = input("\nProceed with download of all the above? [y/N] ").strip().lower()
        if ans != "y":
            print("aborted.")
            return 0

    for m in metas:
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in m.name)[:60] or f"study_{m.study_id}"
        out_path = out_dir / f"{m.study_id}_{safe_name}.csv"
        print(f"\n[study {m.study_id}] {m.name}")
        print(f"  license: {m.license_type}")
        print(f"  ≈ size : {m.estimated_mb:.1f} MB" if m.estimated_mb else "  ≈ size : unknown")
        try:
            accept_license_and_download(session, m.study_id, out_path)
        except Exception as exc:
            print(f"  FAILED: {exc}", file=sys.stderr)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
