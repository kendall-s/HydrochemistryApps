# Hydrochemistry Applications

![Tests](https://github.com/kendall-s/HydrochemistryApps/workflows/Python%20Commit%20Test/badge.svg)


### todo
- incorporate automated tests (done for DO app)
- little bit of refactoring required throughout
- change cpu intensive apps to be non-blocking (put calcs on new thread)

## Technical 
### Application Packaging
Automated Github actions have been setup to enable the cloud building of the Hydrochemistry Apps. 
The build workflow will be triggered whenever a new "release" tag is pushed to the repo. A release tag is denoted as 
beginning with a v, e.g. v1.5.1

```editorconfig
git tag "v1.1.1"
git push -u origin "v1.1.1"
```


### Technologies Used
The application is built 100% using Python, making significant use of PyQt5 for the GUI aspect.  

---

## Hydrochemistry Background

This collection of small applications are used for making day-to-day hydrochemistry data processing tasks easier and more straightforward.

The applications are housed within a unified "launcher" allowing one program to be launched and multiple uses available.

## Applications Included

### Dissolved Oxygen Calculator
This is an glorified calculator for re-calculating final dissolved oxygen values. All of the values that contribute to 
the dissolved oxygen result can be changed. Exporting of different file formats can also be done.

### QC Table Reader
The Matlab version of HyPro can output a .csv of results, referred to in HyPro as the QC Table. QC Table reader can 
parse the file and generate various statistics or isolate the results that are being investigated.

### Hydrology Data QCer
Hydrology Data QCer can be used to quickly complete a final data check on the output Hydrochemistry data from HyPro. 
The app allows the user to load in the final output files, make comparisons and quickly plot the data for visual verification. 

### AACE Base Offset Plot
This utility can quickly plot the instrument baseline offset across a voyage when it is shown a folder container the 
nutrient .SLK files. Plotting of the baseline offset allows for checking of instrument performance or flowcell wear.

### Analyte Normality
When making stock standards for both nutrients and dissolved oxygen, the accurate normality will need to be calculated. 
This application can calculate the normality accounting for all environmental variables. 

### Glass Calibration
When calibrating glass volumetrics, this calculator can be used to get an accurate result. Again this accounts for all 
environmental variables when calculating.

### NC Checker
For ensuring the data between the final .csv and .nc files output from HyPro this application can be used. It is an 
automated process where all the user has to do it input the .csv and the folder of the .nc files. Any differences will 
highlighted. 

### SLK Time Stamps
Occasionally the nutrient analyser acquisition software will not output time stamps in the .SLK file. This is typically 
not an issue, however when using the underway AA100 time stamps will be required. This app allows for time stamps that 
match the usual format. 
