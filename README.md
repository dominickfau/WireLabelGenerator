# WireLabelGenerator

## Overview

This GUI application lets you generate Dymo style labels for each wire in a given wiring harness. Simply select the excel file containing the cut list for the wiring harness, data from the cut list will be used to generate labels for each wire / bundle. The part number and customer name is pulled from the filename using this coonvention: `<part number> <customer>.xlsx`. If the customer name is not found in the filename, the user will be prompted to enter the customer name.

Before loading the excel file, the user can specify the total number of harasses they are cutting and the desired batch size. Using this information, the application will calculate the number of labels that will be printed for each wire / bundle. After loading the excel file, a table with the wire / bundle information will be displayed. The user can then select the wire they want to generate labels for and click the `Print Selected` button. The application will then generate the labels and print them to the selected Dymo printer, using the `WireBundleLabel.label` template saved under `templates` folder. After printing the labels, the highlighted wire will be removed from the table. Clicking the `Reload` button will reload the table with the selected file and recalculate the number of labels for each wire. Clicking the `Print Previous` button will print a single label for the previously selected wire. Clicking the `Print Single` button will print a single label for the selected wire, this will not remove the selected wire from the table.

## Installation

Download the latest version of the application from [GitHub](https://github.com/dominickfau/WireLabelGenerator/releases). Extract the contents of the zip file and run the `Wire Label Generator.exe` file.

## Settings and Configuration

All settings and configuration are saved to the windows registry. The hive key is `HKEY_CURRENT_USER\SOFTWARE\DF-Software\Wire Cutting Label Generator`. Below is a list of the settings and their default values.

| Setting                          | Default Value | Description                                                                                                                                                    |
| -------------------------------- | ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| initial_cut_sheet_directory      | None string   | This is an optional setting that can be used to specify the initial directory for the cut sheet file.                                                          |
| Logging\log_level                | 20 decimal    | This setting controls the level of logging. The default value is 20. Valid values are 0 to 100. 10 = Critical, 20 = Error, 30 = Warning, 40 = Info, 50 = Debug |
| Logging\max_log_count            | 3 decimal     | All log files are saved in a rotating fashion. This setting controls the number of log files to keep. The default value is 3.                                  |
| Logging\max_log_size_mb          | 5 decimal     | This setting controls the maximum size of each log file in megabytes. The default value is 5.                                                                  |
| MainWindow\selected_printer_name | None string   | This setting saves the last selected printer name.                                                                                                             |
| Program\debug                    | false boolean | This setting controls whether the application will run in debug mode. The default value is false.                                                              |
| Program\disable_label_printing   | false boolean | This setting controls whether the application will print labels. The default value is false. If set to true, label data will be logged.                        |
| Program\remove_printed_labels    | false boolean | This setting controls whether the application will remove labels from the table after printing. The default value is false.                                    |
| User\first_name                  | None string   | This setting saves the first name of the last user to use the application.                                                                                     |
| User\last_name                   | None string   | This setting saves the last name of the last user to use the application.                                                                                      |

## Excel File Format

An excel file containing the cut list for a wiring harness must have the following columns:

| Sheet Name | Column Name    | Data Type | Description                                  |
| ---------- | -------------- | --------- | -------------------------------------------- |
| Cut List   | Qty            | Integer   | The number of pieces required for this wire. |
| Cut List   | Gauge          | Integer   | The gauge of the wire.                       |
| Cut List   | Type           | String    | The type of wire. IE. GPT, GXL, etc          |
| Cut List   | Color          | String    | The color of the wire.                       |
| Cut List   | Length         | Integer   | The length of the wire in inches.            |
| Cut List   | Left Strip     | float     | The length of the left strip in inches.      |
| Cut List   | Left Gap       | float     | The length of the left gap in inches.        |
| Cut List   | Right Gap      | float     | The length of the right gap in inches.       |
| Cut List   | Right Strip    | float     | The length of the right strip in inches.     |
| Cut List   | Left Terminal  | String    | The left terminal.                           |
| Cut List   | Right Terminal | String    | The right terminal.                          |

A template for the excel file can be found in the `templates` folder.
