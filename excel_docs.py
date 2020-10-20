import os
import sys
from flask import session
import pyexcel
from pyexcel_xlsxw import save_data
from pyexcel_io import get_data
from collections import OrderedDict
from pyOdbcDBLayer import get_district_KPI_list_for_entry, get_districts, get_campus, get_new_row_id_fact_kpi, get_campus_KPI_list_for_entry


def prepare_excel_docs_for_districts(DepartmentRowID, defDir):
    fileName = defDir + "KPI_District_Scores_Dept_" +  str(DepartmentRowID) + "_Term_" + str(session['TermKey']) + ".xlsx"
    data = OrderedDict() # from collections import OrderedDict
    v_dist = get_districts()
    for rowD in v_dist:
        vDistRowID = rowD[0]
        vDistName = rowD[6]
        sheetName = vDistName.replace('*', '')
        sheetName = sheetName.replace('?', '')
        sheetName = sheetName.replace('/', '')
        sheetName = sheetName.replace("\\", '')

        dataContent = [["Term_RowID", "KPI_RowID", "KPI_Name", "Category_RowID", "Category_Name", "Department_RowID", "Department_Name", 
                            "Is_KPI_Applicable", "Adjusted_Weight", "District_RowID", "District_Name",  "Adjusted_Score", "Score", "Raw_Score", 
                            "Raw_Score_Details", "Artifact_URL"]]

        # getting dept + dist KPI list
        v_kpi = get_district_KPI_list_for_entry(session['TermKey'], DepartmentRowID, vDistRowID, vDistName)
        #NewRowID = get_new_row_id_fact_kpi('Fact_KPI')

        for rowKPI in v_kpi:
            #NewRowID = NewRowID + 1
            dataContent.append([rowKPI[2], rowKPI[3], rowKPI[4], rowKPI[5], rowKPI[6], rowKPI[7], rowKPI[8], 
                                rowKPI[9], rowKPI[10], rowKPI[11], rowKPI[12], rowKPI[13], 0, rowKPI[15], rowKPI[16], rowKPI[17]])

            data.update({sheetName: dataContent})
        save_data(fileName, data)
    return fileName
    

def prepare_excel_docs_for_districts2(DepartmentRowID):
    data = OrderedDict() # from collections import OrderedDict
    #data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    v_dist = get_districts()
    for rowD in v_dist:
        vDistRowID = rowD[0]
        vDistName = rowD[6]
        sheetName = vDistName.replace('*', '')
        sheetName = sheetName.replace('?', '')
        sheetName = sheetName.replace('/', '')
        sheetName = sheetName.replace("\\", '')

        data = [["RowID", "CorpID", "Term_RowID", "KPI_RowID", "KPI_Name", "Category_RowID", "Category_Name", "Department_RowID", "Department_Name", 
                            "Is_KPI_Applicable", "Adjusted_Weight", "District_RowID", "District_Name",  "Adjusted_Score", "Score", "Raw_Score", 
                            "Raw_Score_Details", "Artifact_URL"]]
        
        # getting dept + dist KPI list
        v_kpi = get_district_KPI_list_for_entry(DepartmentRowID, vDistRowID, vDistName)
        roww = get_new_row_id_fact_kpi('Fact_KPI')
        NewRowID = roww.NewRowId

        # data = [[1, 2, 3], [4, 5, 6]]
#        for rowKPI in v_kpi:
#            NewRowID = NewRowID + 1
#            data.update({sheetName: [[NewRowID, rowKPI[1], rowKPI[2], rowKPI[3], rowKPI[4], rowKPI[5], rowKPI[6], rowKPI[7], rowKPI[8], 
#                            rowKPI[9], rowKPI[10], rowKPI[11], rowKPI[12], rowKPI[13], 0, rowKPI[15], rowKPI[16], rowKPI[17],]]})

    pyexcel.save_as(array=data, sheetName = sheetName, dest_file_name="D://PROJECTS/USA/HPS/documents/Department_" + str(DepartmentRowID) + "_KPI3.xlsx")
    
    
def prepare_excel_docs_for_campuses(TermID, DepartmentRowID, defDir):
    xlsFile = defDir + "KPI_Campus_Scores_Dept_" +  str(DepartmentRowID) + "_Term_" + str(TermID) + ".xlsx"
    data = OrderedDict() # from collections import OrderedDict
    v_cmp = get_campus()

    for rowD in v_cmp:
        vCmpRowID = rowD[0]
        vCmpName = rowD[9]
        sheetName = vCmpName.replace('*', '')
        sheetName = sheetName.replace('?', '')
        sheetName = sheetName.replace('/', '')
        sheetName = sheetName.replace("\\", '')

        vDistRowID = rowD[3]
        vDistName = rowD[5]

        dataContent = [["Term_RowID", "KPI_RowID", "KPI_Name", "Category_RowID", "Category_Name", "Department_RowID", "Department_Name", 
                            "District_RowID", "District_Name", "Campus_RowID", "Campus_Name", "Is_KPI_Applicable", "Adjusted_Weight",
                            "Adjusted_Score", "Score", "Raw_Score", "Raw_Score_Details", "Artifact_URL"]]
                       
                        #  NULL RowID, k.CorpID, ? Term_RowID, K.RowID AS KPI_RowID, k.KPI AS KPI_Name, c.RowID Category_RowID, c.CategoryShort AS Category_Name,
                        #  d.RowID Department_RowID, d.Department Department_Name, ? Campus_RowID, ? Campus_Name, 
                        #  w.Is_KPI_Applicable, w.Weight * w.Is_KPI_Applicable as Adjusted_Weight, 0 Adjusted_Score, 0 Score, NULL Raw_Score, NULL Raw_Score_Details, NULL Artifact_URL

        # getting dept + dist KPI list
        v_kpi = get_campus_KPI_list_for_entry(TermID, DepartmentRowID, vCmpRowID, vCmpName)
        for rowKPI in v_kpi:
            dataContent.append([rowKPI[2], rowKPI[3], rowKPI[4], rowKPI[5], rowKPI[6], rowKPI[7], rowKPI[8], 
                                vDistRowID, vDistName, rowKPI[9], rowKPI[10], rowKPI[11], rowKPI[12], 
                                rowKPI[13], rowKPI[14], rowKPI[15], rowKPI[16], rowKPI[17]])

            
            data.update({sheetName: dataContent})
        
        save_data(xlsFile, data)
    return xlsFile