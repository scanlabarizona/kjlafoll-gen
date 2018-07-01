#Author: Kyle J. LaFollette
#Department of Psychiatry, University of Arizona
#Correspondance: kjlafoll@psychiatry.arizona.edu

#Generates an excel spreadsheet for self-auditing PREEMPT data entry.
#Must be connected to shared drive to run script

import os
import pandas as pd
import csv
import win32com.client
import xlsxwriter

print("Collecting Files...")
root = "S:\\Killgore_SCAN\\UA_SCAN_Shared\\PREEMPT\\"
#Check if connected to shared drive. If not, exit program
if not os.path.exists("S:\\Killgore_SCAN\\UA_SCAN_Shared\\PREEMPT\\"):
	print('Connect to Shared Drive and restart program.')
	ExitProgramWarn = str(input("Processes completed. Press ENTER to exit program."))
	exit()
#Build a list of all files and their respective paths in the PREEMPT folder
dumplist = []
for p, s, f in os.walk(root):
    for n in f:
        dumplist.append(os.path.join(p, n))

#Open subject masterlist. Masterlist is encrypted, so set 'Password' to workbook password
xlApp = win32com.client.Dispatch('Excel.Application')
masterobject = xlApp.Workbooks.Open(root + "Tracking_Storage_Scheduling_Logs\\PREEMPT_Subject_Masterlist.xlsx", False,
                                    True, None, Password='').Worksheets(1)
#Build dataframe with first 19 columns of masterlist cells and all used rows (all subjects)
masterlist = pd.DataFrame(
    list(masterobject.Range(masterobject.Cells(1, 1), masterobject.Cells(masterobject.UsedRange.Rows.Count, 19)).Value))
masterlist.columns = masterlist.iloc[0]
masterlist.reindex(masterlist.index.drop(0))
#Build list of subjects' record IDs that are listed as either having completed V2, V1 or dropped out
subslist = list(masterlist[(masterlist.Status == 'V2 Complete') | (masterlist.Status == "V1 Complete") | (
            masterlist.Status == "Drop Out")]['Record ID'].astype(int))
subslist.sort()

print("Writing DataFrame...")
#Build a sublist of files within the PREEMPT folder that are also in Data and a specific subject data folder (i.e., PREEMPT1_0001)
fileslist = [x for x in dumplist if "UA_SCAN_Shared\\PREEMPT\\Data\\PREEMPT1_" in x]
#Remove files from fileslist if they are not from the data folders of subjects specified in subslist
fileslist[:] = [x for x in fileslist if any("PREEMPT1_%04d" % y in x for y in subslist)]

#Dictionary of files to search for and their file paths. To add additional files to this script, append the dictionary before 'status' with additional keys and values in the format of '[[path, keyword],0,[]]'. Keyword is a specific string to search for in the filename.
datalist = {'hrv1':[["HRV\\PREEMPT1_%04d_Day1"],0,[]],
            'hrv2':[["HRV\\PREEMPT1_%04d_Day2"],0,[]],
            'cvltc1':[["PREEMPT1_%04d\\Raw Data\\cvlt", "copy1"],0,[]],
            'cvltc2':[["PREEMPT1_%04d\\Raw Data\\cvlt", "copy2"],0,[]],
            'eqi':[["PREEMPT1_%04d\\Raw Data\\eqi2"],0,[]],
            'msceit':[["PREEMPT1_%04d\\Raw Data\\msceit"],0,[]],
            'neoc1':[["PREEMPT1_%04d\\Raw Data\\neo", "copy1"],0,[]],
            'neoc2':[["PREEMPT1_%04d\\Raw Data\\neo", "copy2"],0,[]],
            'staxic1':[["PREEMPT1_%04d\\Raw Data\\staxi", "copy1"],0,[]],
            'staxic2':[["PREEMPT1_%04d\\Raw Data\\staxi", "copy2"],0,[]],
            'wasic1':[["PREEMPT1_%04d\\Raw Data\\wasi", "copy1"],0,[]],
            'wasic2':[["PREEMPT1_%04d\\Raw Data\\wasi", "copy2"],0,[]],
            'status':[],
            'missing':[]
            }
totfiles = 12

for x in subslist:
    datalist['status'].append(masterlist.loc[masterlist['Record ID'] == x, 'Status'].iloc[0])

for i, x in enumerate(subslist):
    subtrahend = 0 #Total number of missing files for subject x
    for z in range(0,len(list(datalist.keys()))-2): #Loop through each key in the datalist, minus 'status' and 'missing'
        key = datalist[list(datalist.keys())[z]]
        for y in fileslist:
            if len(key[0]) == 1: #If only a path is specified and no keyword is required
                if (key[0][0] % x in y): #If path specified in datalist can be found in file
                    key[2].append(1) #Found it!
                    key[1] = 1 #Mark file as found in the datalist
                else:
                    key[1] = 0 #Keep file marked as not found in datalist
            elif len(key[0]) == 2: #If both a path and keyword are specifed in datalist
                if (key[0][0] % x in y) and (key[0][1] in y): #If both the path and keyword specified can be found in file
                    key[2].append(1) #Found it!
                    key[1] = 1 #Mark file as found in the datalist
                else:
                    key[1] = 0 #Keep file marked as not found in datalist
            if key[1] == 1: #If you found the file, stop searching the fileslist and go on to the next key in datalist
                break
        if key[1] == 0: #Didn't find it
            key[2].append(0)
        key[1] = 0 #Reset key marker to 'not found' for next subject in the loop
        subtrahend += key[2][i] #Add '1' to the total number of missing files for subject x if file was not found
    datalist['missing'].append(totfiles-subtrahend)

for i, x in enumerate(subslist):
    subslist[i] = "%04d" % x
table = pd.DataFrame(
    {'Record ID': subslist,
     'HRV_D1': datalist['hrv1'][2],
     'HRV_D2': datalist['hrv2'][2],
     'CVLT_C1': datalist['cvltc1'][2],
     'CVLT_C2': datalist['cvltc2'][2],
     'EQI': datalist['eqi'][2],
     'MSCEIT': datalist['msceit'][2],
     'NEO_C1': datalist['neoc1'][2],
     'NEO_C2': datalist['neoc2'][2],
     'STAXI_C1': datalist['staxic1'][2],
     'STAXI_C2': datalist['staxic2'][2],
     'WASI_C1': datalist['wasic1'][2],
     'WASI_C2': datalist['wasic2'][2],
     'Status': datalist['status'],
     'MISSING ENTRIES': datalist['missing']
     })

writer = pd.ExcelWriter(root + "Tracking_Storage_Scheduling_Logs\\Data_Entry_Audit.xlsx", engine='xlsxwriter')
table.to_excel(writer, 'Sheet_1', index=False)
workbook = writer.book
worksheet = writer.sheets['Sheet_1']
red_format = workbook.add_format({'bg_color': '#FFACB9'})
green_format = workbook.add_format({'bg_color': '#00B050'})
blue_format = workbook.add_format({'bg_color': '#00B0F1'})
lgreen_format = workbook.add_format({'bg_color': '#C5D69C'})

worksheet.conditional_format('B2:M%s' % (len(table) + 1), {'type': 'text',
                                                           'criteria': 'containing',
                                                           'value': '0',
                                                           'format': red_format})
worksheet.conditional_format('B2:M%s' % (len(table) + 1), {'type': 'text',
                                                           'criteria': 'containing',
                                                           'value': '1',
                                                           'format': green_format})
worksheet.conditional_format('N2:N%s' % (len(table) + 1), {'type': 'text',
                                                           'criteria': 'containing',
                                                           'value': 'V2 Complete',
                                                           'format': lgreen_format})
worksheet.conditional_format('N2:N%s' % (len(table) + 1), {'type': 'text',
                                                           'criteria': 'containing',
                                                           'value': 'V1 Complete',
                                                           'format': blue_format})
worksheet.conditional_format('A2:A%s' % (len(table) + 1), {'type': 'formula',
                                                           'criteria': '=N2:N%s="V1 Complete"' % (len(table) + 1),
                                                           'format': blue_format})
worksheet.conditional_format('A2:A%s' % (len(table) + 1), {'type': 'formula',
                                                           'criteria': '=N2:N%s="V2 Complete"' % (len(table) + 1),
                                                           'format': lgreen_format})
writer.save()

newobject = xlApp.Workbooks.Open(root + "Tracking_Storage_Scheduling_Logs\\Data_Entry_Audit.xlsx", False,
                                    True, None).Worksheets(1)

ExitProgramWarn = str(input("Processes completed. Press ENTER to exit program."))