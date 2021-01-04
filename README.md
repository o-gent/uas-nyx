# UAS image recognition for Surrey team Peryton 2021

- If you want to change code, make another branch and create a merge request so I can review the changes


See main.py for the entry point into the program

use 
```
pip install -r requirements.txt
```
to install the modules used. A decent amount of them are unneccesary for this project but that's what pip freeze does 🤷‍♀️

The dataset can be found on the peryton teams.
The raw source for this dataset is found at https://www.sensefly.com/education/datasets/?dataset=1502


I could organise things into modules... ideally you'd have an app module with sub modules, however this works for now

- doing this makes it harder to test individual components.. (you can't run the script directly as own module imports don't work)

- but then we could initialise global objects in __init__ which is a bit more pythonic / nice


