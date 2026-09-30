#!/usr/bin/env python
"""
WP4 hindcast wrapper (reviewer comment 4).  Task doc: 1J_docs_occ/IMP/impl/2026-09-29_WP4_hindcast.md

Calls the PROTECTED functions in previous/eSim_dynamicML_mHead.py unchanged (imported, never edited, never
monkey-patched: this wrapper installs NO patches and prints "WP4 PATCHES: none").

Modes
  selftest_metrics   G4.1 + G4.2 + G4.4-helper gates on synthetic data (no TensorFlow, no census files)
  smoke              whole path on the real files with 1 training epoch, into a scratch folder (Speed job)
  train   --seed s --latent L      train on 2006/2011/2016 ONLY, save models
  score   --seed s --latent L      project 2016->2021, score against the 2021 census
  aggregate                        B0/B1 baselines + merge + summary + pass rule
  sens2025                         production models, 2025 variants vs seed-1 K=8/0.95
Environment: WP4_ROOT (default /speed-scratch/o_iseri/1J_rerun/wp4), WP4_MH_DIR (folder holding previous/)
"""
import argparse, copy, os, random, sys, json, itertools
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance

ROOT = Path(os.environ.get("WP4_ROOT", "/speed-scratch/o_iseri/1J_rerun/wp4"))
MH_DIR = os.environ.get(
    "WP4_MH_DIR", "/speed-scratch/o_iseri/1J_rerun/occ2025/code/eSim_occ_utils/25CEN22GSS_classification")
DATA = Path(os.environ.get("WP4_DATA", str(ROOT / "data")))
OUT = ROOT / "out"
MODELS = ROOT / "models"
# production models re-serialised for keras 3.10 by convert_prod_models_k310.py (weights byte-identical; see its doc)
PROD = Path(os.environ.get("WP4_PROD", str(ROOT / "prod_models_k310")))
PROD_FP = ROOT / "code" / "prod_fingerprint_k313.json"   # fingerprint of the ORIGINAL models under keras 3.13 (local)

# mH.py:121-126 DEMOGRAPHIC_FEATURES minus YEAR (the design fixes this list)
DEMO_VARS = ['MARSTH', 'EMPIN', 'TOTINC', 'KOL', 'ATTSCH', 'CIP', 'NOCS',
             'GENSTAT', 'POWST', 'CITIZEN', 'LFTAG', 'CF_RP', 'COW', 'CMA',
             'AGEGRP', 'SEX', 'CFSTAT', 'INCTAX', 'HHSIZE', 'EFSIZE', 'CFSIZE',
             'PR', 'HRSWRK', 'MODE']
CONT = ['EMPIN', 'TOTINC', 'INCTAX']
CONT_SCALERS = ["EMPIN", "TOTINC", "INCTAX", "VALUE"]
SEEDS = [1, 2, 3, 4, 5]
KS = [4, 8, 12]
DECAYS = [0.90, 0.95, 1.00]
TRAIN_YEARS = {'2006', '2011', '2016'}
SCORE_COLS = ['method', 'K', 'decay', 'latent', 'seed', 'variable', 'metric', 'value']


# ----------------------------------------------------------------------------- metrics
def tvd_from_probs(pa, pb):
    idx = pa.index.union(pb.index)
    a = pa.reindex(idx).fillna(0.0).values
    b = pb.reindex(idx).fillna(0.0).values
    return 0.5 * float(np.abs(a - b).sum())


def tvd(a, b):
    pa = pd.Series(list(a)).astype(str).value_counts(normalize=True)
    pb = pd.Series(list(b)).astype(str).value_counts(normalize=True)
    return tvd_from_probs(pa, pb)


def w1_scaled(a, b, ref):
    """Wasserstein-1 on values min-max scaled by the range of `ref` (the 2021 values)."""
    ref = np.asarray(ref, dtype=float)
    lo, hi = float(ref.min()), float(ref.max())
    span = (hi - lo) if hi > lo else 1.0
    a = (np.asarray(a, dtype=float) - lo) / span
    b = (np.asarray(b, dtype=float) - lo) / span
    return float(wasserstein_distance(a, b))


def wrong_tvd_no_half(a, b):     # deliberately wrong (missing 0.5) - used only to SEE the gate fail
    pa = pd.Series(list(a)).astype(str).value_counts(normalize=True)
    pb = pd.Series(list(b)).astype(str).value_counts(normalize=True)
    idx = pa.index.union(pb.index)
    return float(np.abs(pa.reindex(idx).fillna(0).values - pb.reindex(idx).fillna(0).values).sum())


def metric_gate(tvd_fn, w1_fn=w1_scaled):
    """G4.2: returns a list of failure strings ([] = pass)."""
    fails = []
    x = ['a', 'a', 'b', 'c']
    if abs(tvd_fn(x, x)) > 1e-12: fails.append("TVD(x,x) != 0")
    if abs(tvd_fn(['a', 'a'], ['b', 'c']) - 1.0) > 1e-12: fails.append("TVD(disjoint) != 1")
    if abs(tvd_fn(['a', 'a', 'b'], ['a', 'b', 'b']) - 1.0 / 3.0) > 1e-12: fails.append("TVD known value != 1/3")
    v = np.array([0., 1., 2., 5.])
    if abs(w1_fn(v, v, v)) > 1e-12: fails.append("W1(x,x) != 0")
    if abs(w1_fn(v, v + 1.0, v) - 0.2) > 1e-12: fails.append("W1 shift-by-1 on range 5 != 0.2")
    return fails


def assert_no_leak(df_processed, paths=None):
    """G4.1: training frame must contain only 2006/2011/2016 rows and no 2021 path."""
    if paths is not None:
        assert set(int(y) for y in paths.keys()) == {2006, 2011, 2016}, f"G4.1 paths years {sorted(paths)}"
        assert not any('cen21' in str(p) for p in paths.values()), "G4.1 a cen21 path is in the training paths"
    ycols = [c for c in df_processed.columns if c.startswith('YEAR_')]
    present = {c.split('_', 1)[1] for c in ycols if df_processed[c].sum() > 0}
    assert present == TRAIN_YEARS, f"G4.1 LEAK/MISSING: YEAR values in training frame = {sorted(present)}"
    return sorted(present)


def scores_identical(a, b):
    """G4.4 helper: two score DataFrames identical (same order, same values)."""
    a = a.reset_index(drop=True); b = b.reset_index(drop=True)
    return a.shape == b.shape and list(a.columns) == list(b.columns) and bool(np.array_equal(a['value'].values, b['value'].values))


def selftest_metrics():
    print("=== G4.1 leakage gate ===")
    good = pd.DataFrame({'YEAR_2006': [1, 0, 0], 'YEAR_2011': [0, 1, 0], 'YEAR_2016': [0, 0, 1]})
    bad = pd.concat([good, pd.DataFrame({'YEAR_2006': [0], 'YEAR_2011': [0], 'YEAR_2016': [0], 'YEAR_2021': [1]})],
                    ignore_index=True).fillna(0)
    try:
        assert_no_leak(bad)
        print("G4.1 SELFTEST: FAILED TO FAIL on a frame with 2021 appended"); sys.exit(20)
    except AssertionError as e:
        print("G4.1 seen failing (frame with 2021 appended):", e)
    try:
        assert_no_leak(good, {2006: 'a', 2011: 'b', 2016: 'c', 2021: 'cen21_filtered2.csv'})
        print("G4.1 SELFTEST: FAILED TO FAIL on a paths dict with 2021"); sys.exit(20)
    except AssertionError as e:
        print("G4.1 seen failing (paths dict with 2021):", e)
    print("G4.1 passing case: years =", assert_no_leak(good, {2006: 'cen06', 2011: 'cen11', 2016: 'cen16'}))
    print("G4.1 SELFTEST: PASS")

    print("=== G4.2 metric gate ===")
    f_wrong = metric_gate(wrong_tvd_no_half)
    print("G4.2 seen failing (TVD without the 0.5):", f_wrong)
    if not f_wrong:
        print("G4.2 SELFTEST: FAILED TO FAIL on the wrong TVD"); sys.exit(21)
    f_ok = metric_gate(tvd)
    print("G4.2 correct metrics failures:", f_ok)
    if f_ok:
        print("G4.2 SELFTEST: FAIL"); sys.exit(22)
    print("G4.2 SELFTEST: PASS")

    print("=== G4.4 helper (scores_identical) ===")
    d1 = pd.DataFrame({c: [1.0, 2.0] for c in SCORE_COLS})
    d2 = d1.copy(); d2.loc[1, 'value'] = 2.0000001
    if scores_identical(d1, d2):
        print("G4.4 SELFTEST: FAILED TO FAIL on perturbed scores"); sys.exit(23)
    print("G4.4 helper seen failing (perturbed copy)")
    if not scores_identical(d1, d1.copy()):
        print("G4.4 SELFTEST: FAIL"); sys.exit(24)
    print("G4.4 helper passing case OK")
    print("WP4 PATCHES: none (no monkey-patching in this wrapper)")
    print("SELFTEST METRICS: ALL PASS")


# ----------------------------------------------------------------------------- TF / protected module
def _mh():
    if MH_DIR not in sys.path:
        sys.path.insert(0, MH_DIR)
    from previous import eSim_dynamicML_mHead as mh
    return mh


def set_threads():
    import tensorflow as tf
    n = int(os.environ.get("SLURM_CPUS_PER_TASK", "3"))
    tf.config.threading.set_intra_op_parallelism_threads(n)
    tf.config.threading.set_inter_op_parallelism_threads(2)
    print(f"THREADS: intra={n} inter=2")


def set_seeds(seed):
    import tensorflow as tf
    random.seed(seed); np.random.seed(seed); tf.random.set_seed(seed)


def load_real(path):
    df = pd.read_csv(path, dtype=str, usecols=DEMO_VARS)
    for c in DEMO_VARS:
        if c in CONT:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        else:
            df[c] = df[c].fillna('Missing')
    return df


def score_frame(pred, real21, method, K, decay, latent, seed):
    """One row per variable.  pred/real21 have DEMO_VARS columns.  Unweighted."""
    rows = []
    for v in DEMO_VARS:
        if v in CONT:
            rows.append((method, K, decay, latent, seed, v, 'W1', w1_scaled(pred[v], real21[v], real21[v])))
        else:
            rows.append((method, K, decay, latent, seed, v, 'TVD', tvd(pred[v], real21[v])))
    return pd.DataFrame(rows, columns=SCORE_COLS)


def prep(years_paths, sample_frac=1.0):
    mh = _mh()
    return mh.prepare_data_for_generative_model({y: str(p) for y, p in years_paths.items()}, sample_frac=sample_frac)


def paths_for(years):
    return {y: DATA / f"cen{str(y)[2:]}_filtered2.csv" for y in years}


def load_models(mdir):
    mh = _mh()
    from tensorflow import keras
    enc = keras.models.load_model(Path(mdir) / "cvae_encoder.keras", custom_objects={"Sampling": mh.Sampling})
    dec = keras.models.load_model(Path(mdir) / "cvae_decoder.keras")
    return enc, dec


def model_fingerprint(enc, dec):
    """Per-variable float64 weight sums + z_mean and decoder outputs on a fixed random input (rng seed 0)."""
    rng = np.random.default_rng(0)
    xd = rng.random((64, enc.inputs[0].shape[-1])).astype(np.float32)
    xb = rng.random((64, enc.inputs[1].shape[-1])).astype(np.float32)
    zm = enc.predict([xd, xb], verbose=0)[0]
    out = dec.predict([zm, xb], verbose=0)
    out = out if isinstance(out, list) else [out]
    # keyed by variable path: keras 3.10 and 3.13 list the decoder's variables in a different order (probe 1401489);
    # md5 of the raw bytes, not a float sum: numpy versions sum large arrays differently in the last bits (probe 1401509)
    import hashlib
    def wsum(m):
        return {getattr(v, 'path', v.name): hashlib.md5(np.ascontiguousarray(v.numpy()).tobytes()).hexdigest() + str(tuple(v.shape))
                for v in m.weights}
    return {'enc_w': wsum(enc), 'dec_w': wsum(dec),
            'z_mean': np.asarray(zm, dtype=np.float64).ravel()[:512].tolist(),
            'dec_out': np.concatenate([np.asarray(o, dtype=np.float64).ravel() for o in out])[:2048].tolist()}


def compare_fingerprints(a, b, tol=1e-5):
    """[] = same model. Weight byte hashes must match exactly; predictions within tol (float32 math on another CPU)."""
    fails = []
    for k in ['enc_w', 'dec_w']:
        if a[k] != b[k]:
            diff = sorted(p for p in set(a[k]) | set(b[k]) if a[k].get(p) != b[k].get(p))
            fails.append(f"{k} differ on {len(diff)} of {len(a[k])} variables, e.g. {diff[:3]}")
    for k in ['z_mean', 'dec_out']:
        x, y = np.array(a[k]), np.array(b[k])
        if x.shape != y.shape or np.max(np.abs(x - y)) > tol:
            fails.append(f"{k} max abs diff {np.max(np.abs(x - y)) if x.shape == y.shape else 'shape'}")
    return fails


def latent_history(encoder, df_proc, demo_cols, bldg_cols):
    """Same extraction as train_temporal_model (mH.py:497-506): z_mean per census year."""
    year_cols = sorted(c for c in demo_cols if c.startswith('YEAR_'))
    hist = {}
    for col in year_cols:
        y = int(col.split('_')[1])
        ydf = df_proc[df_proc[col] == 1]
        z_mean, _, _ = encoder.predict([ydf[demo_cols].values.astype(np.float32),
                                        ydf[bldg_cols].values.astype(np.float32)], verbose=0)
        hist[y] = z_mean
    return hist


def make_model(hist, K, decay, cache):
    """ClusterMomentumModel(K, decay) fitted exactly as train_temporal_model does (mH.py:514-515).
    KMeans depends on K only (decay is used only in predict), so fit once per K and copy with the new decay."""
    mh = _mh()
    if K not in cache:
        base = mh.ClusterMomentumModel(n_clusters=K, decay_factor=decay)
        base.fit(hist)
        cache[K] = base
    m = copy.copy(cache[K])
    m.decay = decay
    return m


def generate(decoder, model, hist, df_proc, bldg_cols, demo_cols, scalers, target_year, n, seed):
    mh = _mh()
    last_year = sorted(hist.keys())[-1]
    set_seeds(seed)                       # the same seed drives generation (design item 6)
    gen_raw, bldg_raw, _ = mh.generate_future_population(
        decoder, model, hist[last_year], last_year, df_proc, bldg_cols,
        target_year=target_year, n_samples=n, variance_factor=1.15)
    df = mh.post_process_generated_data(gen_raw, demo_cols, bldg_raw, bldg_cols, scalers, ref_df=df_proc)
    return df


# ----------------------------------------------------------------------------- modes
def cmd_train(seed, latent, epochs=100, out_root=None, sample_frac=1.0):
    mh = _mh()
    set_threads()
    paths = paths_for([2006, 2011, 2016])                # cen21 is never named here (G4.1)
    print("TRAIN FILES:", {k: str(v) for k, v in paths.items()})
    df_proc, demo_cols, bldg_cols, scalers = prep(paths, sample_frac)
    yrs = assert_no_leak(df_proc, paths)
    print(f"G4.1 PASS: YEAR values in training frame = {yrs}; rows = {len(df_proc)}; demo cols = {len(demo_cols)}; bldg cols = {len(bldg_cols)}")
    set_seeds(seed)
    print(f"SEEDS set: seed={seed} (random, numpy, tensorflow); latent_dim={latent}; epochs={epochs}; batch_size=4096")
    enc, dec, cvae, hist = mh.train_cvae(df_proc, demo_cols, bldg_cols, continuous_cols=CONT_SCALERS,
                                         latent_dim=latent, epochs=epochs, batch_size=4096)
    mdir = Path(out_root or MODELS) / f"seed{seed}_ld{latent}"
    mdir.mkdir(parents=True, exist_ok=True)
    enc.save(mdir / "cvae_encoder.keras"); dec.save(mdir / "cvae_decoder.keras")
    last = {k: float(v[-1]) for k, v in hist.history.items()}
    json.dump({'seed': seed, 'latent': latent, 'epochs': epochs, 'rows': int(len(df_proc)),
               'demo_cols': len(demo_cols), 'bldg_cols': len(bldg_cols), 'final_loss': last},
              open(mdir / "train_info.json", "w"))
    print(f"TRAIN DONE: saved {mdir}; final losses {last}")


def cmd_score(seed, latent, out_root=None, models_root=None, ks=None, decays=None, with_b2=True, g44=True):
    set_threads()
    out = Path(out_root or OUT); out.mkdir(parents=True, exist_ok=True)
    paths = paths_for([2006, 2011, 2016])
    df_proc, demo_cols, bldg_cols, scalers = prep(paths, 1.0)
    assert_no_leak(df_proc, paths)
    print("G4.1 PASS at scoring: training frame years =", sorted(TRAIN_YEARS))
    enc, dec = load_models(Path(models_root or MODELS) / f"seed{seed}_ld{latent}")
    enc_in = [i.shape[-1] for i in enc.inputs]
    assert enc_in == [len(demo_cols), len(bldg_cols)], f"encoder input dims {enc_in} vs data {(len(demo_cols), len(bldg_cols))}"
    hist = latent_history(enc, df_proc, demo_cols, bldg_cols)
    print("LATENT YEARS:", {y: z.shape for y, z in hist.items()})
    real21 = load_real(DATA / "cen21_filtered2.csv")       # the ONLY place 2021 is read
    n = len(real21)
    print(f"2021 records (generated n) = {n}")
    cache = {}
    ks = ks or ([4, 8, 12] if latent == 128 else [8])
    decays = decays or ([0.90, 0.95, 1.00] if latent == 128 else [0.95])
    frames = []
    first_df = None
    for K, d in itertools.product(ks, decays):
        m = make_model(hist, K, d, cache)
        gdf = generate(dec, m, hist, df_proc, bldg_cols, demo_cols, scalers, 2021, n, seed)
        gv = [v for v in DEMO_VARS if v in gdf.columns and v in real21.columns]
        assert gv == DEMO_VARS, f"variable list mismatch: missing {set(DEMO_VARS) - set(gv)}"
        print(f"VARIABLES SCORED ({len(gv)}): {gv}")
        s = score_frame(gdf, real21, 'CBVM', K, d, latent, seed)
        print(f"SCORED CBVM K={K} decay={d} seed={seed} latent={latent}: mean over variables = {s['value'].mean():.4f}")
        frames.append(s)
        if K == 8 and abs(d - 0.95) < 1e-12 and first_df is None:
            first_df = s
    if with_b2 and latent == 128:
        m = make_model(hist, 1, 0.95, cache)
        gdf = generate(dec, m, hist, df_proc, bldg_cols, demo_cols, scalers, 2021, n, seed)
        s = score_frame(gdf, real21, 'B2', 1, 0.95, latent, seed)
        print(f"SCORED B2 K=1 decay=0.95 seed={seed}: mean over variables = {s['value'].mean():.4f}")
        frames.append(s)
    if g44 and first_df is not None:
        m = make_model(hist, 8, 0.95, cache)
        gdf = generate(dec, m, hist, df_proc, bldg_cols, demo_cols, scalers, 2021, n, seed)
        again = score_frame(gdf, real21, 'CBVM', 8, 0.95, latent, seed)
        ok = scores_identical(first_df, again)
        print(f"G4.4 REPRODUCIBLE (seed {seed}, same saved model, generation run twice): {'PASS' if ok else 'FAIL'}")
    res = pd.concat(frames, ignore_index=True)
    fn = out / f"scores_seed{seed}_ld{latent}.csv"
    res.to_csv(fn, index=False)
    print(f"SCORE DONE: wrote {fn} ({len(res)} rows)")


def cmd_aggregate(out_root=None):
    out = Path(out_root or OUT)
    real21 = load_real(DATA / "cen21_filtered2.csv")
    r16 = load_real(DATA / "cen16_filtered2.csv")
    r11 = load_real(DATA / "cen11_filtered2.csv")
    # B0: carry-forward 2016
    b0 = score_frame(r16, real21, 'B0', '', '', '', '')
    # B1: linear trend of marginals
    rows = []
    for v in DEMO_VARS:
        if v in CONT:
            q = np.arange(1, 100)
            q16, q11 = np.percentile(r16[v], q), np.percentile(r11[v], q)
            ext = np.sort(2 * q16 - q11)
            rows.append(('B1', '', '', '', '', v, 'W1', w1_scaled(ext, real21[v], real21[v])))
        else:
            p16 = r16[v].value_counts(normalize=True); p11 = r11[v].value_counts(normalize=True)
            idx = p16.index.union(p11.index)
            ext = (p16.reindex(idx).fillna(0) + (p16.reindex(idx).fillna(0) - p11.reindex(idx).fillna(0))).clip(lower=0)
            ext = ext / ext.sum()
            p21 = real21[v].value_counts(normalize=True)
            rows.append(('B1', '', '', '', '', v, 'TVD', tvd_from_probs(ext, p21)))
    b1 = pd.DataFrame(rows, columns=SCORE_COLS)
    pr = b0[b0.variable == 'PR']['value'].iloc[0]
    print(f"G4.3 B0 TVD on PR = {pr:.4f} (smell test, not a pass rule; expect small){'  WARN: not small' if pr > 0.05 else ''}")
    parts = [b0, b1]
    missing = []
    expect = [f"scores_seed{s}_ld128.csv" for s in SEEDS] + ["scores_seed1_ld64.csv", "scores_seed1_ld256.csv"]
    for f in expect:
        p = out / f
        if p.exists():
            parts.append(pd.read_csv(p))
        else:
            missing.append(f)
    allsc = pd.concat(parts, ignore_index=True)
    allsc.to_csv(out / "hindcast_scores.csv", index=False)
    a = allsc.copy()
    for c in ['K', 'decay', 'latent', 'seed']:
        a[c] = a[c].astype(str)
    grp = a.groupby(['variable', 'metric', 'method', 'K', 'decay', 'latent'])['value']
    summ = grp.agg(n_seeds='count', mean='mean', min='min', max='max').reset_index()
    summ.to_csv(out / "hindcast_summary.csv", index=False)
    lines = ["WP4 hindcast pass rule (fixed 2026-09-19 before any run). Unweighted: no survey weights exist in these files.",
             "Distance to the real 2021 Census; seed-mean over seeds 1-5; CBVM = K=8, decay 0.95, latent 128; strict '<' vs B0.",
             ""]
    if missing:
        lines.append(f"MISSING score files: {missing}")
        lines.append("WP4 PASS RULE: NOT_EVALUABLE (score files missing)")
    else:
        c = summ[(summ.method == 'CBVM') & (summ.K == '8') & (summ.decay == '0.95') & (summ.latent == '128')].set_index('variable')
        b = summ[summ.method == 'B0'].set_index('variable')
        assert (c.n_seeds == 5).all(), "CBVM K8/0.95 does not have 5 seeds for every variable"
        vs = list(c.index)
        wins = [v for v in vs if c.loc[v, 'mean'] < b.loc[v, 'mean']]
        N = len(vs)
        lines.append("variable, metric, CBVM_seed_mean, B0, closer")
        for v in vs:
            lines.append(f"{v}, {c.loc[v, 'metric']}, {c.loc[v, 'mean']:.5f}, {b.loc[v, 'mean']:.5f}, {'CBVM' if v in wins else 'B0'}")
        for name, meth in [('B1', 'B1'), ('B2', 'B2')]:
            o = summ[(summ.method == meth)].set_index('variable')
            if meth == 'B2':
                o = o[(o.K == '1')]
            w = sum(1 for v in vs if c.loc[v, 'mean'] < o.loc[v, 'mean'])
            lines.append(f"(information only) CBVM beats {name} on {w} of {N}")
        verdict = 'MET' if len(wins) * 2 > N else 'NOT MET'
        lines.append(f"WP4 PASS RULE: CBVM beats B0 on {len(wins)} of {N} -> {verdict}")
    (out / "pass_rule.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[-3:]))
    print("AGGREGATE DONE")


def cmd_sens2025(out_root=None, prod_dir=None, sample_frac=1.0, n=250000):
    set_threads()
    out = Path(out_root or OUT); out.mkdir(parents=True, exist_ok=True)
    paths = paths_for([2006, 2011, 2016, 2021])
    df_proc, demo_cols, bldg_cols, scalers = prep(paths, sample_frac)
    enc, dec = load_models(prod_dir or PROD)
    enc_in = [i.shape[-1] for i in enc.inputs]
    assert enc_in == [len(demo_cols), len(bldg_cols)], f"PRODUCTION encoder input dims {enc_in} vs data {(len(demo_cols), len(bldg_cols))}"
    print(f"PRODUCTION MODELS OK: encoder inputs {enc_in} match the 4-year data; latent dim {enc.outputs[0].shape[-1]}")
    hist = latent_history(enc, df_proc, demo_cols, bldg_cols)
    print("LATENT YEARS:", sorted(hist.keys()))
    cache = {}
    ref = generate(dec, make_model(hist, 8, 0.95, cache), hist, df_proc, bldg_cols, demo_cols, scalers, 2025, n, 1)
    rows = []

    def cmp(df, variant, K, d, seed):
        for v in DEMO_VARS:
            if v in CONT:
                rows.append((variant, K, d, seed, v, 'W1', w1_scaled(df[v], ref[v], ref[v])))
            else:
                rows.append((variant, K, d, seed, v, 'TVD', tvd(df[v], ref[v])))
    # control: the reference regenerated with the same seed must be identical
    again = generate(dec, make_model(hist, 8, 0.95, cache), hist, df_proc, bldg_cols, demo_cols, scalers, 2025, n, 1)
    cmp(again, 'control_repeat_seed1_K8_d0.95', 8, 0.95, 1)
    ctrl = max(r[-1] for r in rows)
    print(f"CONTROL repeat of the reference: max distance = {ctrl:.6f} (expect 0)")
    for K, d in itertools.product(KS, DECAYS):
        if K == 8 and abs(d - 0.95) < 1e-12:
            continue
        cmp(generate(dec, make_model(hist, K, d, cache), hist, df_proc, bldg_cols, demo_cols, scalers, 2025, n, 1),
            f'K{K}_d{d}', K, d, 1)
        print(f"SENS variant K={K} decay={d} done")
    for s in [2, 3, 4, 5]:
        cmp(generate(dec, make_model(hist, 8, 0.95, cache), hist, df_proc, bldg_cols, demo_cols, scalers, 2025, n, s),
            f'seed{s}_K8_d0.95', 8, 0.95, s)
        print(f"SENS seed {s} done")
    res = pd.DataFrame(rows, columns=['variant', 'K', 'decay', 'seed', 'variable', 'metric', 'value'])
    res.to_csv(out / "sens2025.csv", index=False)
    print(f"SENS2025 DONE: wrote {out/'sens2025.csv'} ({len(res)} rows); reference = seed 1, K=8, decay 0.95, n={n}, dt=4 from 2021")


def cmd_sens2025_probe():
    set_threads()
    enc, dec = load_models(PROD)
    print(f"PRODUCTION MODELS LOADED from {PROD}")
    ref = json.load(open(PROD_FP))
    # the check must be seen failing: a copy with one weight sum nudged has to be rejected
    bad = copy.deepcopy(ref); k0 = sorted(bad["enc_w"])[0]; bad["enc_w"][k0] = "0" + bad["enc_w"][k0][1:]
    fp = model_fingerprint(enc, dec)
    if not compare_fingerprints(fp, bad):
        print("PROD FINGERPRINT SELFTEST: FAILED TO FAIL on a nudged copy"); sys.exit(30)
    print("PROD FINGERPRINT seen failing (nudged copy):", compare_fingerprints(fp, bad))
    f = compare_fingerprints(fp, ref)
    print(f"PROD FINGERPRINT vs the original models under keras 3.13: {'SAME MODEL' if not f else 'DIFFERENT: ' + str(f)}")
    if f:
        sys.exit(31)
    paths = paths_for([2006, 2011, 2016, 2021])
    df_proc, demo_cols, bldg_cols, scalers = prep(paths, 1.0)
    enc_in = [i.shape[-1] for i in enc.inputs]
    assert enc_in == [len(demo_cols), len(bldg_cols)], f"PRODUCTION encoder input dims {enc_in} vs data {(len(demo_cols), len(bldg_cols))}"
    print(f"PRODUCTION MODELS OK: encoder inputs {enc_in} match the 4-year data")
    hist = latent_history(enc, df_proc, demo_cols, bldg_cols)
    g = generate(dec, make_model(hist, 8, 0.95, {}), hist, df_proc, bldg_cols, demo_cols, scalers, 2025, 2000, 1)
    print("PRODUCTION GENERATION OK: 2025 sample columns =", len(g.columns), "rows =", len(g))


def cmd_smoke():
    """Whole path on a scratch folder: 1-epoch training, scoring with K in {8,1}, prod-model load check.
    Nothing here goes to the real out/ or models/ folders."""
    tmp = ROOT / "smoke"
    print("SMOKE: scratch folder", tmp)
    cmd_train(1, 128, epochs=1, out_root=tmp / "models")
    cmd_score(1, 128, out_root=tmp / "out", models_root=tmp / "models", ks=[8, 1], decays=[0.95], with_b2=False, g44=True)
    cmd_sens2025_probe()
    print("SMOKE DONE: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["selftest_metrics", "smoke", "train", "score", "aggregate", "sens2025", "probe"])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--latent", type=int, default=128)
    a = ap.parse_args()
    print("WP4 PATCHES: none (protected functions imported and called unchanged)")
    if a.mode == "selftest_metrics": selftest_metrics()
    elif a.mode == "smoke": selftest_metrics(); cmd_smoke()
    elif a.mode == "train": cmd_train(a.seed, a.latent)
    elif a.mode == "score": cmd_score(a.seed, a.latent)
    elif a.mode == "aggregate": cmd_aggregate()
    elif a.mode == "sens2025": cmd_sens2025()
    elif a.mode == "probe": cmd_sens2025_probe(); print("PROBE DONE: PASS")
