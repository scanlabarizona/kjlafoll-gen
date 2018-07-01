auditbuilder.py
================

Performs an automated search of the SCANLab shared drive for self-auditing PREEMPT data entry.
Creates an excel spreadsheet called 'Data_Entry_Audit' with columns for each searched for file
and rows for subjects specified as having either completed V1, V2, or dropped out. Records files
as found with a 1 and formats cells as green, and missing files with a 0 and formats cells as red.
Package script with pyinstaller (and appropriate hooks specified) to simplify.
I wrote this script to eliminate human error in our data entry protocol.
