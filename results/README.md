# ESM-AM Bracis2020 Experimental Results

The ESM-AM algorithm available on this repository was executed on 14 survival data sets. The data characterisation and processing pipeline is documented on this repo "databases" folder.\
\
The results analysis regarding the characteristics of the final rule-models was performed according to five metrics: (1) the number of discovered rules [num_rules]; (2) the average rule length [length]; (3) the average relative rule coverage [ruleCoverage] (and standard-deviation [ruleCoverageSTD]); (4) the rule set coverage [setCoverage]; and (5) integrated Brier score on the rule set [IBS].\
The analysis regarding the interestingness of the discovered patterns was assessed through the Kaplan-Meier (KM) curves.

## Results

### final_results
Provides the final results:\
(i)  a .json file with the computed analysed metrics for each data set; and\
(ii) a .pdf for each data set containing the survival models (KM plots) of all discovered subgroups, and - individually - the survival models of each subgroup in contrast to its complement and the population.

### \_esmam_log-files
Provides the ESM-AM execution log-files (described bellow), for each data set.
```
- "dataset"_log.txt: contains the general run information 
- "dataset"_RuleSet.txt: provides the discovered rule-model (each discovered subgroup and characteristics)
- "dataset"_KM-Estimates.txt: provides the KM models of the discovered subgroups (and population)
```

### process_results.py
Script that generates the results in the format provided in "final_results". Makes use of the \_esmam_log-files (specifically "\_RuleSet.txt" and "\_KM-Estimates.txt" files).
```
usage: process_results.py [-h] --p P [--db DB | --r] [--noFigs] [--parlel]
                          [--cpu CPU] [--featTime FEATTIME]
                          [--featEvent FEATEVENT]

Script to process the log files into results.

required arguments:
  --p P                 Log-files folder path¹
```
¹--p must contain both "\_RuleSet.txt" and "\_KM-Estimates.txt" files.\
\
**Usage1: process single-run files**
```
python process_results.py --p=files_folder --db=dataset.csv[optional]
```
Process the results of a single ESM-AM run. If --db is not provided, the dataset.csv file must be inside --p.\
_Output:_ esmam_metrics.json and esmam_survivalModels.pdf files (saved inside --p).\
\
**Usage2: process multiple-run files**
```
python process_results.py --p=files_folder --r
```
Process the results of each subfolder of --p. In this case, both "\_RuleSet.txt" and "\_KM-Estimates.txt" files **and** the dataset.csv file must be inside --p.
_Output:_ esmam_metrics.json, with all subfolders metrics integrated in a single nested dictionary; and subfolder_survivalModels.pdf files for each subfolder (saved inside --p).\
\
**Additional setting**
```
Optional arguments
  --noFigs                Do NOT generate the survival models' plots (store-false parameter)
  --parlel                Parallel IBS computation: calculates IBS with parallel processing (store-true parameter)
  --cpu CPU               Number of parallel cpus [default: os.cpu_count()]
  --featTime FEATTIME     The name of Survival Time feature  [default: 'survival_time']
  --featEvent FEATEVENT   The name of Survival Status feature  [default: 'survival_status']
```
