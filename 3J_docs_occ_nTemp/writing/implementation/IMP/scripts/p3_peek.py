import pandas as pd, os
d=pd.read_csv(os.path.join("..","data","P3_comparison_long.csv"))
pd.set_option("display.width",250,"display.max_columns",40)
b=d[d.channel=="_BUILDING"][["cell_tag","annual_peak_hour_of_day_6ch","annual_peak_day_of_year_6ch","annual_peak_hour_of_day_4tenant","annual_peak_day_of_year_4tenant","peak_kW","coincidence_factor_published_6ch","coincidence_factor_4tenant","wd_peak_hour_circular","wd_peak_hour_argmax","all_peak_hour_circular_published","day_night_ratio_08_18","midday_night_ratio_published_def"]]
print(b.round(3).to_string())
h=d[d.channel.isin(["hotel","office","retail"])][["cell_tag","channel","midday_night_ratio_published_def","day_night_ratio_08_18","wd_midday_kW","wd_night_kW","occ_wd_peak_hour_argmax","occ_wd_R"]]
print(h.round(3).to_string())
