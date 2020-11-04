## Data processing scripts

### data_analysis.ipynb
Jupyter nootebook that comprises a manual and interactive data analysis proceadure to extract information for the data processing. The nb generates a .json file as output in the format to be used in the "data_preprocessing.py" script.
The .json files referring to all databases used in the experimental proceadure are provided in the "_prep.json files" folder.

### data_preprocessing.py
Pipeline employed to process and discretize the databases.

```
usage: data_preprocessing.py [-h] (--fl FL | --fd FD) [--jfl JFL | --jfd JFD]
                             [--ext EXT] [--s S] [--d D] [--p P]

Script to perform data preprocessing and discretization [default].

optional arguments:
  -h, --help  show this help message and exit
  --fl FL     File path
  --fd FD     Folder path: executes the script to all files in the folder (or
              the ones defined by extension --ext)
  --jfl JFL   Json preprocessing file path: if not provided, uses the file
              folder
  --jfd JFD   Folder for json preprocessing files: if not provided, uses the
              file folder
  --ext EXT   Extension of the files to process
  --s S       Save path: if not provided, saves processed data in the file
              folder
  --d D       Discretization [bool]: whether to perform or not
  --p P       Preprocessing [bool]: whether to perform or not
```
