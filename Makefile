all: Plots/

Plots/: Scripts/mutation_comparison.R
	Rscript Scripts/mutation_comparison.R

Scripts/mutation_comparison.R: Scripts/area_fixed_daily.py
	python Scripts/area_fixed_daily.py

Scripts/area_fixed_daily.py: Scripts/mutation_daily_num.py
	python Scripts/mutation_daily_num.py

clean:
	rm -f Output/*
	rm -f Plots/*
