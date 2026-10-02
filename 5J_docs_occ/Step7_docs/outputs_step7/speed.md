# Step 7 speed (G5J.7, reported): EnergyPlus against the surrogate S, seconds per dwelling-year

All numbers are read from the jobs' own clock lines (job logs and done files). A dwelling-year is one dwelling for 8,760 h.

## EnergyPlus (one CPU per run; the 2,000 district check runs; 2000 read, 0 not usable)

* wall seconds per dwelling-year, build + run + extract: median over runs 1.675 ; total wall / total dwelling-years 1.665
* EnergyPlus alone, seconds per dwelling-year: median over runs 1.083
* wall seconds per run: median 26.3, mean 33.9 ; total 67746 s = 18.82 CPU-h for 40680 dwelling-years
* nodes (runs per node): [('speed-12.encs.concordia.ca', 127), ('speed-16.encs.concordia.ca', 23), ('speed-20.encs.concordia.ca', 128), ('speed-21.encs.concordia.ca', 278), ('speed-22.encs.concordia.ca', 279), ('speed-23.encs.concordia.ca', 279), ('speed-24.encs.concordia.ca', 253), ('speed-29.encs.concordia.ca', 125), ('speed-30.encs.concordia.ca', 127), ('speed-34.encs.concordia.ca', 127), ('speed-35.encs.concordia.ca', 127), ('speed-36.encs.concordia.ca', 127)]
* The runs of the pilot draw (100) ran 4 at a time, the other 1,900 up to 15 at a time on shared nodes; a run is one process on one CPU in both cases.

## S, pinned S3 (md5 78271da9...)

Load = reading the flats table, the households and the checkpoint onto the device. Write = what the variant writes (see the column). Store build on the CPU (a few seconds per draw) is not in the numbers.

| job | device (node) | variant | dwelling-years | load s | predict s | write s | predict only s/dwy | predict + write s/dwy | load + predict + write s/dwy | EnergyPlus wall / S (predict + write) |
|---|---|---|---|---|---|---|---|---|---|---|
| GPU, district writer, draws 0-9 | NVIDIA A100-SXM4-80GB MIG 2g.20gb (speed-42.encs.concordia.ca) | district hourly totals + per-dwelling annual totals | 20340 | 0.8 | 555.9 | 3.2 | 0.02733 | 0.02748 | 0.02752 | 61 |
| GPU, per-dwelling hourly files, 20 check draws | NVIDIA A100-SXM4-80GB MIG 2g.20gb (speed-43.encs.concordia.ca) | per-dwelling hourly files (8,760 x 4 per dwelling, csv.gz) | 40680 | 0.5 | 1112.9 | 3821.6 | 0.02736 | 0.12130 | 0.12131 | 14 |
| ONE CPU core (threads 1), district writer, draw 0 | cpu(1 thread) (speed-20.encs.concordia.ca) | district hourly totals + per-dwelling annual totals | 2034 | 0.8 | 2815.6 | 0.4 | 1.38426 | 1.38443 | 1.38480 | 1 |

## Reading

* (i) predict only, (ii) predict + district write, (iii) predict + per-dwelling hourly write are the three GPU rows/columns above (i is the 'predict only' column of the first GPU row).
* The CPU core row runs the model in float32 (no bf16 autocast on the CPU), one thread; the GPU rows use bf16 autocast on a MIG 2g.20gb slice of an A100.
* Ratios use the median EnergyPlus wall seconds per dwelling-year (build + run + extract).
