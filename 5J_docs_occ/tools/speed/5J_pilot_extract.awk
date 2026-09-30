# usage: awk -F, -f 5J_pilot_extract.awk eplusout.csv > out.csv
# keeps Date/Time + the 4 hourly columns the analysis reads; fails (exit 3) unless each name matches exactly one column
BEGIN { split("Zone Ideal Loads Supply Air Total Heating Energy|Zone Ideal Loads Supply Air Total Cooling Energy|InteriorEquipment:Electricity|Electricity:Facility", want, "|"); nw = 4 }
NR == 1 {
  for (w = 1; w <= nw; w++) { cnt[w] = 0; for (i = 1; i <= NF; i++) if (index($i, want[w]) > 0) { cnt[w]++; idx[w] = i } }
  for (w = 1; w <= nw; w++) if (cnt[w] != 1) { printf("EXTRACT column [%s] matched %d columns\n", want[w], cnt[w]) > "/dev/stderr"; bad = 1 }
  if (bad) exit 3
  printf("hour,heating_J,cooling_J,appliance_J,facility_elec_J\n")
  next
}
{ gsub(/[ 	]/, ""); n++; printf("%d,%s,%s,%s,%s\n", n, $(idx[1]), $(idx[2]), $(idx[3]), $(idx[4])) }
END { if (!bad && n != 8760) { printf("EXTRACT rows=%d expected 8760\n", n) > "/dev/stderr"; exit 4 } }
