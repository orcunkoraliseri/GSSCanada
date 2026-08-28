"""`EU-08` driver — the GSSCanada 4J half of the European Step 8 campaign.

MVP §9.4 splits the work: OpenUBEM owns the engine (`run_campaign_cell`, the IDF, EnergyPlus),
and this side owns the loop — which cells, in what order, with what concurrency, and the proof
that the campaign as a whole read what it claims to have read.

This driver deliberately owns NO physics.  It calls `openubem.campaign.eu_cell_runner`
`run_campaign_cell` once per cell, passing every identity-bearing input explicitly, and refuses
to start at all if any of them is not what the ruled documents say it must be.

Six preflight refusals, none downgradeable and each one seen failing before this was trusted:

  D1  campaign spec digest mismatch          (the frozen `v1.1`, `16d3fbd6...`)
  D2  chaining-closure notice digest mismatch (the `f>0` lift authority, `058c9d13...`)
  D3  EnergyPlus version mismatch             (the IDF declares 23.1; a 24.2 run would write
                                               `energyplus_version: 23.1` into 510 false manifests)
  D4  binding artefact digest / fold coverage (`eu_cell_presence_binding_v2.json`)
  D5  cell count is not exactly 510
  D6  the run order is not deterministic

`D3` is the one that is easy to miss and impossible to see afterwards: `run_campaign_cell`
hardcodes `energyplus_version` in the manifest, so the manifest cannot disagree with the binary.
The only place that mismatch is visible is here, before the run.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path

OPENUBEM_ROOT = Path(os.environ.get("OPENUBEM_ROOT", r"C:/Users/o_iseri/Desktop/OpenUBEM"))
FOURJ_ROOT = Path(__file__).resolve().parents[1]

SPEC_REL = "openubem/data/campaign/eu_campaign_cell_spec_v1.1.json"
SPEC_SHA256 = "16d3fbd62a9f79265c08c5746bbc70f5130cd30cb673c1a68c74755c79aa65f6"

BINDING_PATH = FOURJ_ROOT / "Step10_docs/outputs_step10/eu_cell_presence_binding_v2.json"
BINDING_SHA256 = "8f94165dab807c5aa74d932492a39db01e1b571d0079559b9ab21541b6371c99"

NOTICE_PATH = FOURJ_ROOT / "Step10_docs/docs/2026-08-26_10.1_chaining-closure-notice.md"
NOTICE_SHA256 = "058c9d132d49db5fca15f2fa3b8d0a161cc947d27559b36fde6233b4a89d74c6"

SCHEDULES_ROOT = FOURJ_ROOT / "Step7_docs/outputs_step7/schedules"

RUNNER_REL = "openubem/campaign/eu_cell_runner.py"
RUNNER_SHA256 = "82eb7cf252fcf4a83390cf4506cfda80c0d21ce535d41dd2dffd7ab22169beb6"

REQUIRED_EP_VERSION = "23.1"
EXPECTED_N_CELLS = 510
EXPECTED_PER_FOLD = {"es": 120, "uk": 180, "it": 210}
EXPECTED_F_LEVELS = [0.0, 0.15, 0.3, 0.5, 1.0]

# Markers of a diverging heat balance in eplusout.err. EnergyPlus reports these as WARNINGS on a
# run it still calls successful, so a completed cell carrying one has a heating figure that means
# nothing. Screened by the driver because no gate downstream of it can see them.
UNSTABLE_MARKERS = (
    "Temperature out of range",
    "CalcHeatBalanceInsideSurf",
    "Inside surface heat balance did not converge",
    "Zone Air Heat Balance did not converge",
)


class PreflightError(RuntimeError):
    """A refusal raised before any cell is built.  Never downgraded to a warning."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def energyplus_version(energyplus_exe: Path) -> str:
    """Return the running EnergyPlus version, e.g. `23.1.0-87ed9199d4`."""
    out = subprocess.run(
        [str(energyplus_exe), "--version"], capture_output=True, text=True, timeout=60
    )
    text = (out.stdout or "") + (out.stderr or "")
    match = re.search(r"Version\s+(\S+)", text)
    if not match:
        raise PreflightError(f"D3: could not read a version from {energyplus_exe}: {text!r}")
    return match.group(1)


def preflight(run_root: Path, dry_run: bool, workers: int) -> dict:
    """Every refusal that must happen before a single cell is built."""
    spec_path = OPENUBEM_ROOT / SPEC_REL
    if not spec_path.exists():
        raise PreflightError(f"D1: campaign spec not found: {spec_path}")
    actual_spec = sha256_file(spec_path)
    if actual_spec != SPEC_SHA256:
        raise PreflightError(
            f"D1: campaign spec digest mismatch — ruled {SPEC_SHA256}, file {actual_spec}. "
            "The frozen spec is never amended in place; a change makes a new version, and this "
            "driver must be re-pinned to it deliberately."
        )

    runner_path = OPENUBEM_ROOT / RUNNER_REL
    actual_runner = sha256_file(runner_path) if runner_path.exists() else None

    if not NOTICE_PATH.exists():
        raise PreflightError(f"D2: the f>0 lift notice is missing: {NOTICE_PATH}")
    actual_notice = sha256_file(NOTICE_PATH)
    if actual_notice != NOTICE_SHA256:
        raise PreflightError(
            f"D2: f>0 lift notice digest mismatch — pinned {NOTICE_SHA256}, file {actual_notice}. "
            "The lift is carried by the notice's identity; an unpinned notice is not authority."
        )

    if not BINDING_PATH.exists():
        raise PreflightError(f"D4: binding artefact not found: {BINDING_PATH}")
    actual_binding = sha256_file(BINDING_PATH)
    if actual_binding != BINDING_SHA256:
        raise PreflightError(
            f"D4: binding digest mismatch — pinned {BINDING_SHA256}, file {actual_binding}."
        )
    binding = json.loads(BINDING_PATH.read_text(encoding="utf-8"))
    binding_spec = str(binding.get("spec", {}).get("sha256", ""))
    if binding_spec != SPEC_SHA256:
        raise PreflightError(
            f"D4: the binding pins spec {binding_spec} but this run executes {SPEC_SHA256}."
        )
    for fold in EXPECTED_PER_FOLD:
        if fold not in binding.get("folds", {}):
            raise PreflightError(f"D4: binding artefact carries no fold {fold!r}")

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    cells = spec["cells"]
    if len(cells) != EXPECTED_N_CELLS:
        raise PreflightError(f"D5: spec holds {len(cells)} cells, expected {EXPECTED_N_CELLS}")
    per_fold: dict[str, int] = {}
    for cell in cells:
        per_fold[cell["survey_fold"]] = per_fold.get(cell["survey_fold"], 0) + 1
    if per_fold != EXPECTED_PER_FOLD:
        raise PreflightError(f"D5: per-fold cell counts are {per_fold}, expected {EXPECTED_PER_FOLD}")
    levels = sorted({float(cell["sensitivity_f"]) for cell in cells})
    if levels != EXPECTED_F_LEVELS:
        raise PreflightError(f"D5: f levels are {levels}, expected {EXPECTED_F_LEVELS}")

    ordered = order_cells(cells)
    if [c["cell_id"] for c in ordered] != [c["cell_id"] for c in order_cells(list(reversed(cells)))]:
        raise PreflightError("D6: the run order is not deterministic under input permutation")
    if len({c["cell_id"] for c in ordered}) != EXPECTED_N_CELLS:
        raise PreflightError("D6: cell_id is not unique across the spec")

    # `openubem.config` reads ENERGYPLUS_PATH as a DIRECTORY (it appends `Energy+.idd`), while
    # `eu_cell_runner._run_energyplus` executes `str(ENERGYPLUS_PATH)` directly as the BINARY.
    # Both cannot be satisfied by one value, and the default is the directory, so an unprepared
    # non-dry run dies with `PermissionError: [WinError 5]` on every cell -- it tries to execute a
    # folder.  Reported to OpenUBEM; fixed here from the caller's side, without touching their
    # tree, by pointing ENERGYPLUS_PATH at the binary and the IDD at its own explicit variable.
    ep_root = Path(os.environ.get("OPENUBEM_ENERGYPLUS_ROOT", r"C:/EnergyPlusV23-1-0"))
    ep_exe = ep_root / "energyplus.exe"
    ep_idd = ep_root / "Energy+.idd"
    os.environ["ENERGYPLUS_PATH"] = str(ep_exe)
    os.environ["OPENUBEM_ENERGYPLUS_IDD_PATH"] = str(ep_idd)
    ep_version = None
    if not dry_run:
        if not ep_exe.exists():
            raise PreflightError(f"D3: EnergyPlus binary not found: {ep_exe}")
        if not ep_idd.exists():
            raise PreflightError(f"D3: EnergyPlus IDD not found: {ep_idd}")
        ep_version = energyplus_version(ep_exe)
        if not ep_version.startswith(REQUIRED_EP_VERSION):
            raise PreflightError(
                f"D3: EnergyPlus version mismatch — the campaign IDFs declare "
                f"Version {REQUIRED_EP_VERSION} and run_campaign_cell writes "
                f"energyplus_version={REQUIRED_EP_VERSION!r} into every manifest, but the binary "
                f"at {ep_exe} is {ep_version}. Running it would put a false version in all "
                f"{EXPECTED_N_CELLS} manifests and no downstream gate could see it."
            )

    run_root.mkdir(parents=True, exist_ok=True)
    return {
        "spec_path": str(spec_path),
        "spec_sha256": actual_spec,
        "runner_path": str(runner_path),
        "runner_sha256": actual_runner,
        "runner_sha256_expected": RUNNER_SHA256,
        "runner_sha256_matches_expected": actual_runner == RUNNER_SHA256,
        "binding_path": str(BINDING_PATH),
        "binding_sha256": actual_binding,
        "binding_spec_sha256": binding_spec,
        "notice_path": str(NOTICE_PATH),
        "notice_sha256": actual_notice,
        "schedules_root": str(SCHEDULES_ROOT),
        "n_cells": len(cells),
        "per_fold": per_fold,
        "f_levels": levels,
        "energyplus_exe": str(ep_exe),
        "energyplus_idd": str(ep_idd),
        "energyplus_version_measured": ep_version,
        "energyplus_version_required": REQUIRED_EP_VERSION,
        "dry_run": dry_run,
        "workers": workers,
        "run_root": str(run_root),
        "host": platform.node(),
        "python": sys.version.split()[0],
        "cells": cells,
    }


def order_cells(cells: list[dict]) -> list[dict]:
    """The declared run order: fold, then archetype, then `f` ascending.

    Declared rather than incidental, so a second implementation can reproduce it and a resumed
    or re-sharded run cannot silently reorder the campaign.  `f = 0` therefore always precedes
    its own `f > 0` cells, which is the order a control-versus-treatment reading wants.
    """
    fold_rank = {"es": 0, "uk": 1, "it": 2}
    return sorted(
        cells,
        key=lambda c: (
            fold_rank.get(str(c["survey_fold"]), 99),
            str(c["archetype_id"]),
            float(c["sensitivity_f"]),
        ),
    )


def _run_one(payload: dict) -> dict:
    """Worker body.  Imports inside the process so Windows `spawn` starts cleanly."""
    sys.path.insert(0, payload["openubem_root"])
    started = time.time()
    try:
        from openubem.campaign.eu_cell_runner import run_campaign_cell

        manifest = run_campaign_cell(
            payload["cell"],
            spec_path=Path(payload["spec_path"]),
            spec_sha256=payload["spec_sha256"],
            binding_path=Path(payload["binding_path"]),
            chaining_notice_path=Path(payload["notice_path"]),
            schedules_root=Path(payload["schedules_root"]),
            chaining_notice_sha256=payload["notice_sha256"],
            run_root=Path(payload["run_root"]),
            dry_run=payload["dry_run"],
            energyplus_timeout=payload["energyplus_timeout"],
        )
        # `run_campaign_cell` returns a manifest even when EnergyPlus itself terminated: the
        # manifest is a record of what was read, not a claim that the simulation converged.
        # A cell that halted on a fatal error still has a manifest, a return code of 1 and a
        # null `heating_kwh`, so counting it as OK would put a fatal into the completed column
        # where no downstream reader could see it.  It is classified here, not downstream.
        # The runner now states this itself (`completed` / `completion_status`, added after this
        # driver reported the ambiguity).  Prefer its own word; keep the local derivation as the
        # fallback so the driver still classifies correctly against an older runner.
        if "completed" in manifest:
            engine_failed = payload["dry_run"] is False and not manifest["completed"]
        else:
            engine_failed = (
                payload["dry_run"] is False
                and (
                    manifest.get("return_code") not in (0, None)
                    or (manifest.get("fatal_count") or 0) > 0
                    or manifest.get("heating_kwh") is None
                )
            )
        # A cell can finish with return code 0 and still be numerically meaningless: EnergyPlus
        # reports a diverging heat balance as a WARNING (`Temperature out of range ...
        # (PsyPsatFnTemp)`), and only escalates to a Severe when a surface temperature leaves the
        # solver's bounds entirely.  A run that lands just inside the bound is reported completed
        # and carries a heating figure that no downstream gate would question.  So `completed` is
        # necessary and not sufficient, and the `.err` is screened here rather than trusted.
        unstable = None
        if not payload["dry_run"]:
            err_path = Path(payload["run_root"]) / str(payload["cell"]["cell_id"]) / "eplusout.err"
            if err_path.exists():
                err_text = err_path.read_text(encoding="utf-8", errors="replace")
                unstable = any(marker in err_text for marker in UNSTABLE_MARKERS)
        return {
            "cell_id": payload["cell"]["cell_id"],
            "rank": payload["rank"],
            "status": "ENGINE_FAILED" if engine_failed else "OK",
            "unstable_solution": unstable,
            "wall_s": round(time.time() - started, 3),
            "manifest_path": manifest.get("manifest_path"),
            "heating_kwh": manifest.get("heating_kwh"),
            "severe_count": manifest.get("severe_count"),
            "fatal_count": manifest.get("fatal_count"),
            "return_code": manifest.get("return_code"),
            "presence_hid": manifest.get("presence_hid"),
            "presence_sha256": manifest.get("presence_sha256"),
            "binding_spec_digest_accepted_by": manifest.get("binding_spec_digest_accepted_by"),
        }
    except Exception as exc:  # a refusal is data, not a crash of the campaign
        return {
            "cell_id": payload["cell"]["cell_id"],
            "rank": payload["rank"],
            "status": "REFUSED",
            "wall_s": round(time.time() - started, 3),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc(limit=4),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="EU-08 campaign driver (510 cells)")
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0, help="run only the first N cells (smoke)")
    parser.add_argument("--cells", default="", help="path to a newline-separated cell_id list; run only those cells (FINDING 181 diagnostic). The order rule is unchanged.")
    parser.add_argument("--energyplus-timeout", type=int, default=900)
    parser.add_argument("--progress-every", type=int, default=10)
    args = parser.parse_args()

    run_root = Path(args.run_root)
    info = preflight(run_root, args.dry_run, args.workers)
    cells = order_cells(info.pop("cells"))
    if args.limit:
        cells = cells[: args.limit]
    if args.cells:
        wanted = {ln.strip() for ln in Path(args.cells).read_text(encoding="utf-8").splitlines() if ln.strip()}
        cells = [c for c in cells if c["cell_id"] in wanted]
        missing = wanted - {c["cell_id"] for c in cells}
        if missing:
            raise SystemExit(f"--cells: {len(missing)} ids are not in the design, e.g. {sorted(missing)[:3]}")
        print(f"[preflight] --cells subset: {len(cells)} of {len(wanted)} requested")

    print(f"[preflight] OK — {len(cells)} cells, dry_run={args.dry_run}, workers={args.workers}")
    print(f"[preflight] spec {info['spec_sha256'][:12]}...  binding {info['binding_sha256'][:12]}...  "
          f"notice {info['notice_sha256'][:12]}...")
    print(f"[preflight] energyplus {info['energyplus_version_measured']} "
          f"(required {REQUIRED_EP_VERSION}.x)")
    sys.stdout.flush()

    payloads = [
        {
            "cell": cell,
            "rank": rank,
            "openubem_root": str(OPENUBEM_ROOT),
            "spec_path": info["spec_path"],
            "spec_sha256": info["spec_sha256"],
            "binding_path": info["binding_path"],
            "notice_path": info["notice_path"],
            "notice_sha256": info["notice_sha256"],
            "schedules_root": info["schedules_root"],
            "run_root": str(run_root),
            "dry_run": args.dry_run,
            "energyplus_timeout": args.energyplus_timeout,
        }
        for rank, cell in enumerate(cells)
    ]

    started = time.time()
    results: list[dict] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        for done, result in enumerate(pool.map(_run_one, payloads), start=1):
            results.append(result)
            if done % args.progress_every == 0 or done == len(payloads):
                ok = sum(1 for r in results if r["status"] == "OK")
                bad = done - ok
                print(f"[{done}/{len(payloads)}] ok={ok} not_completed={bad} "
                      f"elapsed={round(time.time() - started, 1)}s")
                sys.stdout.flush()

    results.sort(key=lambda r: r["rank"])
    ok = [r for r in results if r["status"] == "OK"]
    refused = [r for r in results if r["status"] == "REFUSED"]
    engine_failed = [r for r in results if r["status"] == "ENGINE_FAILED"]
    summary = {
        "campaign": "EU-08",
        "run_order_rule": "survey_fold (es,uk,it), then archetype_id, then sensitivity_f ascending",
        "n_submitted": len(results),
        "n_ok": len(ok),
        "n_refused": len(refused),
        "n_engine_failed": len(engine_failed),
        "n_completed_but_unstable": sum(1 for r in ok if r.get("unstable_solution")),
        "n_completed_and_stable": sum(1 for r in ok if r.get("unstable_solution") is False),
        "unstable_cells": [r["cell_id"] for r in ok if r.get("unstable_solution")],
        "status_note": (
            "REFUSED = the cell never built (a guard fired, in this driver or in the runner). "
            "ENGINE_FAILED = the cell built and EnergyPlus terminated on a fatal error, so a "
            "manifest exists but no heating result does. Neither is a completed cell."
        ),
        "wall_s": round(time.time() - started, 1),
        "refusals": [
            {k: r[k] for k in ("cell_id", "rank", "error_type", "error")} for r in refused
        ],
        "engine_failures": [
            {k: r.get(k) for k in ("cell_id", "rank", "return_code", "severe_count", "fatal_count")}
            for r in engine_failed
        ],
        "results": results,
        **info,
    }
    out = run_root / ("campaign_summary_dryrun.json" if args.dry_run else "campaign_summary.json")
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\n[done] completed={len(ok)} refused={len(refused)} "
          f"engine_failed={len(engine_failed)} in {summary['wall_s']}s")
    print(f"[done] summary -> {out}")
    return 0 if not (refused or engine_failed) else 2


if __name__ == "__main__":
    raise SystemExit(main())
