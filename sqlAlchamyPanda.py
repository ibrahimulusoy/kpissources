from sqlalchemy import create_engine, MetaData, Table
import pandas as pd
from flask import session

#from BaseServices import Bases

SERVER = 'DESKTOP-LK1MSPB\SQLEXPRESS' 
DATABASE = 'HPS_METRICS_QA' 
USERNAME = 'sa' 
PASSWORD = 'sa' 
DRIVER='SQL Server Native Client 11.0'
DATABASE_CONNECTION = f'mssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}' 



def getRowsFromCsv(fileName):
    df = pd.read_csv(fileName)
    return df

def getRowsFromXls(fileName, partial, typeDC, sheetIndex):
    if partial == 'Y':
        if typeDC == "D":
            #cols = [0, 1, 2, 3, 5, 7, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19]
            cols = ['Term_RowID', 'KPI_RowID', 'Category_RowID', 'Department_RowID', 'Is_KPI_Applicable', 'Adjusted_Weight', 
                    'District_RowID', 'Adjusted_Score', 'Score', 'Raw_Score', 'Raw_Score_Details', 'Artifact_URL']
        elif typeDC == "C":
            #cols = [0, 1, 3, 5, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20]
            cols = ['Term_RowID', 'KPI_RowID', 'Category_RowID', 'Department_RowID', 'District_RowID', 'Campus_RowID', 'Is_KPI_Applicable', 
                    'Adjusted_Weight', 'Adjusted_Score', 'Score', 'Raw_Score', 'Raw_Score_Details', 'Artifact_URL']

        df = pd.read_excel(fileName, sheet_name = sheetIndex, usecols = cols)
    else:
        df = pd.read_excel(fileName, sheet_name = sheetIndex)
    
    #df['RowID'] = None
    df['CorpID'] = session['CorpID']
    df['DmlUserID'] = session['UserID']

    df.head()
    return df

def getAllSheetsFromXls(fileName, partial, typeDC):
    if partial == 'Y':
        if typeDC == "D":
            #cols = [0, 1, 2, 3, 5, 7, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19]
            cols = ['Term_RowID', 'KPI_RowID', 'Category_RowID', 'Department_RowID', 'Is_KPI_Applicable', 'Adjusted_Weight', 
                    'District_RowID', 'Adjusted_Score', 'Score', 'Raw_Score', 'Raw_Score_Details', 'Artifact_URL']
        elif typeDC == "C":
            #cols = [0, 1, 3, 5, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20]
            cols = ['District_RowID', 'Campus_RowID', 'Term_RowID', 'KPI_RowID', 'Category_RowID', 'Department_RowID', 'Is_KPI_Applicable', 
                    'Adjusted_Weight', 'Adjusted_Score', 'Score', 'Raw_Score', 'Raw_Score_Details', 'Artifact_URL']

        df = pd.read_excel(fileName, sheet_name = None, usecols = cols)
    else:
        df = pd.read_excel(fileName, sheet_name = None)
    
    sheetCount = 8
    with pd.ExcelFile(fileName) as xls:
        for i in range(0, sheetCount - 1):
            df = pd.read_excel(xls, i)
            if i == 0:
                dfAll = df
            else:
                dfAll = pd.concat([dfAll, df])
        
        # df['RowID'] = None
        df['CorpID'] = 1
        df['DmlUserID'] = 1

    df.head()
    return df    

def getRowsFromXlsFirst(fileName, partial, typeDC):
    if partial == 'Y':
        if typeDC == "D":
            #cols = [0, 1, 2, 3, 5, 7, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19]
            cols = ['RowID', 'CorpID', 'Term_RowID', 'KPI_RowID', 'Category_RowID', 'Department_RowID', 'Is_KPI_Applicable', 'Adjusted_Weight', 
                    'District_RowID', 'Adjusted_Score', 'Score', 'Raw_Score', 'Raw_Score_Details', 'Artifact_URL', 'DmlUserID']
        elif typeDC == "C":
            #cols = [0, 1, 3, 5, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20]
            cols = ['CorpID', 'District_RowID', 'Campus_RowID', 'Term_RowID', 'KPI_RowID', 'Category_RowID', 'Department_RowID', 'Is_KPI_Applicable', 
                    'Adjusted_Weight', 'Adjusted_Score', 'Score', 'Raw_Score', 'Raw_Score_Details', 'Artifact_URL', 'DmlUserID', 'DmlDateTime']

        df = pd.read_excel(fileName, usecols = cols)
    else:
        df = pd.read_excel(fileName)
    df.head()
    return df

def insertFactKPI(df: pd.DataFrame, tableName):
    engine = create_engine(DATABASE_CONNECTION)
    sqlDBConn = engine.connect()
    df.to_sql(tableName, sqlDBConn, if_exists='append', index = False)


def delKPIOldRecords(CorpID, District_RowID, Term_RowID, KPI_RowID):
    engine = create_engine(DATABASE_CONNECTION)
    sqlDBConn = engine.connect()
    sql = 'DELETE Fact_KPI WHERE CorpID = ? and Term_RowID = ? and KPI_RowID = ? and District_RowID = ? '
    sqlDBConn.execute(sql, CorpID, Term_RowID, KPI_RowID, District_RowID)

def delKPIOldRecords2(CorpID, Term_RowID, District_RowID):
    engine = create_engine(DATABASE_CONNECTION)
    sqlDBConn = engine.connect()
    sql = 'DELETE Fact_KPI WHERE CorpID = ? and Term_RowID = ? and District_RowID = ? '
    sqlDBConn.execute(sql, CorpID, Term_RowID, District_RowID)


def delKPICampusOldRecords(CorpID, Department_RowID, Campus_RowID, Term_RowID):
    engine = create_engine(DATABASE_CONNECTION)
    sqlDBConn = engine.connect()
    sql = 'DELETE Fact_KPI_Campus WHERE CorpID = ? and Term_RowID = ? and Department_RowID = ? and Campus_RowID = ?'
    sqlDBConn.execute(sql, CorpID, Term_RowID, Department_RowID, Campus_RowID)


def delKPICampusOldRecords2(CorpID, Term_RowID, Department_RowID):
    engine = create_engine(DATABASE_CONNECTION)
    sqlDBConn = engine.connect()
    sql = 'DELETE Fact_KPI_Campus WHERE CorpID = ? and Term_RowID = ? and Department_RowID = ?'
    sqlDBConn.execute(sql, CorpID, Term_RowID, Department_RowID)


def get_districtsX():
    engine = create_engine(DATABASE_CONNECTION)
    sqlDBConn = engine.connect()

    data = pd.read_sql_query("SELECT OrderNo, District, DistrictShort  FROM dbo.Dim_District;", sqlDBConn)
    # data = pd.read_sql_table("dim_district", con=sqlDBConn)
    # df = pd.DataFrame(data, columns=['OrderNo','District'])
    sqlDBConn.close()
    return data


def get_all_tasks():
    engine = create_engine(DATABASE_CONNECTION)
    sqlDBConn = engine.connect()

    # cols = ['row_id', 'corp_id', 'user_id', 'task_id', 'description', 'as_by_user_id', 'as_date_time', 'del_date_time']#

    data = pd.read_sql_query("""SELECT tu.row_id, tu.corp_id, tu.user_id, u.full_name, d.Department, tu.task_id, t.name task_name, tu.description, task_url, as_by_user_id,
                                    FORMAT(tu.as_date_time, 'D', 'en-US') AS as_date_time, FORMAT(tu.del_date_time, 'D', 'en-US') AS del_date_time
                                FROM dbo.Dim_Task_User tu
                                JOIN dbo.Dim_task t ON tu.task_id = t.task_id
                                JOIN dbo.Dim_Users u ON tu.user_id = u.user_id
                                LEFT JOIN dbo.Dim_Department d ON u.department_id = d.RowID""", sqlDBConn)
    
    sqlDBConn.close()
    return data



def insertDimTaskUser():
    engine = create_engine(DATABASE_CONNECTION)
    sqlDBConn = engine.connect()
    sql = """DELETE FROM dbo.Dim_Assigned_Tasks;

            INSERT INTO dbo.Dim_Assigned_Tasks 
            SELECT 1, user_id, task_id, description, NULL, 1, GETDATE()
              FROM dbo.Dim_Task_User
             ORDER BY task_id"""
    sqlDBConn.execute(sql)
