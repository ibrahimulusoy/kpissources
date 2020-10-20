from flask import Flask
import pyodbc


server = 'DESKTOP-LK1MSPB\SQLEXPRESS' 
database = 'HPS_METRICS_QA' 
username = 'sa' 
password = 'sa' 

cnxn = pyodbc.connect(driver='{SQL Server Native Client 11.0}',
                               server='DESKTOP-LK1MSPB\SQLEXPRESS',
                               database='HPS_METRICS_QA',
                               uid='sa',pwd='sa')

# --------------------- CLASSES  -------------------------------------------------------------------------------------
class classPublic:
    def __init__(self, CorpID, TermKey, TermRowId, UserID, UserName, UserFullName, UserDistrictId, UserDistrictKey, UserDepartmentId, UserDepartmentKey, UserDRoleId, UserEmail):
        self.CorpID = CorpID
        self.TermKey = TermKey
        self.TermRowId = TermRowId
        self.UserID = UserID
        self.UserName = UserName
        self.UserFullName = UserFullName
        self.UserDistrictId = UserDistrictId
        self.UserDistrictKey = UserDistrictKey
        self.UserDepartmentId = UserDepartmentId
        self.UserDepartmentKey = UserDepartmentKey
        self.UserDRoleId = UserDRoleId
        self.UserEmail = UserEmail


class classTest():
    name = None
    district = 0
    row_id = 0
    key = 0

class classDistrict():
    RowID = None
    CorpID = None
    DistrictKey = None
    District = None
    DistrictShort = None
    IsActive = None
    OrderNo = None
    Weight = None
    DmlUserID = None

class classCampus():
    RowID = None
    CorpID = None
    CampusKey = None
    District_RowID = None
    Integration_DistrictID = None
    DistrictName = None
    Campus = None
    CampusShort = None
    Campus_Weight = None
    IsActive = None
    DmlUserID = None

class classDepartment():
    RowID = None
    CorpID = None
    DepartmentKey = None
    Department = None
    DepartmentShort = None
    Description = None
    Weight = None
    OrderNo = None
    Version = None
    IsActive = None
    DmlUserID = None

class classKPI():
    RowID = None
    CorpID = None
    KPIKey = None
    DepartmentKey = None
    CategoryKey = None
    KPISelfLink = None
    Version = None
    KPI = None
    Version = None
    Description = None
    Weight = None
    DisplayOrder = None
    ScoreDefinition = None
    ScoreCalculationDetails = None
    IsActive = None
    DmlUserID = None

# --------------------- END CLASSES  -------------------------------------------------------------------------------------


# --------------------- HOME  -------------------------------------------------------------------------------------
def get_general_params(CorpId):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT p.*, t.Term, pp.*, CASE pp.process_status WHEN 'A' THEN 'STARTED' WHEN 'P' THEN 'COMPLETED' ELSE 'PASSIVE' END status_text
                        FROM dbo.Dim_General_Params p
                        JOIN dbo.Dim_Term t ON t.TermKey = p.current_semestre_key AND p.corp_id = t.CorpID
                        LEFT JOIN dbo.Dim_Process_Params pp ON pp.corp_id = p.corp_id
                       WHERE p.corp_id = ?""", CorpId) 
    rows = cursor.fetchall() 
    return rows

def get_user_info(CorpId, UserId):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT user_id AS UserID, user_name AS UserName, full_name AS UserFullName, d.RowID AS DepartmentRowID, d.DepartmentKey, dt.RowID AS DistrictRowID, dt.DistrictKey
                        FROM dbo.Dim_Users u 
                        LEFT JOIN dbo.Dim_Department d ON d.CorpID = u.corp_id AND d.RowID = u.department_id
                        LEFT JOIN dbo.Dim_District dt ON dt.CorpID = u.corp_id AND dt.RowID = u.district_id
                       WHERE u.corp_id = ?
                         AND user_id = ?""", CorpId, UserId) 
    rows = cursor.fetchone() 
    return rows

def get_user_by_name_email(CorpId, UserInfo):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT user_id AS UserID, user_name AS UserName, full_name AS UserFullName, e_mail AS UserEmail, d.RowID AS DepartmentRowID, d.DepartmentKey, dt.RowID AS DistrictRowID, dt.DistrictKey
                        FROM dbo.Dim_Users u 
                        LEFT JOIN dbo.Dim_Department d ON d.CorpID = u.corp_id AND d.RowID = u.department_id
                        LEFT JOIN dbo.Dim_District dt ON dt.CorpID = u.corp_id AND dt.RowID = u.district_id
                       WHERE u.corp_id = ?
                         AND (user_name = ?
						  OR e_mail = ?)""", CorpId, UserInfo, UserInfo) 
    rows = cursor.fetchone() 
    return rows    

def task_delete(RowId):
    cursor = cnxn.cursor()
    cursor.execute("DELETE FROM dbo.Dim_Assigned_Tasks WHERE row_id = ?", RowId)
    cnxn.commit()

def task_undo(RowId):
    cursor = cnxn.cursor()
    cursor.execute("UPDATE dbo.Dim_Assigned_Tasks SET archive_date_time = NULL WHERE row_id = ?", RowId)
    cnxn.commit()

def task_to_archive(RowId):
    cursor = cnxn.cursor()
    cursor.execute("UPDATE dbo.Dim_Assigned_Tasks SET archive_date_time = GETDATE() WHERE row_id = ?", RowId)
    cnxn.commit()


def task_assign(CorpID, UserID, TermName):
    cursor = cnxn.cursor()
    cursor.execute("""DELETE FROM dbo.Dim_Assigned_Tasks;

                    INSERT INTO dbo.Dim_Assigned_Tasks 
                    SELECT ?, user_id, task_id, ? + description, NULL, ?, GETDATE()
                      FROM dbo.Dim_Task_User
                     ORDER BY task_id""", CorpID, TermName, UserID)
    cnxn.commit()
    

# --------------------- COMMON METHODS  -------------------------------------------------------------------------------------
def get_term_name(TermKey):
    cursor = cnxn.cursor()
    cursor.execute("SELECT Term FROM dbo.Dim_Term WHERE TermKey = ?", TermKey) 
    rows = cursor.fetchone() 
    return rows[0]

def get_term_key(TermName):
    cursor = cnxn.cursor()
    cursor.execute("SELECT TermKey FROM dbo.Dim_Term WHERE Term = ? OR TermShort = ?", TermName, TermName) 
    rows = cursor.fetchone() 
    return rows[0]


def get_current_term():
    cursor = cnxn.cursor()
    cursor.execute("""SELECT t.*, p.corp_id CurrentCorpID
                        FROM dbo.Dim_Term t
                        JOIN dbo.Dim_General_Params p ON t.TermKey = p.current_semestre_key""") 
    rows = cursor.fetchone() 
    return rows

def get_year_term_list(Year):
    cursor = cnxn.cursor()
    cursor.execute("SELECT RowID, TermKey, SchoolYear, TermShort, Term FROM dbo.Dim_Term WHERE SchoolYear = ? ORDER BY OrderNo", Year) 
    rows = cursor.fetchone() 
    return rows


def get_district_name(DistKey):
    cursor = cnxn.cursor()
    cursor.execute("SELECT District FROM dbo.Dim_District WHERE DistrictKey = ?", DistKey) 
    rows = cursor.fetchone() 
    return rows[0]

def get_department_name(DeptKey):
    cursor = cnxn.cursor()
    cursor.execute("SELECT Department FROM dbo.Dim_Department WHERE DepartmentKey = ?", DeptKey) 
    rows = cursor.fetchone() 
    return rows[0]

def get_campus_name(CampusKey):
    cursor = cnxn.cursor()
    cursor.execute("SELECT CampusShort FROM dbo.Dim_Campus WHERE CampusKey = ?", CampusKey) 
    rows = cursor.fetchone() 
    return rows[0]

def get_category_name(CatKey):
    cursor = cnxn.cursor()
    cursor.execute("SELECT CategoryShort Name FROM dbo.Dim_Category WHERE CategoryKey = ?", CatKey) 
    rows = cursor.fetchone() 
    return rows[0]

def get_category_rowid(CatKey):
    cursor = cnxn.cursor()
    cursor.execute("SELECT RowID Name FROM dbo.Dim_Category WHERE CategoryKey = ?", CatKey) 
    rows = cursor.fetchone() 
    return rows[0]

def get_district_count():
    cursor = cnxn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dbo.Dim_district WHERE isActive = 0") 
    rows = cursor.fetchone() 
    return rows[0]

def get_campus_count():
    cursor = cnxn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dbo.Dim_campus") 
    rows = cursor.fetchone() 
    return rows[0]

def get_download_file_path():
    cursor = cnxn.cursor()
    cursor.execute("SELECT download_file_path FROM dbo.Dim_Process_Params") 
    rows = cursor.fetchone() 
    return rows[0]

def get_archive_file_path():
    cursor = cnxn.cursor()
    cursor.execute("SELECT archive_file_path FROM dbo.Dim_Process_Params") 
    rows = cursor.fetchone() 
    return rows[0]

def get_user_pswd(UserID):
    cursor = cnxn.cursor()
    cursor.execute("SELECT password Term FROM dbo.Dim_Users WHERE user_id = ?", UserID) 
    rows = cursor.fetchone() 
    return rows[0]

def change_pwd(UserID, NewP):
    cursor = cnxn.cursor()
    cursor.execute("UPDATE dbo.Dim_Users SET password = NewP WHERE user_id = ?", NewP, UserID)
    cnxn.commit()


# --------------------- DEFINITIONS -------------------------------------------------------------------------------------
def get_corporation(corpId):
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM dbo.Dim_Corporation WHERE corp_id = ?", corpId) 
    row = cursor.fetchall()
    return row


def get_districts():
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM dbo.Dim_District WHERE isActive = 1 ORDER BY OrderNo") 
    rows = cursor.fetchall() 
    return rows

def update_district(RowId, NewWeight):
    cursor = cnxn.cursor()
    cursor.execute("UPDATE dbo.Dim_district SET Weight = CAST(ROUND(?, 2) AS decimal(2,1)) WHERE RowID = ?", NewWeight, RowId)
    cnxn.commit()


def get_categories():
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM dbo.Dim_Category ORDER BY OrderNo") 
    rows = cursor.fetchall() 
    return rows    

def get_categories_by_department(DeptKey):
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM dbo.Dim_Category WHERE DepartmentKey = ? ORDER BY OrderNo", DeptKey) 
    rows = cursor.fetchall() 
    return rows    


def update_category(RowId, NewWeight):
    cursor = cnxn.cursor()
    cursor.execute("UPDATE dbo.Dim_Category SET Weight = ROUND(?, 1) WHERE RowID = ?", NewWeight, RowId)
    cnxn.commit()


def get_department():
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM dbo.Dim_Department ORDER BY OrderNo") 
    rows = cursor.fetchall() 
    return rows

def update_department(RowId, NewWeight):
    cursor = cnxn.cursor()
    cursor.execute("UPDATE dbo.Dim_Department SET Weight = ? WHERE RowID = ?", NewWeight, RowId)
    cnxn.commit()

def get_campus():
    cursor = cnxn.cursor()
    cursor.execute("SELECT * from dbo.Dim_Campus ORDER BY DistrictName, CampusShort") 
    rows = cursor.fetchall() 
    return rows

def get_campus_by_district(DistKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT c.*, TRIM(REPLACE(REPLACE(CampusShort, '-', ' '), DistrictName, '')) CampusCleanName
                        FROM dbo.Dim_Campus c
                        JOIN dbo.Dim_District d ON d.RowID = c.District_RowID
                        WHERE d.DistrictKey = ?
                        ORDER BY c.CampusShort""", DistKey) 
    rows = cursor.fetchall() 
    return rows

    

def update_campus(RowId, NewWeight):
    cursor = cnxn.cursor()
    cursor.execute("UPDATE dbo.Dim_Campus SET campus_weight = ? WHERE RowID = ?", NewWeight, RowId)
    cnxn.commit()

def insert_new_district(cDist):
    cursor = cnxn.cursor()
    cursor.execute("""INSERT INTO dbo.Dim_District  (RowID, CorpID, DistrictKey, IsActive, OrderNo, Weight, District, DistrictShort, DmlUserID)
                                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                                        cDist.RowID, cDist.CorpID, cDist.DistrictKey, cDist.IsActive, cDist.OrderNo, cDist.Weight, 
                                        cDist.District, cDist.DistrictShort, cDist.DmlUserID)
    cnxn.commit()

def insert_new_campus(c):
    cursor = cnxn.cursor()
    cursor.execute("""INSERT INTO dbo.Dim_Campus  (RowID, CorpID, CampusKey, District_RowID, Integration_DistrictID, IsActive, Campus_Weight, Campus, CampusShort, DmlUserID)
                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", c.RowID, c.CorpID, c.CampusKey, c.District_RowID, 
                                             c.Integration_DistrictID, c.IsActive, c.Campus_Weight, c.Campus, c.CampusShort, c.DmlUserID)
    cnxn.commit()

def insert_new_department(c):
    cursor = cnxn.cursor()
    cursor.execute("""INSERT INTO dbo.Dim_Department  (RowID, CorpID, DepartmentKey, Version, IsActive, OrderNo, Department, DepartmentShort, Weight, Description, DmlUserID)
                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", c.RowID, c.CorpID, c.DepartmentKey, c.Version, 
                                             c.IsActive, c.OrderNo, c.Department, c.DepartmentShort, c.Weight, c.Description, c.DmlUserID)
    cnxn.commit()

def insert_new_kpi(c):
    cursor = cnxn.cursor()
    cursor.execute("""INSERT INTO dbo.Dim_KPI  (RowID, CorpID, KPIKey, DepartmentKey, CategoryKey, KPISelfLink, Version, KPI, Description, 
                                                Weight, DisplayOrder, ScoreDefinition, ScoreCalculationDetails, Source, IsActive, DmlUserID)
                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", c.RowID, c.CorpID, c.KPIKey, c.DepartmentKey, c.CategoryKey, 
                                           c.KPISelfLink, c.Version, c.KPI, c.Description, c.Weight, c.DisplayOrder, c.ScoreDefinition, c.ScoreCalculationDetails, c.Source, c.IsActive, c.DmlUserID)
    cnxn.commit()

def get_kpi_by_categories(CategoryKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT RowID, KPIKey,KPI
                        FROM dbo.Dim_KPI k
                       WHERE CategoryKey = ?""", CategoryKey) 
    rows = cursor.fetchall() 
    return rows    

# END DEFINITIONS --------------------------------------------------------------------------------------------------


# ---------------------PROCESS -------------------------------------------------------------------------------------
def get_kpi_list(TermRowID):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT k.RowID, k.KPIKey, Department, Category, Version, KPI, DisplayOrder, w.Weight, IsActive 
                    FROM dbo.Dim_KPI k 
                    LEFT JOIN dbo.Dim_KPI_Weight w ON k.RowID = w.KPI_RowID
                    WHERE w.Term_RowID = ?
                    ORDER BY Department, Category, DisplayOrder""", TermRowID) 
    rows = cursor.fetchall() 
    return rows

def get_kpi_list_by_department(CorpID, TermRowID, DepartmentKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT k.RowID, k.KPIKey, Department, Category, Version, KPI, Description, DisplayOrder, w.Weight, IsActive 
                    FROM dbo.Dim_KPI k 
                    LEFT JOIN dbo.Dim_KPI_Weight w ON k.RowID = w.KPI_RowID 
                    WHERE w.Term_RowID = ?
                      AND k.DepartmentKey = ?
                    ORDER BY Department, Category, DisplayOrder""", TermRowID, DepartmentKey) 
    rows = cursor.fetchall() 
    return rows

def get_district_KPI_list_by_dist(DistRowId):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT kpi.RowID KPIRowID, kpi.KPIKey, kpi.DepartmentKey , kpi.Department, d.RowID DepartmentRowId,
                            kpi.CategoryKey, kpi.Category, c.RowID CategoryRowId, KPI KPI_Name, DisplayOrder, w.Weight, w.Is_KPI_Applicable, 
                            w.Weight * w.Is_KPI_Applicable as Adjusted_Weight, 
                            (SELECT Score 
                                FROM dbo.Fact_KPI f 
                                WHERE kpi.CorpID = f.CorpID AND Term_RowID = 10 AND kpi.RowID = f.KPI_RowID 
                                AND kpi.CategoryKey = c.CategoryKey AND kpi.DepartmentKey = c.DepartmentKey AND District_RowID = ?) AS Score
                        FROM dbo.Dim_KPI kpi 
                        JOIN dbo.Dim_KPI_Weight w ON kpi.RowID = w.KPI_RowID
                        JOIN dbo.Dim_Category c ON kpi.CategoryKey = c.CategoryKey
                        JOIN dbo.Dim_Department d ON kpi.DepartmentKey = d.DepartmentKey
                        ORDER BY Department, Category, DisplayOrder ASC""", DistRowId)
    rows = cursor.fetchall() 
    return rows

def get_district_KPI_list_all():
    cursor = cnxn.cursor()
    cursor.execute("""SELECT kpi.RowID KPIRowID, kpi.KPIKey, kpi.DepartmentKey , kpi.Department, d.RowID DepartmentRowId,
                            kpi.CategoryKey, kpi.Category, c.RowID CategoryRowId, KPI KPI_Name, DisplayOrder, w.Weight, w.Is_KPI_Applicable, 
                            w.Weight * w.Is_KPI_Applicable as Adjusted_Weight, 0 Score
                        FROM dbo.Dim_KPI kpi 
                        JOIN dbo.Dim_KPI_Weight w ON kpi.RowID = w.KPI_RowID  AND w.kpi_level = 'D'
                        JOIN dbo.Dim_Category c ON kpi.CategoryKey = c.CategoryKey
                        JOIN dbo.Dim_Department d ON kpi.DepartmentKey = d.DepartmentKey
                        ORDER BY Department, Category, DisplayOrder ASC""")
    rows = cursor.fetchall() 
    return rows

def get_campus_KPI_list_all():
    cursor = cnxn.cursor()
    cursor.execute("""SELECT kpi.RowID KPIRowID, kpi.KPIKey, kpi.DepartmentKey , kpi.Department, d.RowID DepartmentRowId,
                            kpi.CategoryKey, kpi.Category, c.RowID CategoryRowId, KPI KPI_Name, DisplayOrder, w.Weight, w.Is_KPI_Applicable, 
                            w.Weight * w.Is_KPI_Applicable as Adjusted_Weight, 0 Score
                        FROM dbo.Dim_KPI kpi 
                        JOIN dbo.Dim_KPI_Weight w ON kpi.RowID = w.KPI_RowID AND w.kpi_level = 'C'
                        JOIN dbo.Dim_Category c ON kpi.CategoryKey = c.CategoryKey
                        JOIN dbo.Dim_Department d ON kpi.DepartmentKey = d.DepartmentKey
                        ORDER BY Department, Category, DisplayOrder ASC""")
    rows = cursor.fetchall() 
    return rows    

def update_dist_kpi_score(RowId, DeptKey, CatKey, Score):
    cursor = cnxn.cursor()
    cursor.execute("""UPDATE dbo.Fact_KPI 
                         SET Score = ? 
                       WHERE KPI_RowID = ? 
                         AND Category_RowID = ?
                         AND Department_RowID = ?""", RowId, DeptKey, CatKey, Score)
    cnxn.commit()

def update_kpi_weight(RowId, NewWeight):
    cursor = cnxn.cursor()
    cursor.execute("UPDATE dbo.Dim_KPI_Weight SET Weight = ? WHERE KPI_RowID = ?", NewWeight, RowId)
    cnxn.commit()


def delete_Fact_KPI(CorpId, TermId, KPIRowId, DistrictRowId):
    cursor = cnxn.cursor()
    cursor.execute("DELETE FROM dbo.Fact_KPI WHERE CorpID = ? and Term_RowID = ? and KPI_RowID = ? and District_RowID = ?", 
                    CorpId, TermId, KPIRowId, DistrictRowId)
    cnxn.commit()

def delete_Fact_KPI_Campus(CorpId, TermId, KPIRowId, DistrictRowId, CampusRowId):
    cursor = cnxn.cursor()
    cursor.execute("DELETE FROM dbo.Fact_KPI_Campus WHERE CorpID = ? and Term_RowID = ? and KPI_RowID = ? and District_RowID = ? AND Campus_RowID = ?", 
                    CorpId, TermId, KPIRowId, DistrictRowId, CampusRowId)
    cnxn.commit()


def get_new_row_id_fact_kpi(tableName):
    cursor = cnxn.cursor()
    if tableName == "Fact_KPI": 
        row = cursor.execute("SELECT MAX(RowId) NewRowId FROM dbo.Fact_KPI").fetchone()
    elif tableName == "Fact_KPI_Campus":
        row = cursor.execute("SELECT MAX(RowId) NewRowId FROM dbo.Fact_KPI_Campus").fetchone()
    return row[0]


def insert_Fact_KPI(CorpID, TermRowID, KPIRowID, CategoryRowID, DepartmentRowID, IsKPIApplicable, DistrictRowID, Score, Weight, ArtifactURL, DmlUserID):
    # NewRowID = get_new_row_id_fact_kpi('Fact_KPI')
    v_Adjusted_Score = float(Weight * Score)
    cursor = cnxn.cursor()
    cursor.execute("""INSERT INTO dbo.Fact_KPI (CorpID, Term_RowID, KPI_RowID, Category_RowID, Department_RowID, Is_KPI_Applicable, 
                                                Adjusted_weight, Adjusted_Score, Raw_score, District_RowID, Score, Artifact_URL, DmlUserID, DmlDateTime)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())""", 
                                        CorpID, TermRowID, KPIRowID, CategoryRowID, DepartmentRowID, IsKPIApplicable, 
                                        Weight, v_Adjusted_Score, 0, DistrictRowID, Score, ArtifactURL, DmlUserID)
    cnxn.commit()

def insert_Fact_KPI_Campus(CorpID, TermRowID, KPIRowID, CampusRowID, CategoryRowID, DepartmentRowID, IsKPIApplicable, DistrictRowID, Score, Weight, ArtifactURL, DmlUserID):
    # NewRowID = get_new_row_id_fact_kpi('Fact_KPI')
    v_Adjusted_Score = float(Weight * Score)
    cursor = cnxn.cursor()
    cursor.execute("""INSERT INTO dbo.Fact_KPI_Campus (CorpID, District_RowID, Campus_RowID, Term_RowID, KPI_RowID, Category_RowID, Department_RowID, Is_KPI_Applicable, 
                                                        Adjusted_weight, Adjusted_Score, Score, Raw_score, Artifact_URL, DmlUserID, DmlDateTime)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())""", 
                                                        CorpID, DistrictRowID, CampusRowID, TermRowID, KPIRowID, CategoryRowID, DepartmentRowID, IsKPIApplicable, 
                                                        Weight, v_Adjusted_Score, Score, 0, ArtifactURL, DmlUserID)
    cnxn.commit()

def update_process_status(CorpId, Status, UserId):
    cursor = cnxn.cursor()
    if Status == 'A':
        Percent = 0
    else:
        Percent = 100
    cursor.execute("UPDATE dbo.Dim_Process_Params SET process_status = ?, start_date = GETDATE(), start_user_id = ?, complete_percent = ? WHERE corp_id = ?", Status, UserId, Percent, CorpId)
    cnxn.commit()


def get_district_KPI_list_for_entry(TermID, DepartmentID, DistrictID, DistrictName):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT NULL RowID, k.CorpID, ? Term_RowID, K.RowID AS KPI_RowID, k.KPI AS KPI_Name, c.RowID Category_RowID, c.CategoryShort AS Category_Name,
                            d.RowID Department_RowID, d.Department Department_Name, w.Is_KPI_Applicable, w.Weight * w.Is_KPI_Applicable as Adjusted_Weight,
                            ? District_RowID, ? District_Name, 0 Adjusted_Score, 0 Score, NULL Raw_Score, NULL Raw_Score_Details, NULL Artifact_URL
                        FROM dbo.Dim_KPI k
                        JOIN dbo.Dim_Category c ON c.CategoryKey = k.CategoryKey
                        JOIN dbo.Dim_KPI_Weight w ON w.KPI_RowID = k.RowID AND w.calculation_type = 'M' and w.kpi_level = 'D'
                        JOIN dbo.Dim_Department d ON d.DepartmentKey = k.DepartmentKey
                        WHERE d.RowID = ?
                        ORDER BY k.DisplayOrder""", TermID, DistrictID, DistrictName, DepartmentID) 
    rows = cursor.fetchall() 
    return rows

def get_campus_KPI_list_for_entry(TermID, DepartmentID, CampusID, CampusName):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT NULL RowID, k.CorpID, ? Term_RowID, K.RowID AS KPI_RowID, k.KPI AS KPI_Name, c.RowID Category_RowID, c.CategoryShort AS Category_Name,
                            d.RowID Department_RowID, d.Department Department_Name, ? Campus_RowID, ? Campus_Name, 
                            w.Is_KPI_Applicable, w.Weight * w.Is_KPI_Applicable as Adjusted_Weight, 0 Adjusted_Score, 0 Score, NULL Raw_Score, 
                            NULL Raw_Score_Details, NULL Artifact_URL
                        FROM dbo.Dim_KPI k
                        JOIN dbo.Dim_Category c ON c.CategoryKey = k.CategoryKey
                        JOIN dbo.Dim_KPI_Weight w ON w.KPI_RowID = k.RowID AND w.calculation_type = 'M' and w.kpi_level = 'C'
                        JOIN dbo.Dim_Department d ON d.DepartmentKey = k.DepartmentKey
                        WHERE d.RowID = ?
                        ORDER BY k.DisplayOrder""", TermID, CampusID, CampusName, DepartmentID) 
    rows = cursor.fetchall() 
    return rows


def get_pr_monitor_sum_by_department(CorpID, TermID, KPIType, CalcType):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT d.RowID, d.DepartmentKey, d.DepartmentShort, 
                            (SELECT COUNT(*) * (SELECT COUNT(*) FROM dbo.Dim_Department WHERE isActive = 1) 
                                FROM dbo.Dim_KPI k 
                                JOIN dbo.Dim_KPI_Weight w ON w.KPI_RowID = k.RowID AND w.Is_KPI_Applicable = 1 AND w.Term_RowID = ? AND w.KPI_Level = ? AND w.Calculation_Type = ?
                                WHERE k.DepartmentKey = d.DepartmentKey) AS Target_Count,
                            (SELECT COUNT(k.RowID)
                                FROM dbo.Fact_KPI k 
                                JOIN dbo.Dim_KPI_Weight w ON w.KPI_RowID = k.KPI_RowID AND w.Is_KPI_Applicable = 1 AND w.Term_RowID = ? AND w.KPI_Level = ? AND w.Calculation_Type = ?
                                WHERE k.Department_RowID = d.RowID
                                AND k.Term_RowID = ?) AS Real_Count
                        FROM dbo.Dim_Department d
                        WHERE d.CorpID = ?
                            AND d.IsActive = 1
                        ORDER BY d.DepartmentKey""", TermID, KPIType, CalcType, TermID, KPIType, CalcType, TermID, CorpID) 
    rows = cursor.fetchall() 
    return rows
     
def get_pr_monitor_sum_by_campus(CorpID, TermID, KPIType, CalcType):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT d.RowID, d.DepartmentKey, d.DepartmentShort, 
                            (SELECT COUNT(*) * (SELECT COUNT(*) FROM dbo.Dim_Campus WHERE isActive = 1) 
                                FROM dbo.Dim_KPI k 
                                JOIN dbo.Dim_KPI_Weight w ON w.KPI_RowID = k.RowID AND w.Is_KPI_Applicable = 1 AND w.Term_RowID = ? AND w.KPI_Level = ? AND w.Calculation_Type = ?
                                WHERE k.DepartmentKey = d.DepartmentKey) AS Target_Count,
                            (SELECT COUNT(k.RowID)
                                FROM dbo.Fact_KPI_Campus k 
                                JOIN dbo.Dim_KPI_Weight w ON w.KPI_RowID = k.KPI_RowID AND w.Is_KPI_Applicable = 1 AND w.Term_RowID = ? AND w.KPI_Level = ? AND w.Calculation_Type = ?
                                WHERE k.Department_RowID = d.RowID
                                AND k.Term_RowID = ?) AS Real_Count
                        FROM dbo.Dim_Department d
                        WHERE d.CorpID = ?
                            AND d.IsActive = 1
                        ORDER BY d.DepartmentKey""", TermID, KPIType, CalcType, TermID, KPIType, CalcType, TermID, CorpID) 
    rows = cursor.fetchall() 
    return rows

def get_real_calculated_district_kpi_count(CorpID, TermID, CalcType):
    cursor = cnxn.cursor()
    row = cursor.execute("""SELECT COUNT(k.RowID)
                              FROM dbo.Fact_KPI k 
                              JOIN dbo.Dim_KPI_Weight w ON w.KPI_RowID = k.KPI_RowID 
                                   AND w.Is_KPI_Applicable = 1 AND w.Term_RowID = ? AND w.KPI_Level = 'D' AND w.Calculation_Type = ?
                             WHERE k.CorpID = ? 
                               AND k.Term_RowID = ?""", TermID, CalcType, CorpID, TermID).fetchone()
    return row[0]
    
def get_real_calculated_campus_kpi_count(CorpID, TermID, CalcType):
    cursor = cnxn.cursor()
    row = cursor.execute("""SELECT COUNT(k.RowID)
                              FROM dbo.Fact_KPI_Campus k 
                              JOIN dbo.Dim_KPI_Weight w ON w.KPI_RowID = k.KPI_RowID 
                                   AND w.Is_KPI_Applicable = 1 AND w.Term_RowID = ? AND w.KPI_Level = 'C' AND w.Calculation_Type = ?
                             WHERE k.CorpID = ? 
                               AND k.Term_RowID = ?""", TermID, CalcType, CorpID, TermID).fetchone()
    return row[0]


def get_target_district_kpi_count(CorpID, TermID, CalcType):
    cursor = cnxn.cursor()
    row = cursor.execute("""SELECT COUNT(*) * (SELECT COUNT(*) FROM dbo.Dim_Department WHERE isActive = 1) 
                              FROM dbo.Dim_KPI k 
                              JOIN dbo.Dim_KPI_Weight w ON w.KPI_RowID = k.RowID 
                                   AND w.Is_KPI_Applicable = 1 AND w.Term_RowID = ? AND w.KPI_Level = 'D' AND w.Calculation_Type = ?
                             WHERE k.CorpID = ?""", TermID, CalcType, CorpID).fetchone()
    return row[0]

def get_target_campus_kpi_count(CorpID, TermID, CalcType):
    cursor = cnxn.cursor()
    row = cursor.execute("""SELECT COUNT(*) * (SELECT COUNT(*) FROM dbo.Dim_Campus WHERE isActive = 1) 
                              FROM dbo.Dim_KPI k 
                              JOIN dbo.Dim_KPI_Weight w ON w.KPI_RowID = k.RowID 
                                   AND w.Is_KPI_Applicable = 1 AND w.Term_RowID = ? AND w.KPI_Level = 'C' AND w.Calculation_Type = ?
                             WHERE k.CorpID = ?""", TermID, CalcType, CorpID).fetchone()
    return row[0]

def get_KPI_artifact_file(CorpID, TermID, KPIRowID):
    cursor = cnxn.cursor()
    row = cursor.execute("""SELECT Artifact_File 
                              FROM dbo.Fact_KPI_Artifact_File
                             WHERE CorpId = ?
                               AND Term_RowID = ?
                               AND KPI_RowID = ?""", CorpID, TermID, KPIRowID).fetchone()
    return row

def get_district_kpi_list_by_department(CorpID, TermRowID, DepartmentKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT k.RowID, k.KPIKey, Department, CategoryKey, Category, Version, KPI, Description, DisplayOrder, w.Weight, IsActive 
                    FROM dbo.Dim_KPI k 
                    LEFT JOIN dbo.Dim_KPI_Weight w ON k.RowID = w.KPI_RowID AND w.KPI_Level = 'D' AND w.Calculation_Type = 'M'
                    WHERE w.Term_RowID = ?
                      AND k.DepartmentKey = ?
                    ORDER BY Department, Category, DisplayOrder""", TermRowID, DepartmentKey) 
    rows = cursor.fetchall() 
    return rows

def get_campus_kpi_list_by_department(CorpID, TermRowID, DepartmentKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT k.RowID, k.KPIKey, Department, CategoryKey, Category, Version, KPI, Description, DisplayOrder, w.Weight, IsActive 
                    FROM dbo.Dim_KPI k 
                    LEFT JOIN dbo.Dim_KPI_Weight w ON k.RowID = w.KPI_RowID AND w.KPI_Level = 'C' AND w.Calculation_Type = 'M'
                    WHERE w.Term_RowID = ?
                      AND k.DepartmentKey = ?
                    ORDER BY Department, Category, DisplayOrder""", TermRowID, DepartmentKey) 
    rows = cursor.fetchall() 
    return rows    
# --------------------- END PROCESS -----------------------------------------------------------------------------


# --------------------- INBOX  ----------------------------------------------------------------------------------

def get_user_inbox(UserId):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT i.*, u.full_name sender_name
                        FROM dbo.private_inbox i
                        JOIN dbo.Dim_Users u ON u.user_id = i.sender_user_id
                        WHERE recipient_user_id = ? """, UserId) 
    rows = cursor.fetchall() 
    return rows

def get_user_sent_box(UserId):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT i.*, u.full_name recipient_name
                        FROM dbo.private_inbox i
                        JOIN dbo.Dim_Users u ON u.user_id = i.recipient_user_id
                        WHERE sender_user_id = ? """, UserId) 
    rows = cursor.fetchall() 
    return rows


def get_user_task_inbox(UserId):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT tu.row_id, tu.corp_id, tu.user_id, u.full_name, d.Department, tu.task_id, t.name task_name, tu.description, task_url, 
                                FORMAT(tu.assign_date_time, 'D', 'en-US') AS assign_date_time, FORMAT(tu.archive_date_time, 'D', 'en-US') AS archive_date_time
                        FROM dbo.Dim_Assigned_Tasks tu
                        JOIN dbo.Dim_task t ON tu.task_id = t.task_id
                        JOIN dbo.Dim_Users u ON tu.user_id = u.user_id
                        LEFT JOIN dbo.Dim_Department d ON u.department_id = d.RowID
                       WHERE tu.archive_date_time IS NULL
                         AND tu.user_id = ?""", UserId)
    rows = cursor.fetchall() 
    return rows

def get_all_user_all_task():
    cursor = cnxn.cursor()
    cursor.execute("""SELECT tu.row_id, tu.corp_id, tu.user_id, u.full_name, d.Department, tu.task_id, t.name task_name, tu.description, task_url, 
                                FORMAT(tu.assign_date_time, 'D', 'en-US') AS assign_date_time, FORMAT(tu.archive_date_time, 'D', 'en-US') AS archive_date_time
                        FROM dbo.Dim_Assigned_Tasks tu
                        JOIN dbo.Dim_task t ON tu.task_id = t.task_id
                        JOIN dbo.Dim_Users u ON tu.user_id = u.user_id
                        LEFT JOIN dbo.Dim_Department d ON u.department_id = d.RowID
                       WHERE tu.archive_date_time IS NULL """)
    rows = cursor.fetchall() 
    return rows

def get_user_task_archive(UserId):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT tu.row_id, tu.corp_id, tu.user_id, u.full_name, d.Department, tu.task_id, t.name task_name, tu.description, task_url, 
                                FORMAT(tu.assign_date_time, 'D', 'en-US') AS assign_date_time, FORMAT(tu.archive_date_time, 'D', 'en-US') AS archive_date_time
                        FROM dbo.Dim_Assigned_Tasks tu
                        JOIN dbo.Dim_task t ON tu.task_id = t.task_id
                        JOIN dbo.Dim_Users u ON tu.user_id = u.user_id
                        LEFT JOIN dbo.Dim_Department d ON u.department_id = d.RowID
                       WHERE tu.archive_date_time IS NOT NULL """)
    rows = cursor.fetchall() 
    return rows
    

# --------------------- END INBOX  -------------------------------------------------------------------------------


# --------------------- USER MANAGEMENT  -------------------------------------------------------------------------------
def get_um_modules():
    cursor = cnxn.cursor()
    cursor.execute("SELECT * from dbo.Dim_Modules ORDER BY MODUL_ID, PARENT_ID") 
    rows = cursor.fetchall() 
    return rows

def get_um_roles():
    cursor = cnxn.cursor()
    cursor.execute("SELECT * from dbo.Dim_roles ORDER BY role_name") 
    rows = cursor.fetchall() 
    return rows

def get_um_users():
    cursor = cnxn.cursor()
    cursor.execute("""SELECT u.*, d.DistrictShort district_name, c.CampusShort campus_name, dp.DepartmentShort department_name,
                             CASE kpi_process WHEN 'Y' THEN 'YES' ELSE 'NO' END process_user
                        FROM dbo.Dim_Users u
                        LEFT JOIN dbo.Dim_District d ON d.RowID = u.district_id
                        LEFT JOIN dbo.Dim_Campus c ON c.RowID = u.campus_id
                        LEFT JOIN dbo.Dim_Department dp ON dp.RowID = u.department_id
                       ORDER BY corp_id, district_name, campus_name, department_name, user_name""")
    rows = cursor.fetchall() 
    return rows
# --------------------- END USER MANAGEMENT  -------------------------------------------------------------------------------


# --------------------- REPORTS --------------------------------------------------------------------------------------------
def get_terms():
    cursor = cnxn.cursor()
    cursor.execute("SELECT RowID, TermKey, Term FROM dbo.Dim_Term ORDER BY OrderNo DESC") 
    rows = cursor.fetchall() 
    return rows

def get_rep_hps_top_score(TermKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT ISNULL(ROUND(SUM(Department_Score)/COUNT(*), 1), 0) HPS_SCORE
                        FROM dbo.Kc_HPS_Department_Scores
                       WHERE TermKey = ?""", TermKey) 
    rows = cursor.fetchone() 
    return rows[0]

def get_hps_all_term_scores(PastYears):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT t.TermKey, t.Term, ISNULL(ROUND(SUM(Department_Score)/COUNT(*), 1), 0) Score
                        FROM dbo.Kc_HPS_Department_Scores s
                        JOIN dbo.Dim_Term t ON t.TermKey = s.TermKey
                       WHERE t.SchoolYear >= YEAR(GETDATE()) - ?
                       GROUP BY t.TermKey, t.Term
                       ORDER BY t.TermKey ASC""", PastYears) 
    rows = cursor.fetchall() 
    return rows

def get_district_all_term_scores(PastYears):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT REPLACE(s.District, '&','-') AS District, t.Term, ISNULL(ROUND(SUM(Department_Score)/COUNT(*), 1), 0) Score
                        FROM dbo.Kc_District_Department_Scores s
                        JOIN dbo.Dim_Term t ON t.TermKey = s.TermKey
                        WHERE t.SchoolYear >= YEAR(GETDATE()) - ?
                        GROUP BY s.District, t.Term
                        ORDER BY s.District ASC""", PastYears) 
    rows = cursor.fetchall() 
    return rows

def get_selected_dist_dept_past_scores(DistKey, PastYears):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT s.DepartmentKey, s.Department, t.Term, t.TermKey, ISNULL(ROUND(SUM(Department_Score)/COUNT(*), 1), 0) Score
                        FROM dbo.Kc_District_Department_Scores s
                        JOIN dbo.Dim_Term t ON t.TermKey = s.TermKey
                        WHERE t.SchoolYear >= YEAR(GETDATE()) - ?
                        AND s.DistrictKey = ?
                        GROUP BY s.DepartmentKey, s.Department, t.Term, t.TermKey
                        ORDER BY s.Department, t.TermKey ASC""", PastYears, DistKey) 
    rows = cursor.fetchall() 
    return rows

def get_selected_district_past_scores(DistKey, PastYears):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT REPLACE(s.District, '&','-') AS District, s.TermKey, t.Term, ISNULL(ROUND(SUM(Department_Score)/COUNT(*), 1), 0) Score
                        FROM dbo.Kc_District_Department_Scores s
                        JOIN dbo.Dim_Term t ON t.TermKey = s.TermKey
                       WHERE t.SchoolYear >= YEAR(GETDATE()) - ?
                         AND s.DistrictKey = ?
                       GROUP BY s.District, s.TermKey, t.Term
                       ORDER BY s.TermKey ASC""", PastYears, DistKey) 
    rows = cursor.fetchall() 
    return rows

def get_selected_district_campus_past_scores(DistKey, PastYears):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT c.CampusKey, t.Term, t.TermKey, REPLACE(c.CampusShort, '&','-') AS CampusShort, ROUND(SUM(adjusted_score) / SUM(Adjusted_Weight), 1) Score,
                                ROW_NUMBER() OVER (ORDER BY CampusKey) OrderNo
                        FROM dbo.Fact_KPI_Campus s
                        JOIN dbo.Dim_District d ON d.RowID = s.District_RowID
                        JOIN dbo.Dim_Campus c ON c.RowID = s.Campus_RowID
                        JOIN dbo.Dim_Term t ON t.RowID = s.Term_RowID
                       WHERE t.SchoolYear >= YEAR(GETDATE()) - ?
                         AND d.DistrictKey = ?
                         AND Is_KPI_Applicable = 1
                       GROUP BY c.CampusKey, c.CampusShort, t.Term, t.TermKey
                       ORDER BY c.CampusKey, t.Term ASC""", PastYears, DistKey) 
    rows = cursor.fetchall() 
    return rows


def get_all_districts_term_scores(TermKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT REPLACE(s.District, '&','-') AS District, ISNULL(ROUND(SUM(Department_Score)/COUNT(*), 1), 0) Score
                        FROM dbo.Kc_District_Department_Scores s
                       WHERE s.TermKey = ?
                       GROUP BY s.District, s.District_OrderNo
                       ORDER BY s.District_OrderNo ASC""", TermKey) 
    rows = cursor.fetchall() 
    return rows

def get_all_departments_term_scores(TermKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT REPLACE(s.Department, '&','-') AS Department, ISNULL(ROUND(SUM(Department_Score)/COUNT(*), 1), 0) Score
                        FROM dbo.Kc_District_Department_Scores s
                        JOIN dbo.Dim_Term t ON t.TermKey = s.TermKey
                        WHERE s.TermKey = ?
                        GROUP BY s.Department, s.Department_OrderNo
                        ORDER BY s.Department_OrderNo ASC""", TermKey) 
    rows = cursor.fetchall() 
    return rows

def get_all_campuses_term_scores(TermKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT c.CampusKey, REPLACE(c.CampusShort, '&','-') AS CampusShort, ROUND(SUM(adjusted_score) / SUM(Adjusted_Weight), 1) Score,
                            ROW_NUMBER() OVER (ORDER BY CampusKey) OrderNo
                        FROM dbo.Fact_KPI_Campus s
                        JOIN dbo.Dim_Campus c ON c.RowID = s.Campus_RowID
                        JOIN dbo.Dim_Term t ON t.RowID = s.Term_RowID
                       WHERE t.TermKey = ?
                         AND Is_KPI_Applicable = 1
                       GROUP BY c.CampusKey, s.Campus_RowID, c.CampusShort
                       ORDER BY OrderNo DESC""", TermKey) 
    rows = cursor.fetchall() 
    return rows

def get_rep_district_top_score(TermKey, DistKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT ISNULL(ROUND(SUM(Department_Score)/COUNT(*), 1), 0) Score
                        FROM dbo.Kc_District_Department_Scores s
                       WHERE TermKey = ?
                         AND DistrictKey = ?""", TermKey, DistKey) 
    rows = cursor.fetchone() 
    return rows[0]


def get_rep_hps_dept_scores(TermKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT TermKey, Term, DepartmentKey, REPLACE(Department, '&','-') AS Department, Department_OrderNo, ISNULL(ROUND(Department_Score, 1), 0) Score
                        FROM dbo.Kc_HPS_Department_Scores
                       WHERE TermKey = ?
                       ORDER BY Department_OrderNo""", TermKey) 
    rows = cursor.fetchall() 
    return rows

def get_rep_hps_dept_cat_scores(TermKey, DeptKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT TermKey, Term, DepartmentKey, CategoryKey, Category, Category_OrderNo, ISNULL(ROUND(Category_Score, 1), 0) Score
                        FROM dbo.Kc_HPS_Category_Scores
                       WHERE TermKey = ?
                         AND DepartmentKey = ?
                       ORDER BY Category_OrderNo""", TermKey, DeptKey) 
    rows = cursor.fetchall() 
    return rows


def get_rep_dist_dept_scores(TermKey, DistKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT TermKey, Term, DepartmentKey, Department, Department_OrderNo, ISNULL(ROUND(Department_Score, 1), 0) Score
                        FROM dbo.Kc_District_Department_Scores
                       WHERE TermKey = ?
                         AND DistrictKey = ?
                       ORDER BY Department_OrderNo""", TermKey, DistKey) 
    rows = cursor.fetchall() 
    return rows

def get_rep_dist_dept_cat_scores(TermKey, DistKey, DeptKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT TermKey, Term, DepartmentKey, CategoryKey, Category, Category_OrderNo, ISNULL(ROUND(Category_Score, 1), 0) Score
                        FROM dbo.Kc_District_Category_Scores
                       WHERE TermKey = ?
                         AND DistrictKey = ?
                         AND DepartmentKey = ?
                       ORDER BY Category_OrderNo""", TermKey, DistKey, DeptKey) 
    rows = cursor.fetchall() 
    return rows


def get_rep_dist_kpi_scores(TermKey, DistKey, DeptKey, CatKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT k.RowID, k.KPIKey, k.KPI KPI_Name, k.Description, ROUND(Score, 1) Score, ROW_NUMBER() OVER (ORDER BY k.RowID) KPI_OrderNo, Artifact_URL
                        FROM dbo.Fact_KPI s
                        JOIN dbo.Dim_Term t ON t.RowID = s.Term_RowID
                        JOIN dbo.Dim_District dc ON dc.RowID = s.District_RowID
                        JOIN dbo.Dim_Department d ON d.RowID = s.Department_RowID
                        JOIN dbo.Dim_KPI k ON k.RowID = s.KPI_RowID
                        JOIN dbo.Dim_Category c ON c.RowID = s.Category_RowID
                       WHERE t.TermKey =  ?
                         AND dc.DistrictKey = ?
                         AND (d.DepartmentKey = ? OR ? = 0)
                         AND (c.CategoryKey = ? OR ? = 0)   
                         AND Is_KPI_Applicable = 1
                       -- GROUP BY k.RowID, k.KPIKey, k.KPI
                       ORDER BY KPI_OrderNo ASC""", TermKey, DistKey, DeptKey, DeptKey, CatKey, CatKey) 
    rows = cursor.fetchall() 
    return rows


def get_rep_campus_kpi_scores(TermKey, CampusKey, CatKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT k.RowID, k.KPIKey, k.KPI KPI_Name, k.Description, ROUND(Score, 1) Score, ROW_NUMBER() OVER (ORDER BY k.RowID) KPI_OrderNo, Artifact_URL
                        FROM dbo.Fact_KPI_Campus s
                        JOIN dbo.Dim_Term t ON t.RowID = s.Term_RowID
                        JOIN dbo.Dim_Campus cmp ON cmp.RowID = s.Campus_RowID
                        JOIN dbo.Dim_KPI k ON k.RowID = s.KPI_RowID
                        JOIN dbo.Dim_Category c ON c.RowID = s.Category_RowID
                       WHERE t.TermKey =  ?
                         AND (cmp.CampusKey = ? OR ? = 0)
                         AND (c.CategoryKey = ? OR ? = 0)   
                         AND Is_KPI_Applicable = 1
                       -- GROUP BY k.RowID, k.KPIKey, k.KPI
                       ORDER BY KPI_OrderNo ASC""", TermKey, CampusKey, CampusKey, CatKey, CatKey) 
    rows = cursor.fetchall() 
    return rows


def get_rep_dist_campus_kpi_score_list(TermKey, DistKey, CmpKey, DeptKey, CatKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT d.DistrictShort, cmp.CampusShort, dp.DepartmentShort, c.CategoryShort,k.KPI KPI_Name, w.Weight, ROUND(s.Score, 1) Score, k.Description, s.Raw_Score, s.Raw_Score_Details, s.Artifact_URL
                        FROM dbo.Fact_KPI_Campus s
                        JOIN dbo.Dim_Term t ON t.RowID = s.Term_RowID
                        JOIN dbo.Dim_KPI k ON k.RowID = s.KPI_RowID
                        LEFT JOIN dbo.Dim_KPI_Weight w ON w.KPI_RowID = s.KPI_RowID AND w.Term_RowID = s.Term_RowID
                        JOIN dbo.Dim_District d ON d.RowID = s.District_RowID
                        JOIN dbo.Dim_Campus cmp ON cmp.RowID = s.Campus_RowID
                        JOIN dbo.Dim_Category c ON c.RowID = s.Category_RowID
                        JOIN dbo.Dim_Department dp ON dp.RowID = s.Department_RowID
                        WHERE t.TermKey = ?
                        AND (d.DistrictKey = ? OR ? = 0)
                        AND (cmp.CampusKey = ? OR ? = 0)
                        AND (dp.DepartmentKey = ? OR ? = 0)
                        AND (c.CategoryKey = ? OR ? = 0)
                        ORDER BY d.OrderNo, CampusShort, c.OrderNo, k.DisplayOrder""", TermKey, DistKey, DistKey, CmpKey, CmpKey, DeptKey, DeptKey, CatKey, CatKey) 
    rows = cursor.fetchall() 
    return rows

def get_rep_dist_campus_scores(TermKey, DistKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT t.TermKey, c.CampusKey, s.Campus_RowID, c.CampusShort, ROUND(SUM(adjusted_score) / SUM(Adjusted_Weight), 1) Score,
                            ROW_NUMBER() OVER (ORDER BY CampusKey) OrderNo
                        FROM dbo.Fact_KPI_Campus s
                        JOIN dbo.Dim_Campus c ON c.RowID = s.Campus_RowID
                        JOIN dbo.Dim_Term t ON t.RowID = s.Term_RowID
                        JOIN dbo.Dim_District d ON d.RowID = s.District_RowID
                        WHERE t.TermKey =  ?
                          AND d.DistrictKey  = ?
                          AND Is_KPI_Applicable = 1
                        GROUP BY t.TermKey, c.CampusKey, s.Campus_RowID, c.CampusShort
                        ORDER BY OrderNo DESC""", TermKey, DistKey) 
    rows = cursor.fetchall() 
    return rows

def get_rep_dist_campus_category_scores(TermKey, CampusKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT t.TermKey, cmp.CampusKey, cmp.RowID CampusRowID, cmp.CampusShort, c.CategoryKey, c.RowID CategoryRowID, c.Category, 
                             ROUND(SUM(adjusted_score) / SUM(Adjusted_Weight), 1) Score,
                                ROW_NUMBER() OVER (ORDER BY c.RowID) Category_OrderNo
                        FROM dbo.Fact_KPI_Campus s
                        JOIN dbo.Dim_Term t ON t.RowID = s.Term_RowID
                        JOIN dbo.Dim_Category c ON c.RowID = s.Category_RowID
                        JOIN dbo.Dim_Campus cmp ON cmp.RowID = s.Campus_RowID
                        WHERE t.TermKey =  ?
                          AND cmp.CampusKey = ?
                          AND Is_KPI_Applicable = 1
                        GROUP BY t.TermKey, cmp.CampusKey, cmp.RowID, cmp.CampusShort, c.CategoryKey, c.RowID, c.Category
                        ORDER BY Category_OrderNo""", TermKey, CampusKey) 
    rows = cursor.fetchall() 
    return rows



def get_rep_hps_kpi_scores(TermKey, DeptKey, CatKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT k.RowID, k.KPIKey, '(' + dc.DistrictShort + ') ' + k.KPI KPI_Name, k.Description, 
                             ROUND(Score, 1) AS Score, ROW_NUMBER() OVER (ORDER BY k.RowID) KPI_OrderNo, Artifact_URL
                        FROM dbo.Fact_KPI s
                        JOIN dbo.Dim_Term t ON t.RowID = s.Term_RowID
                        JOIN dbo.Dim_District dc ON dc.RowID = s.District_RowID
                        JOIN dbo.Dim_Department d ON d.RowID = s.Department_RowID
                        JOIN dbo.Dim_KPI k ON k.RowID = s.KPI_RowID
                        JOIN dbo.Dim_Category c ON c.RowID = s.Category_RowID
                       WHERE t.TermKey = ?
                         AND (d.DepartmentKey = ? OR ? = 0)
                         AND (c.CategoryKey = ? OR ? = 0)
                         AND Is_KPI_Applicable = 1
                       --GROUP BY s.Category_RowID, k.RowID, k.KPIKey, k.KPI
                       ORDER BY dc.DistrictShort, KPI_OrderNo ASC;""", TermKey, DeptKey, DeptKey, CatKey, CatKey) 
    rows = cursor.fetchall() 
    return rows

def get_rep_low_district_scores(TermKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT DistrictKey, District, ISNULL(ROUND(SUM(Department_Score)/COUNT(*), 1), 0) Score
                        FROM dbo.Kc_District_Department_Scores s
                       WHERE TermKey = ?
                       GROUP BY DistrictKey, District
                      HAVING ISNULL(ROUND(SUM(Department_Score)/COUNT(*), 1), 0) < 2.5;""", TermKey) 
    rows = cursor.fetchall() 
    return rows

def get_rep_low_hps_department_scores(TermKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT REPLACE(Department, '&','-') AS Department, ISNULL(ROUND(Department_Score, 1), 0) Score
                        FROM dbo.Kc_HPS_Department_Scores
                       WHERE TermKey = ?
                         AND ISNULL(ROUND(Department_Score, 1), 0) < 2.5;""", TermKey) 
    rows = cursor.fetchall() 
    return rows

def get_rep_low_dist_department_scores(TermKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT District, REPLACE(Department, '&','-') AS Department, ISNULL(ROUND(Department_Score, 1), 0) Score
                        FROM dbo.Kc_District_Department_Scores
                       WHERE TermKey = ?
                         AND ISNULL(ROUND(Department_Score, 1), 0) < 2.5
                       ORDER BY District, Department;""", TermKey)                        
    rows = cursor.fetchall() 
    return rows

def get_rep_low_hps_dept_category_scores(TermKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT REPLACE(Department, '&','-') AS Department, Category, ISNULL(ROUND(Category_Score, 1), 0) Score
                        FROM dbo.Kc_HPS_Category_Scores
                       WHERE TermKey = ?
                         AND ISNULL(ROUND(Category_Score, 1), 0) < 2.5
                       ORDER BY Department, Category;""", TermKey)                        
    rows = cursor.fetchall() 
    return rows

# --------------------- END REPORTS   --------------------------------------------------------------------------------------


# --------------------- MANUEL ENTRY   --------------------------------------------------------------------------------------
def get_kpi_list_by_department2(TermRowID, DepartmentKey):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT DISTINCT kpi.RowID KPIRowID, kpi.KPIKey, kpi.DepartmentKey , kpi.Department, d.RowID DepartmentRowId,
                            kpi.CategoryKey, kpi.Category, c.RowID CategoryRowId, KPI KPI_Name, DisplayOrder, w.Weight,  
                            w.Weight * w.Is_KPI_Applicable as Adjusted_Weight, 0 Score
                        FROM dbo.Dim_KPI kpi 
                        JOIN dbo.Dim_KPI_Weight w ON kpi.RowID = w.KPI_RowID AND w.Is_KPI_Applicable = 1 
                             AND w.calculation_type = 'M' and w.kpi_level = 'D' AND w.Term_RowID = ?
                        JOIN dbo.Dim_Category c ON kpi.CategoryKey = c.CategoryKey
                        JOIN dbo.Dim_Department d ON kpi.DepartmentKey = d.DepartmentKey
                        WHERE kpi.DepartmentKey = ?
                        ORDER BY DisplayOrder ASC""", TermRowID, DepartmentKey) 
    rows = cursor.fetchall() 
    return rows

def get_districts_for_entry():
    cursor = cnxn.cursor()
    cursor.execute("SELECT *, 0 Score, NULL ArtifactUrl FROM dbo.Dim_District WHERE isActive = 1 ORDER BY OrderNo") 
    rows = cursor.fetchall() 
    return rows    

def get_districts_for_entry_with_ex_score(TermRowID, DepartmentKey, KPIRowID):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT *, 0 Score, NULL ArtifactUrl,
                            ISNULL((SELECT Score 
                                FROM dbo.Fact_KPI f 
                                JOIN dbo.Dim_Department d ON d.RowID = f.Department_RowID
                                WHERE Term_RowID = ? AND KPI_RowID = ? AND DepartmentKey = ? AND f.District_RowID = dist.RowID), -1) AS CurrentScore,
                            ISNULL((SELECT Artifact_URL 
                                        FROM dbo.Fact_KPI f 
                                        JOIN dbo.Dim_Department d ON d.RowID = f.Department_RowID
                                        WHERE Term_RowID = ? AND KPI_RowID = ? AND DepartmentKey = ? AND f.District_RowID = dist.RowID), '') AS CurrentArtifactURL                                
                        FROM dbo.Dim_District dist
                        WHERE isActive = 1
                        ORDER BY OrderNo""", TermRowID, KPIRowID, DepartmentKey, TermRowID, KPIRowID, DepartmentKey) 
    rows = cursor.fetchall() 
    return rows    

def get_campuses_for_entry(DistrictRowID):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT *, 0 Score, NULL ArtifactUrl, TRIM(REPLACE(REPLACE(Campus, '-', ' '), DistrictName, '')) CampusCleanName
                        FROM dbo.Dim_Campus c 
                       WHERE isActive = 1 AND District_RowID = ? 
                       ORDER BY CampusShort""", DistrictRowID) 
    rows = cursor.fetchall() 
    return rows


def get_campuses_for_entry_with_ex_score(TermRowID, DepartmentKey, DistrictRowID, KPIRowID):
    cursor = cnxn.cursor()
    cursor.execute("""SELECT *, 0 Score, NULL ArtifactUrl,
                             ISNULL((SELECT Score 
                                FROM dbo.Fact_KPI_Campus f 
                                JOIN dbo.Dim_Department d ON d.RowID = f.Department_RowID
                                WHERE Term_RowID = ? AND KPI_RowID = ? AND DepartmentKey = ? AND f.Campus_RowID = cmp.RowID), -1) AS CurrentScore,
                             ISNULL((SELECT Artifact_URL 
                                        FROM dbo.Fact_KPI_Campus f 
                                        JOIN dbo.Dim_Department d ON d.RowID = f.Department_RowID
                                        WHERE Term_RowID = ? AND KPI_RowID = ? AND DepartmentKey = ? AND f.Campus_RowID = cmp.RowID), '') AS CurrentArtifactURL
                        FROM dbo.Dim_Campus cmp
                       WHERE isActive = 1
                         AND cmp.District_RowID = ?
                       ORDER BY CampusShort""", TermRowID, KPIRowID, DepartmentKey, TermRowID, KPIRowID, DepartmentKey, DistrictRowID) 
    rows = cursor.fetchall() 
    return rows

# --------------------- MANUEL ENTRY   --------------------------------------------------------------------------------------


def insert_test(numara):
    cursor = cnxn.cursor()
    cursor.execute("""INSERT INTO dbo.test  VALUES (?)""", numara )
    cnxn.commit()