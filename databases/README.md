# Survival Databases
The ESM-AM algorithm available on this repository was executed on 14 processed survival data sets presented in the Table bellow - and also provided on this folder. All data sets were processed by removing observations containing missing values and by filtering the features. As the algorithm only copes with categorical attributes, all numerical variables were discretized with K-Means into five interval categories.\
The data preprocessing pipeline is documented on the "scripts" folder.

_Table: Characteristics of 14 datasets used in the experimental study: the number of observations (#obs), the number of descriptive attributes (#att), the number of discretized descriptors (#disc), the percentage of censored observations (%cens), and the survival event description (Event)_
|**Dataset**           | **\#obs** | **\#attr** | **\#disc** | **\%cens** |  **Subject of research**  | **Event** |
|-------           | ----- | ------ | ------ | ------ |  -------------------                     | ----- |
|actg320           |  1151 |     11 |   3    |  91.66 |  HIV-infected patients                   | AIDS diagnosis/death      |
|breast-cancer     |   196 |     80 |  78    |  73.98 |  Node-Negative breast cancer             |     distant metastasis    |
|cancer            |   168 |      7 |   5    |  27.98 |  Advanced lung cancer                    |                  death    |
|carcinoma         |   193 |      8 |   1    |  27.46 |  Carcinoma of the oropharynx             |                  death    |
|gbsg2             |   686 |      8 |   5    |  56.41 |  Breast cancer                           |             recurrence    |
|lung              |   901 |      8 |   0    |  37.40 |  Early lung cancer                       |                  death    |
|melanoma          |   205 |      5 |   3    |  72.20 |  Malignant melanoma                      |                  death    |
|mgus              |   176 |      8 |   6    |   6.25 |  Monoclonal gammopathy                   |                  death    |
|mgus2             |  1338 |      7 |   5    |  29.90 |  Monoclonal gammopathy                   |                  death    |
|pbc               |   276 |     17 |  10    |  59.78 |  Primary biliary cirrhosis               |                  death    |
|ptc               |   309 |     18 |   1    |  93.53 |  Papillary thyroid carcinoma             |  recurrence/progression   |
|uis               |   575 |      9 |   4    |  19.30 |  Drug addiction treatment                |     return to drug use    |
|veteran           |   137 |      6 |   3    |   6.57 |  Lung cancer                             |                  death    |
|whas500           |   500 |     14 |   6    |  57.00 |  Worcester Heart Attack                  |                  death    |


## Original databases
The .csv files regarding the original survival data sets used in the article experimental proceadure. (info.txt files provide information on the data sets: public data domains, data sources, and general data description)

## Processed databases
The .csv files regarding the final processed databases used for the article experimental proceadure. (.json files provide the data dtypes for data reading)

## Scripts
The codes and aditional files used for data processing and data discretization.
