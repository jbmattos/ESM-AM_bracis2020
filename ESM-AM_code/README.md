# ESM-AM algorithm

Algorithm to the discovery of subgroups with unusual survival models.

## Usage
```
ESMAM.py [-h] (--p P | --fd FD) [--s S] [--dtype] [--n N] 
         [--ants ANTS] [--minCases MINCASES] [--maxUncover MAXUNCOVER]
         [--converg CONVERG] [--alpha ALPHA] 
         [--featTime FEATTIME] [--featEvent FEATEVENT]

Exceptional Survival Model Ant-Miner algorithm

required arguments:
  --p P                 Dataset File path
  --fd FD               Dataset Folder path: runs ESM-AM on all .csv files in folder
```

#### Usage1: Execution of a single data file
Runs the algorithm on the provided data.
```
python ESMAM.py --p=data_path.csv¹
```

#### Usage2: Execution of multiple data files
Runs the algorithm for each data.csv file inside the given folder path.
```
python ESMAM.py --fd=data_folder_path
```

#### Additional setting
```
Optional arguments:
--s                     Path to save log-files [default: local python folder]
--dtype                 Use dtypes.json² to read data (store-true parameter)
--n                     Name prefix for log-files [default: 'esmam']
--ants ANTS             ESM-AM parameter: number of ants [default: 3000]
--minCases MINCASES     ESM-AM parameter: minimum number of cases per rule  [default: 10]
--maxUncover MAXUNCOVER ESM-AM parameter: maximum number of remaining uncovered cases  [default: 0]
--converg CONVERG       ESM-AM parameter: number of identical rules to convergence  [default: 10]
--alpha ALPHA           ESM-AM parameter: level of significance of the Logrank test  [default: 0.05]
--featTime FEATTIME     The name of Survival Time feature  [default: 'survival_time']
--featEvent FEATEVENT   The name of Survival Status feature  [default: 'survival_status']
```

¹ The data files must be in .csv, separated by comma, with the header (features' names) on the first line, and with no rows' names column.
² The dtypes.json file must be on the same path of the data file, with the same name ended by "_dtypes.json" (e.g., "dataFile.csv" > "dataFile_dtypes.json")

## Results
The algorithm provides three results' files:
```
> "n-prefix"_log.txt: contains the general run information 
> "n-prefix"_RuleSet.txt: provides the discovered rule-model (each discovered subgroup and characteristics)
> "n-prefix"_KM-Estimates.txt: provides the KM models of the discovered subgroups (and population)
```
