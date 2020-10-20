import os
import datetime
import sqlAlchamyPanda
from flask import Flask, render_template, url_for, request, flash, redirect, session, flash, jsonify
from flask_bootstrap import Bootstrap
from excel_docs import prepare_excel_docs_for_districts, prepare_excel_docs_for_campuses
from datetime import datetime
from pyOdbcDBLayer import get_general_params, get_districts, get_categories, update_category, update_district, get_corporation, get_department, update_department
from pyOdbcDBLayer import get_campus, update_campus, get_kpi_list, update_kpi_weight, get_user_inbox, get_user_sent_box
from pyOdbcDBLayer import get_user_task_inbox, get_user_task_archive, task_to_archive, task_delete, task_undo, task_assign, get_all_user_all_task
from pyOdbcDBLayer import get_um_roles, get_um_modules, get_um_users, delete_Fact_KPI, insert_Fact_KPI, get_new_row_id_fact_kpi, get_district_KPI_list_all, update_dist_kpi_score
from pyOdbcDBLayer import get_terms, get_rep_hps_dept_scores, get_rep_dist_dept_scores, get_rep_hps_dept_cat_scores, get_rep_hps_top_score, get_rep_dist_dept_cat_scores
from pyOdbcDBLayer import get_district_name, get_term_name, get_department_name, get_category_name, get_rep_dist_kpi_scores, get_rep_hps_kpi_scores, get_rep_dist_campus_kpi_score_list
from pyOdbcDBLayer import get_year_term_list, update_process_status, insert_new_district, insert_new_campus, insert_new_department, insert_new_kpi
from pyOdbcDBLayer import get_district_count, get_campus_count, get_rep_dist_campus_scores, get_rep_dist_campus_category_scores, get_rep_campus_kpi_scores
from pyOdbcDBLayer import classTest, classDistrict, classCampus, classDepartment, classKPI, classPublic
from pyOdbcDBLayer import get_campus_name, get_campus_by_district, get_categories_by_department, get_current_term, get_user_info, get_kpi_list_by_department
from pyOdbcDBLayer import get_hps_all_term_scores, get_rep_district_top_score, get_district_all_term_scores, get_all_districts_term_scores, get_user_by_name_email
from pyOdbcDBLayer import get_all_departments_term_scores, get_all_campuses_term_scores, get_selected_district_past_scores, get_selected_dist_dept_past_scores
from pyOdbcDBLayer import get_selected_district_campus_past_scores, get_pr_monitor_sum_by_department, get_pr_monitor_sum_by_campus
from pyOdbcDBLayer import get_real_calculated_district_kpi_count, get_real_calculated_campus_kpi_count, get_target_district_kpi_count, get_target_campus_kpi_count, get_term_key
from pyOdbcDBLayer import get_rep_low_hps_dept_category_scores, get_rep_low_dist_department_scores, get_rep_low_hps_department_scores, get_rep_low_district_scores
from pyOdbcDBLayer import get_archive_file_path, get_download_file_path, get_KPI_artifact_file, get_kpi_by_categories, get_user_pswd, change_pwd, get_kpi_list_by_department2
from pyOdbcDBLayer import insert_test, get_districts_for_entry, get_district_kpi_list_by_department, get_campus_kpi_list_by_department, get_campuses_for_entry
from pyOdbcDBLayer import get_category_rowid, get_districts_for_entry_with_ex_score, get_campuses_for_entry_with_ex_score, insert_Fact_KPI_Campus, delete_Fact_KPI_Campus
from sqlAlchamyPanda import getRowsFromCsv, getRowsFromXls, delKPIOldRecords, delKPIOldRecords2, insertFactKPI, delKPICampusOldRecords, delKPICampusOldRecords2, get_all_tasks

import time
import pandas as pd
import subprocess
import sys
from random import random
import random



DOWNLOAD_DIRECTORY = get_download_file_path()
UPLOAD_DIRECTORY = get_download_file_path()
ARCHIVE_DIRECTORY = get_archive_file_path()



# this is very very important. all public variables assign at here
# def __init__(self, CorpID, TermKey, TermRowId, UserID, UserDistrictId, UserDistrictKey, UserDepartmentId, UserDepartmentKey, UserDRoleId):
v_Term = get_current_term()
v_user = get_user_info(1, 11)  # user_id AS UserID, user_name AS UserName, full_name AS UserFullName, d.RowID AS DepartmentRowID, d.DepartmentKey, dt.RowID AS DistrictRowID, dt.DistrictKey
publicVars = classPublic(1, v_Term[0], v_Term[2], v_user[0], v_user[1], v_user[2], v_user[5], v_user[6], v_user[3], v_user[4], None, None)

app = Flask(__name__)
# app.secret_key = os.urandom(24)
Bootstrap(app)

# -------------------------------------------------------------------------------------------------------------------------------
labels = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
values = [967.67, 1190.89, 1079.75, 1349.19, 2328.91, 2504.28, 2873.83, 4764.87, 4349.29, 6458.30, 9907, 16297]

colors = [
        "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
        "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
        "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

# -------------------------------------------------------------------------------------------------------------------------------

curCorp = 1
def set_current_corp():
    global curCorp 
    curCorp = 1
    return
  
set_current_corp() 

@app.route('/')

@app.errorhandler(Exception)
def server_error(err):
    app.logger.exception(err)
    return render_template("err_gen.html", errorDetail = err)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("err_404.html")

@app.route("/login")
def login():
    session.clear()
    session['logged_in'] = True
    return render_template("login.html")

@app.route("/ucp", methods = ["GET", "POST"])
def ucp():
    if request.method == 'POST':
        vOld = request.form['txtOld']
        vNew = request.form['txtNew']
        vNew2 = request.form['txtConfirm']
        vCurrP = get_user_pswd(session['UserID'])
        
        if vOld != vCurrP:
            return render_template("user_cp.html", messType = 'Error', mess = 'Your current password is wrong! Please type correct.')
        elif len(vNew) < 8:
            return render_template("user_cp.html", messType = 'Error', mess = 'Password must be at least 8 characters.')
        elif vNew != vNew2:
            return render_template("user_cp.html", messType = 'Error', mess = 'Your new password and confirmation password are not the same! Please type them the same.')

        change_pwd(session['UserID'], vNew)

        return render_template("user_cp.html", messType = 'Success',  mess = 'Your password changed successfully.')
    return render_template("user_cp.html")


@app.route("/home", methods = ["GET", "POST"])
def home():
    #try:
    if session['logged_in'] != True:
        redirect('/login')

    v_Term = get_current_term()

    if request.method == 'POST':
        vUserNm = request.form['UserName']
        vPswd = request.form['UserPwd']
    
        v_user = get_user_by_name_email(1, vUserNm)

        if v_user is None:
            return redirect("/login")

        # def __init__(self, CorpID, TermKey, TermRowId, UserID, UserName, UserFullName, UserDistrictId, UserDistrictKey, UserDepartmentId, UserDepartmentKey, UserDRoleId):
        publicVars = classPublic(1, v_Term[0], v_Term[2], v_user[0], v_user[1], v_user[2], v_user[6], v_user[7], v_user[4], v_user[5], None, v_user[3])
        
        session['CorpID'] = publicVars.CorpID
        session['TermKey'] = publicVars.TermKey
        session['TermID'] = publicVars.TermRowId
        session['UserID'] = publicVars.UserID
        session['UserName'] = publicVars.UserName
        session['UserFullName'] = publicVars.UserFullName
        session['UserDistrictKey'] = publicVars.UserDistrictKey
        session['UserDepartmentKey'] = publicVars.UserDepartmentKey
        session['UserDepartmentRowID'] = publicVars.UserDepartmentId
        session['UserDRoleId'] = publicVars.UserDRoleId

        if session['UserDepartmentKey'] is not None:
            session['UserDepartmentName'] = get_department_name(session['UserDepartmentKey'])
        else:
            session['UserDepartmentName'] = ''

        v_params = get_general_params(publicVars.CorpID)
        
        if publicVars.UserDepartmentKey == 50:
            v_inbox = get_all_user_all_task()
        else:
            v_inbox = get_user_task_inbox(publicVars.UserID)

        return render_template("home.html", myBox = v_inbox, gnrlParams = v_params, c = publicVars)
    else:
        if session['UserName'] is not None:
            v_user = get_user_by_name_email(1, session['UserName'])
            if v_user is None:
                return redirect("/login")
        else:
            return redirect("/login")

    # def __init__(self, CorpID, TermKey, TermRowId, UserID, UserName, UserFullName, UserDistrictId, UserDistrictKey, UserDepartmentId, UserDepartmentKey, UserDRoleId):
    publicVars = classPublic(1, v_Term[0], v_Term[2], v_user[0], v_user[1], v_user[2], v_user[6], v_user[7], v_user[4], v_user[5], None, v_user[3])

    if session['UserDepartmentKey'] == 50:
        v_inbox = get_all_user_all_task()
    else:
        v_inbox = get_user_task_inbox(session['UserID'])
    v_params = get_general_params(session['CorpID'])
    return render_template("home.html", myBox = v_inbox, gnrlParams = v_params, c = publicVars)        

    #except Exception as e:
	#    render_template('err_gen.html', errorDetail = str(e))


@app.route("/task_archive")
def task_archive():
    v_inbox = get_user_task_archive(1)
    return render_template("inbox_deleted.html", myBox = v_inbox)

@app.route("/home_archive_task/<int:rowid>", methods = ["GET", "POST"])
def home_archive_task(rowid):
    task_to_archive(rowid)
    # v_inbox = get_user_task_inbox(1)
    return redirect('/home')

@app.route("/home_delete_task/<int:rowid>", methods = ["GET", "POST"])
def home_delete_task(rowid):
    task_delete(rowid)
    v_inbox = get_user_task_archive(1)
    return render_template("inbox_deleted.html", myBox = v_inbox)

@app.route("/home_undo_task/<int:rowid>", methods = ["GET", "POST"])
def home_undo_task(rowid):
    task_undo(rowid)
    return redirect('/home')


@app.route('/corporation', methods = ["GET", "POST"])
def corporation():
    v_corp = get_corporation(1)
    return render_template("corporation.html", corpInfo = v_corp)


@app.route('/def_district')
def districts():
    cDist = classTest()
    cDist.corp_id = 1
    v_districts = get_districts()
    return render_template("def_district.html", dists = v_districts, openType = 0)

@app.route('/pr_district')
def pr_district():
    v_districts = get_districts()
    return render_template("def_district.html", dists = v_districts, openType = 1)


@app.route('/insert_district', methods = ['GET', 'POST'])
def insert_district():
    classDist = classDistrict()
    if request.method == 'POST':
        classDist.RowID = request.form['RowID']
        classDist.CorpID = request.form['CorpID']
        classDist.DistrictKey= request.form['DistrictKey']
        classDist.District = request.form['District']
        classDist.DistrictShort = request.form['DistrictShort']
        classDist.Weight = request.form['Weight']
        classDist.OrderNo = request.form['OrderNo']
        classDist.IsActive = request.form['IsActive']
        classDist.DmlUserID = 1

        insert_new_district(classDist)
    return redirect('/def_district')


@app.route('/district_upd', methods = ['GET', 'POST'])
def district_upd():
    if request.method == 'POST':
        RowId = request.form['RowID']
        NewWeight = request.form['Weight']
        update_district(RowId, NewWeight)
        # flash("Category Updated Successfully")
        return redirect('/pr_district')


@app.route('/def_category')
def categories():
    set_current_corp() 
    v_categories = get_categories()
    return render_template("def_category.html", cats = v_categories, openType = 0)

@app.route('/pr_category')
def pr_category():
    set_current_corp() 
    v_categories = get_categories_by_department(session['UserDepartmentKey'])
    return render_template("def_category.html", cats = v_categories, openType = 1)

@app.route('/category_upd', methods = ['GET', 'POST'])
def category_upd():
    if request.method == 'POST':
        RowId = request.form['RowID']
        NewWeight = round(float(request.form['Weight']), 1)
        update_category(RowId, NewWeight)
        return redirect('/pr_category')


@app.route('/def_department')
def department():
    set_current_corp() 
    v_department = get_department()
    return render_template("def_department.html", depts = v_department, openType = 0)

@app.route('/pr_department')
def pr_department():
    set_current_corp() 
    v_department = get_department()
    return render_template("def_department.html", depts = v_department, openType = 1)

@app.route('/department_insert', methods = ['GET', 'POST'])
def department_insert():
    classDept = classDepartment()
    if request.method == 'POST':
        classDept.RowID = request.form['RowID']
        classDept.CorpID = 1
        classDept.DepartmentKey= request.form['DepartmentKey']
        classDept.Department = request.form['Department']
        classDept.DepartmentShort = request.form['DepartmentShort']
        classDept.Description = request.form['Description']
        classDept.Weight = request.form['Weight']
        classDept.OrderNo = request.form['OrderNo']
        classDept.Version = request.form['Version']
        classDept.IsActive = 1
        classDept.DmlUserID = 1

        insert_new_department(classDept)
    return redirect('/def_department')

@app.route('/department_upd', methods = ['GET', 'POST'])
def department_upd():
    if request.method == 'POST':
        RowId = request.form['RowID']
        NewWeight = request.form['Weight']
        update_department(RowId, NewWeight)
        # flash("Category Updated Successfully")
        return redirect('/pr_department')


@app.route('/def_campus')
def campus():
    set_current_corp() 
    v_campus = get_campus()
    return render_template("def_campus.html", campuses = v_campus, openType = 0)

@app.route('/pr_campus')
def pr_campus():
    set_current_corp() 
    v_campus = get_campus()
    return render_template("def_campus.html", campuses = v_campus, openType = 1)

@app.route('/campus_upd', methods = ['GET', 'POST'])
def campus_upd():
    if request.method == 'POST':
        RowId = request.form['RowID']
        NewWeight = request.form['Weight']
        update_campus(RowId, NewWeight)
        # flash("Category Updated Successfully")
        return redirect('/pr_campus')

@app.route('/campus_insert', methods = ['GET', 'POST'])
def campus_insert():
    classCamp = classCampus()
    if request.method == 'POST':
        classCamp.RowID = request.form['RowID']
        classCamp.CorpID = 1
        classCamp.CampusKey= request.form['CampusKey']
        classCamp.District_RowID = request.form['District_RowID']
        classCamp.Integration_DistrictID = request.form['Integration_DistrictID']
        classCamp.Campus = request.form['Campus']
        classCamp.CampusShort = request.form['CampusShort']
        classCamp.Campus_Weight = request.form['Campus_Weight']
        classCamp.IsActive = 1
        classCamp.DmlUserID = 1

        insert_new_campus(classCamp)
    return redirect('/def_campus')


@app.route('/def_kpi')
def kpi_list():
    set_current_corp() 
    v_kpi = get_kpi_list(publicVars.TermRowId)
    v_dept = get_department()
    v_cat = get_categories()
    return render_template("def_kpi_list.html", kpilist = v_kpi, listDept = v_dept, listCat = v_cat, openType = 0)

@app.route('/pr_kpi')
def pr_kpi():
    set_current_corp() 
    v_kpi = get_kpi_list_by_department(publicVars.CorpID, publicVars.TermRowId, session['UserDepartmentKey'])
    return render_template("def_kpi_list.html", kpilist = v_kpi, openType = 1)


@app.route('/kpi_insert', methods = ['GET', 'POST'])
def kpi_insert():
    classKpi = classKPI()
    if request.method == 'POST':
        classKpi.RowID = request.form['RowID']
        classKpi.CorpID = 1
        classKpi.KPIKey= request.form['KPIKey']
        classKpi.DepartmentKey = request.form['cmbDepartment']
        classKpi.CategoryKey = request.form['cmbCategory']
        classKpi.KPISelfLink = request.form['KPISelfLink']
        classKpi.Version = request.form['Version']
        classKpi.KPI = request.form['KPI']
        classKpi.Weight = request.form['Weight']
        classKpi.DisplayOrder = request.form['DisplayOrder']
        classKpi.ScoreDefinition = request.form['ScoreDefinition']
        classKpi.ScoreCalculationDetails = request.form['ScoreCalculationDetails']
        classKpi.Source = request.form['Source']
        classKpi.IsActive = 1
        classKpi.DmlUserID = 1

        insert_new_kpi(classKpi)
    return redirect('/def_kpi')


@app.route('/kpi_upd', methods = ['GET', 'POST'])
def kpi_upd():
    if request.method == 'POST':
        RowId = request.form['RowID']
        NewWeight = request.form['Weight']
        update_kpi_weight(RowId, NewWeight)
        # flash("Category Updated Successfully")
        return redirect('/pr_kpi')


# PROCESS ------------------------------------------------------------------------
@app.route('/pr_start')
def pr_start():
    return render_template("process_start.html")

@app.route('/insert_process_task')
def insert_process_task():
    TermName = get_term_name(session['TermKey'])
    task_assign(session['CorpID'], session['UserID'], TermName)
    update_process_status(1, 'A', 1)
    return redirect('/home')

@app.route('/pr_end')
def process_end():
    return render_template("process_end.html")

@app.route('/process_end_update')
def process_end_update():
    update_process_status(1, 'P', 1)
    return redirect('/home')


@app.route('/pr_mntr_sum')
def pr_mntr_sum():
    v_DA = get_pr_monitor_sum_by_department(session['CorpID'], session['TermID'], 'D', 'A')
    v_DM = get_pr_monitor_sum_by_department(session['CorpID'], session['TermID'], 'D', 'M')
    v_CA = get_pr_monitor_sum_by_campus(session['CorpID'], session['TermID'], 'C', 'A')
    v_CM = get_pr_monitor_sum_by_campus(session['CorpID'], session['TermID'], 'C', 'M')
    return render_template("process_monitor_sum.html", listDA = v_DA, listDM = v_DM, listCA = v_CA, listCM = v_CM)

@app.route('/pr_monitor')
def process_monitor():
    # get_real_calculated_district_kpi_count, get_real_calculated_campus_kpi_count, get_target_district_kpi_count, get_target_campus_kpi_count
    # district automatic
    v_tda = get_target_district_kpi_count(session['CorpID'], session['TermID'], 'A')
    v_rda = get_real_calculated_district_kpi_count(session['CorpID'], session['TermID'], 'A')
    if v_rda >= v_tda:
        v_dist_auto = True
    else:
        v_dist_auto = False

    # district manuel
    v_tdm = get_target_district_kpi_count(session['CorpID'], session['TermID'], 'M')
    v_rdm = get_real_calculated_district_kpi_count(session['CorpID'], session['TermID'], 'M')
    if v_rdm >= v_tdm:
        v_dist_man = True
    else:
        v_dist_man = False

    # campus automatic
    v_tda = get_target_campus_kpi_count(session['CorpID'], session['TermID'], 'A')
    v_rda = get_real_calculated_campus_kpi_count(session['CorpID'], session['TermID'], 'A')
    if v_rda >= v_tda:
        v_cmp_auto = True
    else:
        v_cmp_auto = False

    # campus manuel
    v_tda = get_target_campus_kpi_count(session['CorpID'], session['TermID'], 'M')
    v_rda = get_real_calculated_campus_kpi_count(session['CorpID'], session['TermID'], 'M')
    if v_rda >= v_tda:
        v_cmp_man = True
    else:
        v_cmp_man = False

    return render_template("process_monitor.html", vda = v_dist_auto, vdm = v_dist_man, vca = v_cmp_auto, vcm = v_cmp_man)


@app.route('/pr_dist_man_entry', methods = ['GET', 'POST'])
def pr_dist_man_entry():
    v_depts = get_department()
    # v_dists = get_districts_for_entry()
    v_TermKey = session['TermKey']
    v_TermID = session['TermID']
    v_DeptKey = session['UserDepartmentKey']
    v_DeptName = get_department_name(session['UserDepartmentKey'])

    v_KpiListCombo = get_district_kpi_list_by_department(session['CorpID'], v_TermKey, session['UserDepartmentKey'])
    v_KPIRowID =  v_KpiListCombo[0][0] # first KPI will be selected
    v_dists = get_districts_for_entry_with_ex_score(v_TermID, v_DeptKey, v_KPIRowID)

    if request.method == 'POST':
        v_KPIRowID = int(request.form['txtKPIRowID'])
        v_dists = get_districts_for_entry_with_ex_score(v_TermID, v_DeptKey, v_KPIRowID)

        length = len(v_KpiListCombo)
        index = 0
        while index < length:
            Kpi = v_KpiListCombo[index][0]
            if  Kpi == v_KPIRowID:
                break
            index += 1

        return render_template("pr_dist_man_entry.html", listDists = v_dists, currentTerm = get_term_name(v_TermKey), DeptName = v_DeptName, listKPI = v_KpiListCombo,
                        defKPI = v_KpiListCombo[index])

    return render_template("pr_dist_man_entry.html", listDists = v_dists, currentTerm = get_term_name(v_TermKey), DeptName = v_DeptName, listKPI = v_KpiListCombo,
                    defKPI = v_KpiListCombo[0])


@app.route("/pr_dist_man_entry_upd", methods = ['GET', 'POST'])
def pr_dist_man_entry_upd():
    if request.method == 'POST':
        # score update method, actually delete insert DML
        v_TermKey = session['TermKey']
        v_TermID = session['TermID']
        v_DistRowID = request.form['varDistrictRowID']
        v_CatKey = request.form['varKPICategoryKey']
        v_DeptRowID = session['UserDepartmentRowID']
        v_KPIRowID = request.form['KPIRowID']
        v_MyScore = int(request.form['score'])
        v_weight = round(float(request.form['varKPIWeight']), 1)
        v_ArtifactURL = request.form['varArtifactURL']       
        
        # print('v_DeptKey', v_DeptRowID, '- v_DistRowID ', v_DistRowID)

        v_CatRowId = get_category_rowid(v_CatKey)

        # def delete_Fact_KPI(CorpId, TermId, KPIRowId, DistrictRowId):
        delete_Fact_KPI(1, v_TermKey, v_KPIRowID, v_DistRowID)
        
        # def insert_Fact_KPI(CorpID, TermRowID, KPIRowID, CategoryRowID, DepartmentRowID, IsKPIApplicable, DistrictRowID, Score, DmlUserID):
        insert_Fact_KPI(1, v_TermKey, v_KPIRowID, v_CatRowId, v_DeptRowID, 1, v_DistRowID, v_MyScore, v_weight, v_ArtifactURL, 1)
        
        return jsonify(status = 'OK')
        #if error 
        #return jsonify(status='error',error='some error text here')


@app.route("/pr_dist_man_entry_bulk", methods = ['POST'])
def pr_dist_man_entry_bulk():
    print('pr_dist_man_entry_bulk geldi')
    if request.method == 'POST':
        print('after post')
        v_TermKey = session['TermKey']
        v_TermID = session['TermID']
        v_DeptRowID = session['UserDepartmentRowID']
        v_CatKey = request.form['varKPICategoryKey']
        v_KPIRowID = request.form['varKPIRowID']

        v_weight = round(float(request.form['varKPIWeight']), 1)

        IDs  = request.form.get('arrayIDs')
        listIDs = IDs.split(",")

        Keys  = request.form.get('arrayKeys') 
        listKeys = Keys.split(",")

        Scores = request.form.get('arrayScores')
        listScores = Scores.split(",")
       
        URLs = request.form.get('arrayURLs')
        listURLs = URLs.split(",")
       
        for i in range(0, len(listIDs)):
            v_DistRowID = listIDs[i]
            v_MyScore = int(listScores[i])
            v_ArtifactURL = listURLs[i]

            v_CatRowId = get_category_rowid(v_CatKey)

            # def delete_Fact_KPI(CorpId, TermId, KPIRowId, DistrictRowId):
            delete_Fact_KPI(1, v_TermKey, v_KPIRowID, v_DistRowID)
            print(1, v_TermKey, v_KPIRowID, v_CatRowId, v_DeptRowID, 1, v_DistRowID, v_MyScore, v_weight, v_ArtifactURL, 1)
            # def insert_Fact_KPI(CorpID, TermRowID, KPIRowID, CategoryRowID, DepartmentRowID, IsKPIApplicable, DistrictRowID, Score, DmlUserID):
            insert_Fact_KPI(1, v_TermKey, v_KPIRowID, v_CatRowId, v_DeptRowID, 1, v_DistRowID, v_MyScore, v_weight, v_ArtifactURL, 1)
        
        return jsonify(status = 'OK')


# ---- campus level entry ***********************
@app.route('/pr_cmp_man_entry', methods = ['GET', 'POST'])
def pr_cmp_man_entry():
    v_depts = get_department()
    v_dists = get_districts()
    v_selDistRowID = v_dists[0][0]
    v_selDistKey = v_dists[0][2]

    v_TermKey = session['TermKey']
    v_TermID = session['TermID']
    v_DeptKey = session['UserDepartmentKey']
    v_DeptName = get_department_name(session['UserDepartmentKey'])

    v_KpiListCombo = get_campus_kpi_list_by_department(session['CorpID'], v_TermKey, session['UserDepartmentKey'])
    v_KPIRowID =  v_KpiListCombo[0][0] # first KPI will be selected

    v_camps = get_campuses_for_entry_with_ex_score(v_TermID, v_DeptKey, v_selDistRowID, v_KPIRowID)

    if request.method == 'POST':        
        v_selDistRowID = int(request.form['varDistrictRowID'])
        v_selDistKey = int(request.form['varDistrictKey'])        
        v_camps = get_campuses_for_entry(v_selDistRowID)

        v_KPIRowID = int(request.form['txtKPIRowID'])
        v_camps = get_campuses_for_entry_with_ex_score(v_TermID, v_DeptKey, v_selDistRowID, v_KPIRowID)

        length = len(v_KpiListCombo)
        index = 0
        while index < length:
            Kpi = v_KpiListCombo[index][0]
            if  Kpi == v_KPIRowID:
                break
            index += 1        

        return render_template("pr_cmp_man_entry.html", listDists = v_dists, listCamps = v_camps, currentTerm = get_term_name(v_TermKey), DeptName = v_DeptName, 
                            listKPI = v_KpiListCombo, defKPI = v_KpiListCombo[index], selDist = v_selDistKey)

    return render_template("pr_cmp_man_entry.html",  listDists = v_dists, listCamps = v_camps, currentTerm = get_term_name(v_TermKey), DeptName = v_DeptName, 
                        listKPI = v_KpiListCombo, defKPI = v_KpiListCombo[0], selDist = v_selDistKey)        


@app.route("/pr_cmp_man_entry_one", methods = ['POST'])
def pr_cmp_man_entry_one():
    if request.method == 'POST':
        print('after post')        
        v_TermKey = session['TermKey']
        v_TermID = session['TermID']
        v_DistRowID = request.form['varDistrictRowID']
        v_CmpRowID = request.form['varCampusRowID']
        v_CatKey = request.form['varKPICategoryKey']
        v_DeptRowID = session['UserDepartmentRowID']
        v_KPIRowID = request.form['KPIRowID']
        v_MyScore = int(request.form['score'])
        v_weight = round(float(request.form['varKPIWeight']), 1)
        v_ArtifactURL = request.form['varArtifactURL']       
        
        print('v_TermKey', 'v_KPIRowID', '- v_DistRowID ', 'v_CmpRowID', v_TermKey, v_KPIRowID, v_DistRowID, v_CmpRowID)

        v_CatRowId = get_category_rowid(v_CatKey)

        print('before delete')
        # def delete_Fact_KPI_Campus(CorpId, TermId, KPIRowId, DistrictRowId, CampusRowId):
        delete_Fact_KPI_Campus(1, v_TermKey, v_KPIRowID, v_DistRowID, v_CmpRowID)
        
        print('before insert')
        # def insert_Fact_KPI_Campus(CorpID, TermRowID, KPIRowID, CampusRowID, CategoryRowID, DepartmentRowID, IsKPIApplicable, DistrictRowID, Score, Weight, ArtifactURL, DmlUserID):
        insert_Fact_KPI_Campus(1, v_TermKey, v_KPIRowID, v_CmpRowID, v_CatRowId, v_DeptRowID, 1, v_DistRowID, v_MyScore, v_weight, v_ArtifactURL, 1)
        print('after insert')
        
        return jsonify(status = 'OK')

        #if error 
        #return jsonify(status='error',error='some error text here')

@app.route("/pr_cmp_man_entry_bulk", methods = ['POST'])
def pr_cmp_man_entry_bulk():
    if request.method == 'POST':
        print('after post')
        v_TermKey = session['TermKey']
        v_TermID = session['TermID']
        v_DistRowID = request.form['varDistrictRowID']
        v_DeptRowID = session['UserDepartmentRowID']
        v_CatKey = request.form['varKPICategoryKey']
        v_KPIRowID = request.form['varKPIRowID']

        print('v_CatKey', v_CatKey)

        v_weight = round(float(request.form['varKPIWeight']), 1)

        IDs  = request.form.get('arrayIDs')
        listIDs = IDs.split(",")

        Keys  = request.form.get('arrayKeys') 
        listKeys = Keys.split(",")

        Scores = request.form.get('arrayScores')
        listScores = Scores.split(",")
       
        URLs = request.form.get('arrayURLs')
        listURLs = URLs.split(",")

        for i in range(0, len(listKeys)):
            v_CmpRowID = listIDs[i]
            v_MyScore = int(listScores[i])
            v_ArtifactURL = listURLs[i]

            v_CatRowId = get_category_rowid(v_CatKey)

            # def delete_Fact_KPI(CorpId, TermId, KPIRowId, DistrictRowId):
            delete_Fact_KPI_Campus(1, v_TermKey, v_KPIRowID, v_DistRowID, v_CmpRowID)
            print(1, v_TermKey, v_KPIRowID, v_CatRowId, v_DeptRowID, 1, v_DistRowID, v_MyScore, v_weight, v_ArtifactURL, 1)
            # def insert_Fact_KPI(CorpID, TermRowID, KPIRowID, CategoryRowID, DepartmentRowID, IsKPIApplicable, DistrictRowID, Score, DmlUserID):
            insert_Fact_KPI_Campus(1, v_TermKey, v_KPIRowID, v_CmpRowID, v_CatRowId, v_DeptRowID, 1, v_DistRowID, v_MyScore, v_weight, v_ArtifactURL, 1)
        
        return jsonify(status = 'OK')


@app.route('/pr_sil')
def pr_sil():
    v_depts = get_department()
    v_dists = get_districts()

    v_KPI_list = get_kpi_list_by_department(1, 12, 10)

    v_TermKey = session['TermKey']
    v_TermID = session['TermID']

    return render_template("pr_district_kpi_man_entry.html", depts = v_depts, dists = v_dists, kpi_list = v_KPI_list, currentTerm = get_term_name(v_TermKey))


@app.route('/pr_dxls')
def pr_dxls():
    
    if not os.path.exists(DOWNLOAD_DIRECTORY):
        os.makedirs(DOWNLOAD_DIRECTORY)
    '''
    v_list = get_district_KPI_list_all()
    v_depts = get_department()
    v_dists = get_districts() 
    '''

    retFile = prepare_excel_docs_for_districts(session['UserDepartmentRowID'], DOWNLOAD_DIRECTORY)

    if retFile is None:
        retFile = ''
    
    FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
    subprocess.run([FILEBROWSER_PATH, DOWNLOAD_DIRECTORY])
    
    return render_template('pr_district_kpi_excel_entry.html', 
                            dirName = UPLOAD_DIRECTORY, mess = retFile + " is prepared and downloaded. First, you must open the excel and fill all values of the SCORE column and then upload it.") 


@app.route('/pr_cxls')
def pr_cxls():

    if not os.path.exists(DOWNLOAD_DIRECTORY):
        os.makedirs(DOWNLOAD_DIRECTORY)

    #retFile = prepare_excel_docs_for_campuses(session['TermID'], session['UserDepartmentRowID'], DOWNLOAD_DIRECTORY)
    retFile = prepare_excel_docs_for_campuses(session['TermID'], session['UserDepartmentRowID'], DOWNLOAD_DIRECTORY)
    if retFile is None:
        retFile = ''
    return render_template('pr_campus_kpi_excel_entry.html', mess = retFile + " is prepared and downloaded. First, you must open the excel and fill all values of the SCORE column and then upload it.") 


@app.route('/dist_kpi_score_entry', methods = ['GET', 'POST'])
def dist_kpi_score_entry():
    if request.method == 'POST':
        KPIRowID = request.form['KPIRowID']
        DeptRowId = request.form['DepartmentRowId']
        CatRowId = request.form['CategoryRowId']
        IsKPIApplicable = request.form['IsKPIApplicable']
        DistrictRowID = request.form['DistrictRowID']
        Score = request.form['Score']

        delete_Fact_KPI(1, session['TermKey'], KPIRowID, DistrictRowID)
        insert_Fact_KPI(1, session['TermKey'], KPIRowID, CatRowId, DeptRowId, IsKPIApplicable, DistrictRowID, Score, 1)
    return redirect('/process_dist_man_entry')


@app.route('/pr_dist_excel_entry', methods=['GET', 'POST'])
def pr_dist_excel_entry():
    if request.method == 'POST':
        try:
            myFile = request.files['file']
            
            if myFile is not None :
                full = UPLOAD_DIRECTORY + myFile.filename
                # first control - xls shett count and district count must be same
                myXls = pd.ExcelFile(myFile)
                sheetCount = len(myXls.sheet_names)
                distCount = len(get_districts())
                
                if sheetCount != distCount:
                    return render_template('pr_district_kpi_excel_entry.html', messType = 'Error', 
                                mess = "District count (" + str(distCount) + ") on system and district count (" + str(sheetCount) + 
                                        ") in the excel file are different. Please confirm that the excel file includes all districts!")

                # this fot is for concat all sheets as a dataframe
                with pd.ExcelFile(myFile) as xls:
                    for i in range(0, sheetCount):
                        df = pd.read_excel(xls, i)
                        if i == 0:
                            dfAll = df
                        else:
                            dfAll = pd.concat([dfAll, df])
                

                return render_template('pr_district_kpi_excel_entry.html', 
                                column_names = dfAll.columns.values, row_data=list(dfAll.values.tolist()), dirName = UPLOAD_DIRECTORY, fileName = full, 
                                mess = "Upload complete. Please check your scores in the grid below.") 
            else:
                return render_template('pr_district_kpi_excel_entry.html', mess = "Please select the file with the filled score!") 

        except Exception as e:
            return render_template('pr_district_kpi_excel_entry.html', mess = "Something is wrong! Error's detail : " + str(e)) 

    return render_template('pr_district_kpi_excel_entry.html', dirName = UPLOAD_DIRECTORY)


# bu method csv den alinan datayi sql servera insert ediyor
@app.route('/pr_xls2', methods=['GET', 'POST'])
def pr_xls2():
    if request.method == 'POST':
        try:
            myFile = request.form['file']
        except Exception as e:
            myFile = request.form['file2']
        
        vDistCount = get_district_count()
        for i in range(0, vDistCount):
            try:
                df = getRowsFromXls(myFile, 'Y', 'D', i)
                if i == 0:
                    dfTotal = df
                
            except Exception as e:
                return render_template('pr_district_kpi_excel_entry.html', messType = 'Error', 
                        mess = "Something went wrong!. Please check uploaded excel file or upload again!. Error's detail : " + str(e)) 

            failScore = False
            failChar = ''
            for index, row in df.iterrows():
                try:
                    cScore = int(df.loc[index, 'Score'])
                except Exception as e:
                    failScore = True
                    failChar = df.loc[index, 'Score']

                # data validation
                if not ( cScore>= 0 and cScore <= 4): 
                    failScore = True
                    failChar = df.loc[index, 'Score']
                if failScore == True:
                    return render_template('pr_district_kpi_excel_entry.html', fullFile = myFile, messType = 'Error', 
                            mess = str(failChar) + ' is unacceptable value. Please fill up the Scores with 0.0 - 4.0 numbers.')

                # adjusted Adjusted_Score
                df.loc[index, 'Adjusted_Score'] = df.loc[index, 'Score'] * df.loc[index, 'Adjusted_Weight']

            CorpID = row['CorpID']
            Term_RowID = row['Term_RowID']
            KPI_RowID = row['KPI_RowID']
            District_RowID = row['District_RowID']
            dfTotal = pd.concat([dfTotal, df]) 
        delKPIOldRecords2(CorpID, Term_RowID, District_RowID)
        insertFactKPI(dfTotal, 'Fact_KPI')
    return render_template('pr_district_kpi_excel_entry.html', fullFile = myFile, mess = 'Save scores process successfully completed')


@app.route('/pr_campus_excel_entry', methods=['GET', 'POST'])
def pr_campus_excel_entry():
    if request.method == 'POST':
        #try:
            myFile = request.files['file']
            
            if myFile is not None :
                full = UPLOAD_DIRECTORY + myFile.filename
                # first control - xls shett count and district count must be same
                myXls = pd.ExcelFile(myFile)
                sheetCount = len(myXls.sheet_names)
                distCount = len(get_campus())
                
                if sheetCount != distCount:
                    return render_template('pr_campus_kpi_excel_entry.html', messType = 'Error', 
                                mess = "Campus count (" + str(distCount) + ") on system and campus count (" + str(sheetCount) + 
                                        ") in the excel file are different. Please confirm that the excel file includes all districts!")

                # this fot is for concat all sheets as a dataframe
                with pd.ExcelFile(myFile) as xls:
                    for i in range(0, sheetCount):
                        df = pd.read_excel(xls, i)
                        if i == 0:
                            dfAll = df
                        else:
                            dfAll = pd.concat([dfAll, df])

                return render_template('pr_campus_kpi_excel_entry.html', 
                                column_names = dfAll.columns.values, row_data = list(dfAll.values.tolist()), dirName = UPLOAD_DIRECTORY, fileName = full, 
                                mess = "Upload complete. Please check your scores in the grid below.") 
            else:
                return render_template('pr_campus_kpi_excel_entry.html', mess = "Please select the file with the filled score!")

        #except Exception as e:
        #    return render_template('pr_district_kpi_excel_entry.html', mess = "Something is wrong! Error's detail : " + str(e)) 

    return render_template('pr_campus_kpi_excel_entry.html', dirName = UPLOAD_DIRECTORY)


@app.route('/pr_xls1', methods=['GET', 'POST'])
def pr_xls1():
    if request.method == 'POST':
        try:
            myFile = request.form['file']
        except Exception as e:
            myFile = request.form['file2']
        
        vCmpCount = get_campus_count()
        for i in range(0, vCmpCount):
            #try:
            df = getRowsFromXls(myFile, 'Y', 'C', i)
            if i == 0:
                dfTotal = df
                
            #except Exception as e:
            #    return render_template('pr_campus_kpi_excel_entry.html', messType = 'Error', 
            #            mess = "Something went wrong!. Please check uploaded excel file or upload again!. Error's detail : " + str(e)) 

            failScore = False
            failChar = ''
            for index, row in df.iterrows():
                try:
                    cScore = int(df.loc[index, 'Score'])
                except Exception as e:
                    failScore = True
                    failChar = df.loc[index, 'Score']

                # data validation
                if not ( cScore>= 0 and cScore <= 4): 
                    failScore = True
                    failChar = df.loc[index, 'Score']
                if failScore == True:
                    return render_template('pr_campus_kpi_excel_entry.html', fullFile = myFile, messType = 'Error', 
                            mess = str(failChar) + ' is unacceptable value. Please fill up the Scores with 0.0 - 4.0 numbers.')
                # adjusted Adjusted_Score
                df.loc[index, 'Adjusted_Score'] = df.loc[index, 'Score'] * df.loc[index, 'Adjusted_Weight']

            CorpID = row['CorpID']
            Term_RowID = row['Term_RowID']
            Department_RowID = row['Department_RowID']
            Campus_RowID = row['Campus_RowID']
            

            dfTotal = pd.concat([dfTotal, df]) 
        delKPICampusOldRecords2(CorpID, Term_RowID, Department_RowID)
        insertFactKPI(dfTotal, 'Fact_KPI_Campus')
    return render_template('pr_campus_kpi_excel_entry.html', fullFile = myFile, mess = 'Save scores process successfully completed.')



# bu method csv den alinan datayi sql servera insert ediyor
# SILINECEK
@app.route('/process_cmp_excel_to_db', methods=['GET', 'POST'])
def process_cmp_excel_to_db():
    if request.method == 'POST':
        myFile = request.form['file2']

        # df = getRowsFromCsv(myFile)
        df = getRowsFromXls(myFile, 'Y', 'C', 0)
        for index, row in df.iterrows():
            #row['RowId'] = 5000 + index
            #df.loc[1].B
            #df.loc[1].at['B']
            CorpID = row['CorpID']
            Term_RowID = row['Term_RowID']
            Campus_RowID = row['Term_RowID']
            KPI_RowID = row['KPI_RowID']
            District_RowID = row['District_RowID']
            delKPICampusOldRecords(CorpID, District_RowID, Campus_RowID, Term_RowID, KPI_RowID)
        
        df.drop(["RowID"], axis = 1, inplace = True) 
        insertFactKPI(df, 'Fact_KPI_Campus')
    return render_template('pr_campus_kpi_excel_entry.html', fullFile = myFile, mess = 'Campus level KPI score saving process is success.')


# USER MANAGEMENT
@app.route('/um_modules')
def um_modules():
    set_current_corp() 
    v_m = get_um_modules()
    return render_template("um_modules.html", modules = v_m)

@app.route('/um_roles')
def um_roles():
    set_current_corp() 
    v_roles = get_um_roles()
    return render_template("um_roles.html", roles = v_roles)

@app.route('/um_users')
def um_users():
    set_current_corp() 
    v_users = get_um_users()
    return render_template("um_users.html", users = v_users)


# ------- SCORE CARDS ------------------------------------------
@app.route("/rep_do/<int:viewType>")
def rep_do(viewType):
    if viewType == 1:
        htmlFile = "rep_do.html"
    else:
        htmlFile = "rep_do2.html"
    session['DictrictScoreViewType'] = viewType

    TermKey = session['TermKey']
    #year = datetime.date.today().year
    v_terms = get_terms()
    v_dist = get_districts()
    v_hps_top = get_rep_hps_top_score(TermKey)
    if v_hps_top is None:
        v_hps_top = 0
    return render_template(htmlFile, listTerms = v_terms, selDist = 00, listDists = v_dist, hpsScore = v_hps_top)


@app.route("/rep_do2", methods = ["GET", "POST"])
def rep_do2():
    if request.method == 'POST':
        if session['DictrictScoreViewType'] == 1:
            htmlFile = "rep_do.html"
        else:
            htmlFile = "rep_do2.html"

        vTermKey = int(request.form['varTermKey'])
        vTermName = request.form['varTermName']
        vDistrictKey = int(request.form['varDistrictKey'])
        vDistrictName = request.form['varDistrictName']

        v_terms = get_terms()
        v_dist = get_districts()
        class prevVar():
            TermKey = vTermKey
            TermName = vTermName
            DistrictKey = vDistrictKey
            DistrictName = vDistrictName

        if vDistrictKey == 0:
            v_scores = get_rep_hps_dept_scores(vTermKey)
            v_hps_top = float(get_rep_hps_top_score(vTermKey))
        elif vDistrictKey > 0:
            v_scores = get_rep_dist_dept_scores(vTermKey, vDistrictKey)
            v_hps_top = get_rep_district_top_score(vTermKey, vDistrictKey)

        if v_hps_top is None:
            v_hps_top = 0
        return render_template(htmlFile, listTerms = v_terms, listDists = v_dist, listScores = v_scores, selDist = prevVar.DistrictKey, selTerm = prevVar.TermKey,
                                             prevVar = prevVar,  hpsScore = v_hps_top)
    return redirect("/rep_do/1")


@app.route("/rep_cat/<int:TermKey>/<int:DistKey>/<int:DeptKey>", methods = ["GET", "POST"])
def rep_cat(TermKey,DistKey,DeptKey ):
    # bize, post edilen sayfadaki sevili term ve distric name lazim, onlari geri gonderiyoruz
    vTermKey = TermKey
    class prevVar():
        TermKey = vTermKey
        TermName = get_term_name(TermKey)
        DistrictKey = DistKey
        DistrictName = None
        DepartmentKey = DeptKey
        DepartmentName = get_department_name(DeptKey)

    v_hps_top = get_rep_hps_top_score(TermKey)
    v_terms = get_terms()
    v_dist = get_districts()

    if DistKey == 0:
        v_scores = get_rep_hps_dept_scores(vTermKey)
        v_cat_scores = get_rep_hps_dept_cat_scores(TermKey, DeptKey)
    elif DistKey > 0:
        prevVar.DistrictName = get_district_name(DistKey)
        v_cat_scores = get_rep_dist_dept_cat_scores(TermKey, DistKey, DeptKey)
        v_scores = get_rep_dist_dept_scores(vTermKey, DistKey)

    if session['DictrictScoreViewType'] == 1:
        htmlFile = "rep_do.html"
    else:
        htmlFile = "rep_do2.html"

    return render_template(htmlFile, listTerms = v_terms, listDists = v_dist, listScores = v_scores, listCatScores = v_cat_scores, 
                                        selDist = prevVar.DistrictKey, selTerm = prevVar.TermKey, prevVar = prevVar, hpsScore = v_hps_top)


@app.route("/rep_cat_kpi/<int:TermKey>/<int:DistKey>/<int:DeptKey>/<int:CatKey>", methods = ["GET", "POST"])
def rep_cat_kpi(TermKey, DistKey, DeptKey, CatKey ):
    # bize, post edilen sayfadaki sevili term ve distric name lazim, onlari geri gonderiyoruz
    vTermKey = TermKey
    class prevVar():
        TermKey = vTermKey
        TermName = get_term_name(TermKey)
        DistrictKey = DistKey
        DistrictName = None
        DepartmentKey = DeptKey
        DepartmentName = get_department_name(DeptKey)
        CategoryKey = DeptKey
        CategoryName = get_category_name(CatKey)

    v_hps_top = get_rep_hps_top_score(TermKey)
    v_terms = get_terms()
    v_dist = get_districts()

    if DistKey == 0:
        v_scores = get_rep_hps_dept_scores(vTermKey)
        v_cat_scores = get_rep_hps_dept_cat_scores(TermKey, DeptKey)
        v_kpi_scores = get_rep_hps_kpi_scores(TermKey, DeptKey, CatKey)
    elif DistKey > 0:
        prevVar.DistrictName = get_district_name(DistKey)
        v_scores = get_rep_dist_dept_scores(vTermKey, DistKey)
        v_cat_scores = get_rep_dist_dept_cat_scores(TermKey, DistKey, DeptKey)
        v_kpi_scores = get_rep_dist_kpi_scores(TermKey, DistKey, DeptKey, CatKey)

    if session['DictrictScoreViewType'] == 1:
        htmlFile = "rep_do.html"
    else:
        htmlFile = "rep_do2.html"

    return render_template(htmlFile, listTerms = v_terms, listDists = v_dist, listScores = v_scores, listCatScores = v_cat_scores, 
                                        listKPIScores = v_kpi_scores, selDist = prevVar.DistrictKey, selTerm = prevVar.TermKey, prevVar = prevVar, hpsScore = v_hps_top)


# also campus kpi card view
@app.route("/rep_cmp")
def rep_cmp():
    TermKey = session['TermKey']
    #year = datetime.date.today().year
    v_terms = get_terms()
    v_dist = get_districts()
    v_hps_top = get_rep_hps_top_score(TermKey)
    if v_hps_top is None:
        v_hps_top = 0
    return render_template("rep_cmp.html", listTerms = v_terms, listDists = v_dist, hpsScore = v_hps_top)


@app.route("/rep_cmp2", methods = ["GET", "POST"])
def rep_cmp2():
    if request.method == 'POST':
        vTermKey = int(request.form['varTermKey'])
        vTermName = request.form['varTermName']
        vDistrictKey = int(request.form['varDistrictKey'])
        vDistrictName = request.form['varDistrictName']

        v_terms = get_terms()
        v_dist = get_districts()
        class prevVar():
            TermKey = vTermKey
            TermName = vTermName
            DistrictKey = vDistrictKey
            DistrictName = vDistrictName

        v_scores = get_rep_dist_campus_scores(vTermKey, vDistrictKey)

        v_hps_top = float(get_rep_hps_top_score(vTermKey))

        if v_hps_top is None:
            v_hps_top = 0
        return render_template("rep_cmp.html", listTerms = v_terms, listDists = v_dist, listScores = v_scores, selDist = prevVar.DistrictKey, selTerm = prevVar.TermKey,
                                             prevVar = prevVar,  hpsScore = v_hps_top)
    return redirect("/rep_cmp2")


@app.route("/rep_cmp_cat/<int:TermKey>/<int:DistKey>/<int:CmpKey>", methods = ["GET", "POST"])
def rep_cmp_cat(TermKey, DistKey, CmpKey):
    # bize, post edilen sayfadaki sevili term ve distric name lazim, onlari geri gonderiyoruz
    vTermKey = TermKey
    class prevVar():
        TermKey = vTermKey
        TermName = get_term_name(TermKey)
        DistrictKey = DistKey
        DistrictName = get_district_name(DistKey)
        CampusKey = CmpKey
        CampusName = get_campus_name(CampusKey)

    v_hps_top = get_rep_hps_top_score(TermKey)
    v_terms = get_terms()
    v_dist = get_districts()

    prevVar.DistrictName = get_district_name(DistKey)
    v_scores = get_rep_dist_campus_scores(vTermKey, DistKey)
    v_cat_scores = get_rep_dist_campus_category_scores(TermKey, CmpKey)
    return render_template("rep_cmp.html", listTerms = v_terms, listDists = v_dist, listScores = v_scores, listCatScores = v_cat_scores, 
                                        selDist = prevVar.DistrictKey, selTerm = prevVar.TermKey, prevVar = prevVar, hpsScore = v_hps_top)


@app.route("/rep_cmp_kpi/<int:TermKey>/<int:DistKey>/<int:CmpKey>/<int:CatKey>", methods = ["GET", "POST"])
def rep_cmp_kpi(TermKey, DistKey, CmpKey, CatKey ):
    # bize, post edilen sayfadaki sevili term ve distric name lazim, onlari geri gonderiyoruz
    vTermKey = TermKey
    class prevVar():
        TermKey = vTermKey
        TermName = get_term_name(TermKey)
        DistrictKey = DistKey
        DistrictName = get_district_name(DistKey)
        CampusKey = CmpKey
        CampusName = get_campus_name(CmpKey)
        CategoryKey = CatKey
        CategoryName = get_category_name(CatKey)

    v_hps_top = get_rep_hps_top_score(TermKey)
    v_terms = get_terms()
    v_dist = get_districts()

    v_scores = get_rep_dist_campus_scores(vTermKey, DistKey)
    v_cat_scores = get_rep_dist_campus_category_scores(TermKey, CmpKey)
    v_kpi_scores = get_rep_campus_kpi_scores(TermKey, CmpKey, CatKey)

    return render_template("rep_cmp.html", listTerms = v_terms, listDists = v_dist, listScores = v_scores, listCatScores = v_cat_scores, 
                                        listKPIScores = v_kpi_scores, selDist = prevVar.DistrictKey, selTerm = prevVar.TermKey, prevVar = prevVar, hpsScore = v_hps_top)


# list scores
@app.route("/rep_kpi", methods = ["GET", "POST"])
def rep_kpi():
    v_terms = get_terms()
    v_dists = get_districts()
    v_depts = get_department()
    v_cats = get_categories()

    if request.method == 'POST':
        vTermKey = int(request.form['cmbTerm'])
        vDistrictKey = int(request.form['cmbDistrict'])
        vDepartmentKey = int(request.form['cmbDepartment'])
        vCategoryKey = int(request.form['cmbCategory'])

        class prevVar():
            TermKey = vTermKey
            DistrictKey = vDistrictKey
            DepartmentKey = vDepartmentKey
            CategoryKey = vCategoryKey

        if vDistrictKey == 0:
            v_score = get_rep_hps_kpi_scores(vTermKey, vDepartmentKey, vCategoryKey)
        else:
            v_score = get_rep_dist_kpi_scores(vTermKey, vDistrictKey, vDepartmentKey, vCategoryKey)

        return render_template("rep_kpi.html", listTerms = v_terms, listDists = v_dists, listDepts = v_depts, listCats = v_cats, listScore = v_score, prevVar = prevVar)
    return render_template("rep_kpi.html", listTerms = v_terms, listDists = v_dists, listDepts = v_depts, listCats = v_cats)


@app.route("/rep_kpi2/<int:TermKey>/<int:DistKey>/<int:DeptKey>/<int:CatKey>", methods = ["GET", "POST"])
def rep_kpi2(TermKey, DistKey, DeptKey, CatKey):
    vTermKey = TermKey
    class prevVar():
        TermKey = vTermKey
        DistrictKey = DistKey
        DepartmentKey = DeptKey
        CategoryKey = CatKey
    v_terms = get_terms()
    v_dists = get_districts()
    v_depts = get_department()
    v_cats = get_categories()

    if DistKey == 0:
        v_score = get_rep_hps_kpi_scores(TermKey, DeptKey, CatKey)
    else:
        v_score = get_rep_dist_kpi_scores(TermKey, DistKey, DeptKey, CatKey)
    return render_template("rep_kpi.html", listTerms = v_terms, listDists = v_dists, listDepts = v_depts, listCats = v_cats, listScore = v_score, prevVar = prevVar)


@app.route("/rep_list_kpi", methods = ["GET", "POST"])
def rep_list_kpi():
    v_terms = get_terms()
    v_dists = get_districts()
    v_depts = get_department()
    
    if request.method == 'POST':
        vTermKey = int(request.form['cmbTerm'])
        vDistrictKey = int(request.form['cmbDistrict'])
        vCampusKey = int(request.form['cmbCampus'])
        vDepartmentKey = int(request.form['cmbDepartment'])
        vCategoryKey = int(request.form['cmbCategory'])

        v_camps = get_campus_by_district(vDistrictKey)
        v_cats = get_categories_by_department(vDepartmentKey)

        class prevVar():
            TermKey = vTermKey
            DistrictKey = vDistrictKey
            DepartmentKey = vDepartmentKey
            CategoryKey = vCategoryKey
            CampusKey = vCategoryKey

        if vDistrictKey == 0:
            v_score = get_rep_hps_kpi_scores(vTermKey, vDepartmentKey, vCategoryKey)
        else:
            v_score = get_rep_dist_campus_kpi_score_list(vTermKey, vDistrictKey, vCampusKey, vDepartmentKey, vCategoryKey)

        return render_template("rep_campus_kpi.html", listTerms = v_terms, listDists = v_dists, listCamps = v_camps, listDepts = v_depts, listCats = v_cats, listScore = v_score, prevVar = prevVar)
    else:
        v_camps = get_campus()
        v_cats = get_categories()
    return render_template("rep_campus_kpi.html", listTerms = v_terms, listDists = v_dists, listCamps = v_camps, listDepts = v_depts, listCats = v_cats)


@app.route('/rep_low', methods = ["GET", "POST"])
def rep_low():
    v_terms = get_terms()
    
    if request.method == 'POST':
        vTermKey = int(request.form['cmbTerm'])
        get_rep_low_hps_dept_category_scores, get_rep_low_dist_department_scores, get_rep_low_hps_department_scores, get_rep_low_district_scores

        v_low_dist = get_rep_low_district_scores(vTermKey)
        v_low_depts = get_rep_low_hps_department_scores(vTermKey)
        v_low_dist_dept = get_rep_low_dist_department_scores(vTermKey)
        v_low_dept_cat = get_rep_low_hps_dept_category_scores(vTermKey)

        return render_template("rep_low.html", listTerms = v_terms, listDist = v_low_dist, listDept = v_low_depts, listDistDept = v_low_dist_dept, listDeptCat = v_low_dept_cat)
    return render_template("rep_low.html", listTerms = v_terms)

@app.route("/rep_view_file", methods = ["GET", "POST"])
def rep_view_file():
    v_terms = get_terms()
    v_dists = get_districts()
    vFirstDistKey = v_dists[0][0]
    v_camps = get_campus_by_district(vFirstDistKey)
    v_depts = get_department()
    
    if request.method == 'POST':
        vTermKey = int(request.form['cmbTerm'])
        vDistrictKey = int(request.form['cmbDistrict'])
        vCampusKey = int(request.form['cmbCampus'])
        vDepartmentKey = int(request.form['cmbDepartment'])
        vCategoryKey = int(request.form['cmbCategory'])

        v_camps = get_campus_by_district(vDistrictKey)
        v_cats = get_categories_by_department(vDepartmentKey)
        v_kpi = get_kpi_by_categories(vCategoryKey)

        vKPI = request.form['cmbKpi']
        v_file = get_KPI_artifact_file(1, vTermKey, vKPI)


        if v_file is not None:
            v_file_name = v_file[0]
        else:
            v_file_name = None

        class prevVar():
            TermKey = vTermKey
            DistrictKey = vDistrictKey
            DepartmentKey = vDepartmentKey
            CampusKey = vCategoryKey
            CategoryKey = vCategoryKey
            KPIKey = vKPI

        if vDistrictKey == 0:
            v_score = get_rep_hps_kpi_scores(vTermKey, vDepartmentKey, vCategoryKey)
        else:
            v_score = get_rep_dist_campus_kpi_score_list(vTermKey, vDistrictKey, vCampusKey, vDepartmentKey, vCategoryKey)

        return render_template("rep_view_file.html", listTerms = v_terms, listDists = v_dists, listCamps = v_camps, listDepts = v_depts, 
            listCats = v_cats, listScore = v_score, listKPI = v_kpi, file_name = v_file_name, prevVar = prevVar)

    else:
        v_cats = get_categories()
    return render_template("rep_view_file.html", listTerms = v_terms, listDists = v_dists, listCamps = v_camps, listDepts = v_depts, listCats = v_cats)

# ------- END SCORE CARDS ---------------------------------------


@app.route('/map')
def map():
    return render_template('TX_County.html')


@app.route('/map/<int:CountyID>')
def map3(CountyID):
    v_dist_name = get_district_name(CountyID)
    v_dist = get_selected_district_past_scores(CountyID, 2)
    # v_dept = get_selected_dist_dept_past_scores(CountyID, 2)
    # v_campus = get_selected_district_campus_past_scores(CountyID, 2)
    # bu kapatilanlar last x termdeki scorelari getiriyor. ancak sadece secilen term gelsin istendi
    v_dept = get_rep_dist_dept_scores(session['TermKey'], CountyID)
    v_campus = get_rep_dist_campus_scores(session['TermKey'], CountyID)
    
    return render_template('TX_County.html', chartValuesDist = v_dist, chartValuesDept = v_dept, chartValuesCmp = v_campus, distName = v_dist_name,
            distKey =  CountyID, termKey = session['TermKey'])

@app.route('/map2', methods = ["GET", "POST"])
def map2():
    CountyID = request.form['varDistrictKey']
    vTermName = request.form['varTermName']

    v_dist_name = get_district_name(CountyID)
    v_dist = get_selected_district_past_scores(CountyID, 2)
    TermKey = get_term_key(vTermName)
    # v_dept = get_selected_dist_dept_past_scores(CountyID, 2)
    # v_campus = get_selected_district_campus_past_scores(CountyID, 2)
    # bu kapatilanlar last x termdeki scorelari getiriyor. ancak sadece secilen term gelsin istendi
    v_dept = get_rep_dist_dept_scores(TermKey, CountyID)
    v_campus = get_rep_dist_campus_scores(TermKey, CountyID)
    
    return render_template('TX_County.html', chartValuesDist = v_dist, chartValuesDept = v_dept, chartValuesCmp = v_campus, 
            distName = v_dist_name, distKey =  CountyID, termKey = TermKey, termName = vTermName)


@app.route('/map/<int:CountyID>/<string:TermName>')
def map4(CountyID, TermName):
    v_dist_name = get_district_name(CountyID)
    v_dist = get_selected_district_past_scores(CountyID, 2)
    TermKey = get_term_key(TermName)
    # v_dept = get_selected_dist_dept_past_scores(CountyID, 2)
    # v_campus = get_selected_district_campus_past_scores(CountyID, 2)
    # bu kapatilanlar last x termdeki scorelari getiriyor. ancak sadece secilen term gelsin istendi
    v_dept = get_rep_dist_dept_scores(TermKey, CountyID)
    v_campus = get_rep_dist_campus_scores(TermKey, CountyID)
    
    return render_template('TX_County.html', chartValuesDist = v_dist, chartValuesDept = v_dept, chartValuesCmp = v_campus, 
            distName = v_dist_name, distKey =  CountyID, termKey = TermKey)



@app.route('/rep_chart')
def rep_chart():
    return render_template('rep_chart.html')


@app.route('/bar')
def bar():
    v_all = get_hps_all_term_scores(2) # past 2 years terms 
    # v_all_dist = get_district_all_term_scores(2) # past 2 years terms 
    v_all_dist = get_all_districts_term_scores(publicVars.TermKey)
    v_all_dept = get_all_departments_term_scores(publicVars.TermKey)
    TermName = get_term_name(publicVars.TermKey)
    v_all_cmp = get_all_campuses_term_scores(publicVars.TermKey)
    return render_template('bar_chart.html', max = 4, chartValues = v_all, chartValuesDist = v_all_dist, chartValuesDept = v_all_dept, chartValuesCmp = v_all_cmp,
                                            selectedTermName = TermName)

@app.route('/bar/<int:termIndex>')
def bar2(termIndex):
    v_all = get_hps_all_term_scores(2) # past 2 years terms 
    v_term = v_all[termIndex][0] 
    v_all_dist = get_all_districts_term_scores(v_term)
    v_all_dept = get_all_departments_term_scores(v_term)
    v_all_cmp = get_all_campuses_term_scores(v_term)
    TermName = get_term_name(v_term)
    return render_template('bar_chart.html', max = 4, chartValues = v_all, chartValuesDist = v_all_dist, chartValuesDept = v_all_dept, chartValuesCmp = v_all_cmp,
                                            selectedTermName = TermName)


@app.route('/bar_dist')
def bar_dist():
    v_all_dist = get_all_districts_term_scores(publicVars.TermKey)
    return render_template('bar_dist.html', max = 4, chartValuesDist = v_all_dist)

@app.route('/bar_dept')
def bar_dept():
    v_all = get_all_departments_term_scores(publicVars.TermKey)
    return render_template('bar_dept.html', max = 4, chartValues = v_all)


@app.route('/json2')
def json2():
    year = datetime.date.today().year
    v_terms = get_year_term_list(year-2)
    return render_template('test.html', listTerms = v_terms)




if __name__ == "__main__":
    app.secret_key = "mysupersecretkey:)"
    #app.secret_key = os.urandom(24)
    app.run(debug=True)
