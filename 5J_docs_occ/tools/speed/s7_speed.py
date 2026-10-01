# -*- coding: utf-8 -*-
"""5J Step 7 part G (Speed CPU job): outputs_step7/speed.md from the jobs' OWN clock lines.
EnergyPlus: ep/done/<run>.json of the 2,000 district runs (wall_seconds_incl_build_extract = build + run + extract on one CPU; seconds = EnergyPlus alone; host).
S: the SPEED_S lines printed by s7_draws_gpu.py in three job logs (paths in the environment): LOG_TIME (GPU, draws 0-9, district writer),
LOG_HOURLY (GPU, 20 check draws, per-dwelling hourly files), LOG_CPU (ONE CPU core, threads 1, draw 0, district writer)."""
import io, json, os, re, statistics, sys
sys.dont_write_bytecode = True
import s7_common as s7

OUT = s7.D + "out_step7/"
PAT = re.compile(r"SPEED_S mode=(\w+) tag=(\S+) node=(\S+) device=(.*) dwy=(\d+) store_s=([\d.]+) load_s=([\d.]+) predict_s=([\d.]+) accumulate_or_hourly_write_s=([\d.]+) district_write_s=([\d.]+) total_incl_load_s=([\d.]+)")


def parse(path):
    out = []
    for ln in io.open(path, encoding="utf-8", errors="replace"):
        m = PAT.search(ln)
        if m:
            g = m.groups()
            out.append({"mode": g[0], "tag": g[1], "node": g[2], "device": g[3], "dwy": int(g[4]), "store": float(g[5]), "load": float(g[6]), "predict": float(g[7]), "acc": float(g[8]), "dwrite": float(g[9]), "total": float(g[10])})
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    runs = s7.read_csv(s7.IN + "district_runs_es.csv")
    wall, epo, perw, perp, nds, hosts = [], [], [], [], [], {}
    miss = 0
    for r in runs:
        p = s7.D + "ep/done/%s.json" % r["run_id"]
        if not os.path.exists(p):
            miss += 1
            continue
        d = json.load(io.open(p, encoding="utf-8"))
        if d.get("status") != "pass":
            miss += 1
            continue
        n = int(r["n_dwellings"])
        wall.append(d["wall_seconds_incl_build_extract"])
        epo.append(d["seconds"])
        perw.append(d["wall_seconds_incl_build_extract"] / n)
        perp.append(d["seconds"] / n)
        nds.append(n)
        hosts[d.get("host")] = hosts.get(d.get("host"), 0) + 1
    print("EP runs read %d of %d (missing or not pass %d)" % (len(wall), len(runs), miss))
    ep_w = statistics.median(perw)
    ep_e = statistics.median(perp)
    ep_tot = sum(wall) / sum(nds)
    L = ["# Step 7 speed (G5J.7, reported): EnergyPlus against the surrogate S, seconds per dwelling-year", "",
         "All numbers are read from the jobs' own clock lines (job logs and done files). A dwelling-year is one dwelling for 8,760 h.", "",
         "## EnergyPlus (one CPU per run; the 2,000 district check runs; %d read, %d not usable)" % (len(wall), miss), "",
         "* wall seconds per dwelling-year, build + run + extract: median over runs %.3f ; total wall / total dwelling-years %.3f" % (ep_w, ep_tot),
         "* EnergyPlus alone, seconds per dwelling-year: median over runs %.3f" % ep_e,
         "* wall seconds per run: median %.1f, mean %.1f ; total %.0f s = %.2f CPU-h for %d dwelling-years" % (statistics.median(wall), sum(wall) / len(wall), sum(wall), sum(wall) / 3600.0, sum(nds)),
         "* nodes (runs per node): %s" % sorted(hosts.items()),
         "* The runs of the pilot draw (100) ran 4 at a time, the other 1,900 up to 15 at a time on shared nodes; a run is one process on one CPU in both cases.", ""]
    rows = []
    for key, label in (("LOG_TIME", "GPU, district writer, draws 0-9"), ("LOG_HOURLY", "GPU, per-dwelling hourly files, 20 check draws"), ("LOG_CPU", "ONE CPU core (threads 1), district writer, draw 0")):
        ps = os.environ.get(key)
        if not ps or not os.path.exists(ps):
            L.append("* %s: log not found (%s)" % (key, ps))
            continue
        for x in parse(ps):
            rows.append((key, label, x))
    L.extend(["## S, pinned S3 (md5 78271da9...)", "",
              "Load = reading the flats table, the households and the checkpoint onto the device. Write = what the variant writes (see the column). Store build on the CPU (a few seconds per draw) is not in the numbers.", "",
              "| job | device (node) | variant | dwelling-years | load s | predict s | write s | predict only s/dwy | predict + write s/dwy | load + predict + write s/dwy | EnergyPlus wall / S (predict + write) |",
              "|---|---|---|---|---|---|---|---|---|---|---|"])
    for key, label, x in rows:
        if x["mode"] == "district":
            var, wr = "district hourly totals + per-dwelling annual totals", x["acc"] + x["dwrite"]
        else:
            var, wr = "per-dwelling hourly files (8,760 x 4 per dwelling, csv.gz)", x["acc"]
        n = x["dwy"]
        L.append("| %s | %s (%s) | %s | %d | %.1f | %.1f | %.1f | %.5f | %.5f | %.5f | %.0f |" % (label, x["device"], x["node"], var, n, x["load"], x["predict"], wr, x["predict"] / n, (x["predict"] + wr) / n, (x["load"] + x["predict"] + wr) / n, ep_w / ((x["predict"] + wr) / n)))
    L.extend(["", "## Reading", "",
              "* (i) predict only, (ii) predict + district write, (iii) predict + per-dwelling hourly write are the three GPU rows/columns above (i is the 'predict only' column of the first GPU row).",
              "* The CPU core row runs the model in float32 (no bf16 autocast on the CPU), one thread; the GPU rows use bf16 autocast on a MIG 2g.20gb slice of an A100.",
              "* Ratios use the median EnergyPlus wall seconds per dwelling-year (build + run + extract)."])
    io.open(OUT + "speed.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("WROTE %sspeed.md md5 %s" % (OUT, s7.md5(OUT + "speed.md")))
    for ln in L:
        print("SPEED_MD " + ln)


if __name__ == "__main__":
    main()
