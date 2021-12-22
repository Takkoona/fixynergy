all: Plots/

Plots/: Scripts/mutation_comparison.R
	Rscript Scripts/mutation_comparison.R

Scripts/mutation_comparison.R: Scripts/mutation_linkage.py
	python Scripts/mutation_linkage.py

Scripts/mutation_linkage.py: Scripts/mutation_daily_num.py
	python Scripts/mutation_daily_num.py

clean:
	rm -f Output/*
	rm -f Plots/*
