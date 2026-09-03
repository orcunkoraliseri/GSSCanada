"""2026-09-03_box5-6_scratch_perturbations.py -- perturbation checks for boxes 5/6 of the
no-core execution run-book (IMP/Prompt/4thJ_imp_nocore_execution_2026-09-03.md).

Four gate-design demonstrations on scratch fixtures only. No real manifest, cell, or campaign
artefact is read or written. Not a shipped tool -- kept as the record of the check.
"""

REQUIRED_FIELDS = [
    "weather_sha256", "energyplus_build_hash", "energyplus_version", "openubem_version",
    "openubem_git_commit", "platform", "rotated_to_midnight", "diary_origin_hour",
    "completed", "completion_status", "scheme", "status", "k", "observed_dwellings",
    "dwelling_deficit",
]


def g12_14_manifest_complete(manifest):
    missing = [f for f in REQUIRED_FIELDS if manifest.get(f) is None]
    return len(missing) == 0, missing


def check_g12_14():
    baseline = {f: "x" for f in REQUIRED_FIELDS}
    ok, missing = g12_14_manifest_complete(baseline)
    assert ok and not missing, "baseline should be clean: %r" % (missing,)
    felled = 0
    for field in REQUIRED_FIELDS:
        mutant = dict(baseline)
        mutant[field] = None
        ok, missing = g12_14_manifest_complete(mutant)
        if not ok and missing == [field]:
            felled += 1
    return felled, len(REQUIRED_FIELDS)


def g12_replicate_quotable(values, tol_pct):
    mean = sum(values) / len(values)
    worst_rel = max(abs(v - mean) / mean for v in values)
    return (worst_rel * 100.0) <= tol_pct, worst_rel * 100.0


def check_g12_replicate():
    clean = [100.0, 100.3, 99.8, 100.1, 99.9]
    quotable, worst = g12_replicate_quotable(clean, tol_pct=0.5)
    assert quotable, "clean control should be quotable, worst=%.4f%%" % worst
    outlier = [100.0, 100.3, 99.8, 100.1, 102.0]  # last value planted 2.0% off
    quotable_out, worst_out = g12_replicate_quotable(outlier, tol_pct=0.5)
    assert not quotable_out, "planted outlier should be barred, worst=%.4f%%" % worst_out
    return (quotable, worst), (quotable_out, worst_out)


def g12_20_case_b_ok(dwellings):
    sha_list = [d["gain_sha256"] for d in dwellings]
    return len(set(sha_list)) == len(sha_list)


def check_g12_20():
    baseline = [
        {"unit": 0, "gain_sha256": "aaa"},
        {"unit": 1, "gain_sha256": "bbb"},
        {"unit": 2, "gain_sha256": "ccc"},
    ]
    assert g12_20_case_b_ok(baseline), "baseline (3 distinct series) should PASS"
    collision = [
        {"unit": 0, "gain_sha256": "aaa"},
        {"unit": 1, "gain_sha256": "aaa"},
        {"unit": 2, "gain_sha256": "ccc"},
    ]
    assert not g12_20_case_b_ok(collision), "2-of-3 sharing a series should FAIL"
    return True


def g12_8_fold_ok(dwelling_country, series_bundle_fold):
    return dwelling_country.lower() == series_bundle_fold.lower()


def check_wrong_fold():
    assert g12_8_fold_ok("es", "es"), "matched fold should PASS"
    assert not g12_8_fold_ok("es", "uk"), "mismatched fold should FAIL"
    return True


if __name__ == "__main__":
    felled, total = check_g12_14()
    print("G10N.14 blank-field: %d of %d single-field blanks felled the gate" % (felled, total))
    assert felled == total

    (q_clean, w_clean), (q_out, w_out) = check_g12_replicate()
    print("G10N.replicate: clean set quotable=%s (worst %.4f%%); outlier set quotable=%s (worst %.4f%%)"
          % (q_clean, w_clean, q_out, w_out))

    check_g12_20()
    print("G10N.20 binding rule: baseline PASS, 2-of-3 collision fixture FAILS")

    check_wrong_fold()
    print("Wrong-fold check: matched fold PASS, mismatched fold FAILS")

    print("ALL FOUR CHECKS: seen felling, 0 false positives, 0 no-ops")
