# WireLabelGenerator

## Overview

This GUI application lets you generate Dymo style labels for each wire in a given wiring harness. Simply select the excel file containing the cut list for the wiring harness, data from the cut list will be used to generate labels for each wire / bundle. The part number and customer name is pulled from the filename using this coonvention: `<part number> <customer>.xlsx`. If the customer name is not found in the filename, the user will be prompted to enter the customer name.

Before loading the excel file, the user can specify the total number of harasses they are cutting and the desired batch size. Using this information, the application will calculate the number of labels that will be printed for each wire / bundle. After loading the excel file, a table with the wire / bundle information will be displayed. The user can then select the wire they want to generate labels for and click the `Print Selected` button. The application will then generate the labels and print them to the selected Dymo printer, using the `WireBundleLabel.label` template saved under `templates` folder. After printing the labels, the highlighted wire will be removed from the table. Clicking the `Reload` button will reload the table with the selected file and recalculate the number of labels for each wire.

## Installation
