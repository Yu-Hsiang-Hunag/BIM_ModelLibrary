#coding: utf-8
# module we will need
import datetime, time, json, keyboard, pymysql, ifcopenshell, os, re, math, datetime, requests, configparser
from web3 import Web3
from flask import Flask, request, redirect, url_for, jsonify, request, render_template, send_from_directory
from flask_api import status
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import pandas as pd
from create_table.create_table import create_database
import uuid
from Insert_FileRule import insert_to_database, file_rule
from query_database import query

#python use http connect to Ethereum, private chain architecture 
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:9101'))
print(w3.isConnected()) #confirm connection is True

path = os.path.abspath('.')
cfgpath = path.split('python_code')[0] + 'python_code/config.ini'

config = configparser.ConfigParser()
config.read(cfgpath)

# Define Flask
app = Flask(__name__)
CORS(app) # solve CORS problem, 測試時不用經過驗證，利用token去做驗證
app_router = '/Product/v3' # router url

create_database() # 創建資料庫與表格

@app.route(app_router+'/model_data', methods=['POST'])
@cross_origin()
def model_data():
    # 判斷必要參數
    if not request.form.get("S_ManufacturerAccountID"): # 製造商帳戶
        return jsonify({"error" : "Require accountID"}), status.HTTP_400_BAD_REQUEST
    if not request.form.get("S_ModelCategory"):
        return jsonify({"error" : "Require ModelCategory"}), status.HTTP_400_BAD_REQUEST # 模型系統、類別
    if not request.form.get("S_ModelName"):
        return jsonify({"error" : "Require ModelName"}), status.HTTP_400_BAD_REQUEST # 模型名稱
    if not request.form.get("S_ModelNumber"):
        return jsonify({"error" : "Require ModelNumber"}), status.HTTP_400_BAD_REQUEST # 模型型號
    # if not request.form.get("I_ModelFormat"):
    #     return jsonify({"error" : "Require ModelFormat"}) # 模型格式 ， 前台能選擇Format，但LOD不能選
    # if not request.form.get("S_ModelLOD"): # LOD資訊沒有在其中
    #     return jsonify({"error" : "Require ModelLOD"})
    S_ManufacturerAccountID = request.form.get('S_ManufacturerAccountID')
    S_ModelCategory = request.form.get("S_ModelCategory")
    S_ModelName = request.form.get("S_ModelName")
    S_ModelNumber = request.form.get("S_ModelNumber")
    S_ManufacturerName = request.form.get("S_ManufacturerName")
    ###### 以上為必要
    S_ModelSubCategory = request.form.get('S_ModelSubCategory')
    F_ModelHeight = request.form.get('F_ModelHeight') # ModelSizeID, ModelWarrarnyt
    F_ModelLength = request.form.get('F_ModelLength') # ModelSizeID, ModelWarrarnyt
    F_ModelWidth = request.form.get('F_ModelWidth') # ModelSizeID, ModelWarrarnyt
    I_ModelUnit = request.form.get('I_ModelUnit') # ModelFileInfo
    B_ModelImage = request.form.get('B_ModelImage')
    S_ModelMaterial = request.form.get('S_ModelMaterial') # ModelSizeID, ModelSize
    S_Location = request.form.get('S_Location')
    S_ModelDescription = request.form.get('S_ModelDescription') # S_WarrantyID, ModelWarrarnyt
    S_ModelProductURL = request.form.get('S_ModelProductURL')
    D_WarrantyDuration = request.form.get('D_WarrantyDuration') # S_WarrantyID, ModelWarrarnyt
    S_WarrantyDescription = request.form.get('S_WarrantyDescription')
    S_OtherProperties = request.form.get('S_OtherProperties')
    Remark = request.form.get('Remark')
    
    return_to = insert_to_database(S_ManufacturerAccountID, S_ModelCategory, S_ModelName, S_ModelNumber,
        S_ModelSubCategory, F_ModelHeight, F_ModelLength, F_ModelWidth, I_ModelUnit, S_ModelMaterial, S_Location,
        S_ModelDescription, S_ModelProductURL, D_WarrantyDuration, S_WarrantyDescription, S_OtherProperties, S_ManufacturerName, Remark, B_ModelImage)

    return return_to

@app.route(app_router+'/model_file', methods=['POST'])
@cross_origin()
def model_file():
    api_time_start = time.time()
    S_ModelID = request.form.get('S_ModelID')
    I_ModelFormat = request.form.get('I_ModelFormat')
    I_ModelLOD = request.form.get('I_ModelLOD')
    S_ModelCover = request.form.get("S_ModelCover")
    # 判斷上傳檔案是否存在
    F_UploadFile = request.files['F_UploadFile']
    return_to = file_rule(F_UploadFile, S_ModelID, I_ModelFormat, I_ModelLOD, S_ModelCover)
    api_time_end = time.time()
    print("total api time :", api_time_end - api_time_start)
    return return_to

@app.route(app_router+'/model', methods=['GET'])
@cross_origin()
def model_query():
    S_ModelID = request.args.get('S_ModelID')
    S_ModelCategory = request.args.get('S_ModelCategory')
    S_ManufacturerName = request.args.get('S_ManufacturerName')
    S_ModelName = request.args.get('S_ModelName')
    # S_ModelNumber = request.args.get('S_ModelNumber')
    S_Location = request.args.get('S_Location')
    S_ModelSubCategory = request.args.get('S_ModelSubCategory')
    I_ModelFormat = request.args.get('I_ModelFormat')
    Model_File_Name = request.args.get('Model_File_Name')
    if S_ModelID != None and Model_File_Name != None:
        db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
        cursor = db.cursor()
        sql_find = "SELECT S_ModelFilePath from Model_Info WHERE S_ModelID = '%s'"%(S_ModelID)
        cursor.execute(sql_find)
        File_Path = cursor.fetchone()
        print("File Path", File_Path)
        print(type(File_Path))
        File_Path = str(File_Path) # 搜尋出來資料型態是tuple，因為搜尋路徑需要string
        File_Path = File_Path.strip("(),'")
        print("File Path", File_Path)
        File_Name = os.listdir(File_Path)
        print("File in Server", File_Name)
        Model_File_Name_Format = Model_File_Name.rsplit("_",1)[1]
        print("Model File Format", Model_File_Name_Format)
        # 搜尋最新版檔案
        sql_find = ("SELECT I_Version from Model_File_Info WHERE S_ModelID = '%s' ORDER BY I_Index DESC")%(S_ModelID)
        cursor.execute(sql_find)
        I_Version = cursor.fetchone()
        print("I_Version", I_Version)
        I_Version = str(I_Version) # 處理Version型態，需要消除搜尋出來的(),
        I_Version = I_Version.strip("(),")
        print("I_Version", I_Version)
        for i in range(len(File_Name)):
            print("single File Name", File_Name[i].rsplit(".",1)[1])
            if Model_File_Name_Format == "01":
                Model_File_Name1 = Model_File_Name + "_" + I_Version + "." + File_Name[i].rsplit(".",1)[1] # Model_File_Name1為比對的名字
            elif Model_File_Name_Format == "02":
                Model_File_Name1 = Model_File_Name + "_" + I_Version + "." + File_Name[i].rsplit(".",1)[1]
            elif Model_File_Name_Format == "03":
                Model_File_Name1 = Model_File_Name + "_" + I_Version + "." + File_Name[i].rsplit(".",1)[1]
            elif Model_File_Name == "04":
                Model_File_Name1 = Model_File_Name + "_" + I_Version + "." + File_Name[i].rsplit(".",1)[1]
            print("Model_File_Name", Model_File_Name)
            if Model_File_Name1 == File_Name[i]:
                print(Model_File_Name)
                sql_update = ("UPDATE Model_File_Info SET I_Downloads = I_Downloads + 1 WHERE S_ModelID = %s and S_FileName = %s and I_Version = %s")
                val_update = (S_ModelID, Model_File_Name, I_Version)
                cursor.execute(sql_update, val_update)
                db.commit()
                print("Update success")
                return send_from_directory(File_Path, Model_File_Name1, as_attachment=True), status.HTTP_200_OK
        db.close()
        return jsonify({"File_01":"No such file!!"}), status.HTTP_400_BAD_REQUEST
    else:
        return_to = query(S_ModelID, S_ModelCategory, S_ManufacturerName, S_Location, S_ModelSubCategory, I_ModelFormat) # query function
        print(return_to)
        return return_to

@app.route(app_router+'/model', methods=['PATCH'])
@cross_origin()
def model_update():
    request_data = request.get_json()
    # 必要參數(必須要有才能修改)
    S_ManufacturerAccountID = request_data['S_ManufacturerAccountID']
    S_ModelID = request_data['S_ModelID']
    S_ModelCategory = request_data['S_ModelCategory']
    S_ManufacturerName = request_data['S_ManufacturerName']
    S_ModelName = request_data['S_ModelName']
    S_ModelNumber = request_data['S_ModelNumber']
    # I_ModelFormat = request_data['I_ModelFormat']
    # I_ModelLOD = request_data['I_ModelLOD']
    # 修正參數
    S_ModelSubCategory = request_data['S_ModelSubCategory']
    F_ModelHeight = request_data['F_ModelHeight']
    F_ModelLength = request_data['F_ModelLength']
    F_ModelWidth = request_data['F_ModelWidth']
    S_ModelMaterial = request_data['S_ModelMaterial']
    S_Location = request_data['S_Location']
    S_ModelDescription = request_data['S_ModelDescription']
    B_ModelImage = request_data['B_ModelImage']
    S_ModelProductURL = request_data['S_ModelProductURL']
    D_WarrantyStart = request_data['D_WarrantyStart']
    D_WarrantyDuration = request_data['D_WarrantyDuration']
    S_WarrantyDescription = request_data['S_WarrantyDescription']
    S_OtherProperties = request_data['S_OtherProperties']
    Remark = request_data['Remark']

    # connect to db
    db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    cursor = db.cursor()
    # update sql command
    sql_update_Model_Info = ("UPDATE Model_Info SET S_ModelSubCategory = %s, S_Location = %s, S_ModelDescription = %s, B_ModelImage = %s, S_ModelProductURL = %s, S_OtherProperties = %s \
        WHERE S_ModelID = %s and S_ModelCategory = %s and S_ManufacturerName = %s and S_ModelName = %s and S_ModelNumber = %s")
    val_update_Model_Info = (S_ModelSubCategory, S_Location, S_ModelDescription, B_ModelImage, S_ModelProductURL, S_OtherProperties, S_ModelID, S_ModelCategory, S_ManufacturerName, 
    S_ModelName, S_ModelNumber)
    cursor.execute(sql_update_Model_Info, val_update_Model_Info)
    db.commit()
    
    sql_findID = ("SELECT S_WarrantyID, S_ModelSizeID from Model_Info WHERE S_ModelID = '%s' and S_ModelCategory = '%s' and S_ManufacturerName = '%s' and S_ModelName = '%s' and \
        S_ModelNumber = '%s'")%(S_ModelID, S_ModelCategory, S_ManufacturerName, S_ModelName, S_ModelNumber)
    cursor.execute(sql_findID)
    data = cursor.fetchone()
    sql_update_Model_Warranty = ("UPDATE Model_Warranty SET D_WarrantyDuration = %s, S_WarrantyDescription = %s WHERE S_WarrantyID = %s")
    val_update_Model_Warranty = (D_WarrantyDuration, S_WarrantyDescription, data[0])
    cursor.execute(sql_update_Model_Warranty, val_update_Model_Warranty)
    db.commit()
    sql_update_Model_Size = ("UPDATE Model_Size SET F_ModelHeight = %s, F_ModelLength = %s, F_ModelWidth = %s, S_ModelMaterial = %s WHERE S_ModelSizeID = %s")
    val_update_Model_Size = (F_ModelHeight, F_ModelLength, F_ModelWidth, S_ModelMaterial, data[1])
    cursor.execute(sql_update_Model_Size, val_update_Model_Size)
    db.commit()
    sql_find = "SELECT * from Model_Info WHERE S_ModelID='%s'"%(S_ModelID)
    cursor.execute(sql_find)
    data = cursor.fetchall()
    json_data = []
    for row in data:
        print("totlarow",row)
        result_data1 = {}
        result_data_File_Info = {}
        result_data1["S_ModelID"] = row[1]
        result_data1["S_ModelCategory"] = row[3]
        result_data1["S_ManufacturerName"] = row[4]
        result_data1["S_ModelName"] = row[5]
        result_data1["S_ModelNumber"] = row[6]
        result_data1["S_ModelSubCategory"] = row[7]
        result_data1["S_WarrantyID"] = row[8]
        result_data1["S_ModelSizeID"] = row[9]
        result_data1["S_Location"] = row[10]
        result_data1["S_ModelDescription"] = row[11]
        result_data1["B_ModelImage"] = row[12]
        result_data1["S_ModelProductURL"] = row[14]
        result_data1["S_OtherProperties"] = row[15]
        sql_find_Model_Size = "SELECT F_ModelHeight, F_ModelLength, F_ModelWidth, S_ModelMaterial from Model_Size WHERE S_ModelSizeID = '%s'"%(row[9])
        cursor.execute(sql_find_Model_Size)
        data_Model_Size = cursor.fetchone()
        result_data1["F_ModelHeight"] = data_Model_Size[0]
        result_data1["F_ModelLength"] = data_Model_Size[1]
        result_data1["F_ModelWidth"] = data_Model_Size[2]
        result_data1["S_ModelMaterial"] = data_Model_Size[3]
        sql_find_Model_Warranty = "SELECT D_WarrantyDuration, S_WarrantyDescription from Model_Warranty WHERE S_WarrantyID = '%s'"%(row[8])
        cursor.execute(sql_find_Model_Warranty)
        data_Model_Warranty = cursor.fetchone()
        result_data1["D_WarrantyDuration"] = data_Model_Warranty[0]
        result_data1["S_WarrantyDescription"] = data_Model_Warranty[1]
        sql_find_Model_File_Info = "SELECT * from Model_File_Info WHERE S_ModelID = '%s'"%(row[1])
        cursor.execute(sql_find_Model_File_Info)
        data_Model_File_Info = cursor.fetchall()
        #####
        data_Model_File_list1 = [] # ModelFormat
        data_Model_File_list2 = [] # ModelLOD
        data_Model_File_list3 = [] # ModelFileName
        for row1 in data_Model_File_Info: # Model_FileName, Model_Format, Model_LOD要回傳list
            if row1[2] != None:
                data_Model_File_list1.append(row1[2])
                result_data_File_Info["I_ModelFormat"] = data_Model_File_list1
            if row1[3] != None:
                data_Model_File_list2.append(row1[3])
                result_data_File_Info["I_ModelLOD"] = data_Model_File_list2
            result_data1["I_Likes"] = row1[4]
            result_data1["I_ModelUnit"] = row1[5]
            result_data1["I_Downloads"] = row1[6]
            if row1[7] != None:
                data_Model_File_list3.append(row1[7])
                result_data_File_Info["S_FileName"] = data_Model_File_list3
            result_data1["File_Info"] = result_data_File_Info
        json_data.append(result_data1)
    db.close()
    return json.dumps(json_data), status.HTTP_200_OK

@app.route(app_router+'/model_likes', methods=["GET"])
@cross_origin()
def model_likes():
    S_ModelID = request.args.get('S_ModelID')
    db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    cursor = db.cursor()
    sql_update = ("UPDATE Model_File_Info SET I_Likes = I_Likes + 1 WHERE S_ModelID = %s")
    val_update = (S_ModelID)
    cursor.execute(sql_update, val_update)
    db.commit()
    sql_find = "SELECT I_Likes from Model_File_Info WHERE S_ModelID = '%s'"%(S_ModelID)
    cursor.execute(sql_find)
    data = cursor.fetchone()
    db.close()
    return jsonify({"I_Likes":data}), status.HTTP_200_OK

@app.route(app_router+'/model_location', methods=["GET"])
@cross_origin()
def model_location():
    # connect to db
    db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    cursor = db.cursor()
    sql_find = ("SELECT DISTINCT S_Location from Model_Info")
    cursor.execute(sql_find)
    data = cursor.fetchall()
    location_list = []
    result_data = {}
    for row in data:
        if row[0] != None:
            location_list.append(row[0])
    result_data["S_Location"] = location_list
    db.close()
    return json.dumps(result_data), status.HTTP_200_OK

@app.route(app_router+'/model_manufacturername', methods=["GET"])
@cross_origin()
def model_manufacutername():
    # connect to db
    db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    cursor = db.cursor()
    sql_find = ("SELECT DISTINCT S_ManufacturerName from Model_Info")
    cursor.execute(sql_find)
    data = cursor.fetchall()
    manufacturername_list = []
    result_data = {}
    for row in data:
        if row[0] != None:
            manufacturername_list.append(row[0])
    result_data["S_ManufacturerName"] = manufacturername_list
    db.close()
    return json.dumps(result_data), status.HTTP_200_OK
#主函式
if __name__ == '__main__':
    app.run(host= '0.0.0.0',port=9104,debug=True)
