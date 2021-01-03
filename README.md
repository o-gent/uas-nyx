# UAS image recognition for Surrey team Peryton 2021

- If you want to change code, make another branch and create a merge request so I can review the changes

See main.py for the entry point into the program

I could organise things into modules... ideally you'd have an app module with sub modules, however this works for now

- doing this makes it harder to test individual components.. (you can't run the script directly as own module imports don't work)

- but then we could initialise global objects in __init__ which is a bit more pythonic / nice
