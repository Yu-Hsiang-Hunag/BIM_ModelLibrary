import datetime, time, keyboard, json, pymysql, os, re, math, datetime, requests, configparser
from flask import Flask, request, redirect, url_for, jsonify, request, render_template, send_from_directory
from flask_api import status
from werkzeug.utils import secure_filename
import pandas as pd
import uuid
import requests
path = os.path.abspath('.')
cfgpath = path.split('python_code')[0] + 'python_code/config.ini'

config = configparser.ConfigParser()
config.read(cfgpath)

def insert_to_database(S_ManufacturerAccountID, S_ModelCategory, S_ModelName, S_ModelNumber,
        S_ModelSubCategory, F_ModelHeight, F_ModelLength, F_ModelWidth, I_ModelUnit, S_ModelMaterial, S_Location,
        S_ModelDescription, S_ModelProductURL, D_WarrantyDuration, S_WarrantyDescription, S_OtherProperties, S_ManufacturerName, Remark, B_ModelImage):
    # connect to database
    db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    cursor = db.cursor()
    ##　ID
    S_ModelID = str(uuid.uuid4()) # table => Model_Info
    # S_ManufacturerAccountID # 前端會給
    S_WarrantyID = str(uuid.uuid4())
    S_ModelSizeID = str(uuid.uuid4())
    # sql command using pymysql
    sql_ModelInfo = ("INSERT INTO Model_Info(S_ModelID, S_ManufacturerAccountID, S_ModelCategory, S_ManufacturerName, S_ModelName, S_ModelNumber, S_ModelSubCategory, S_WarrantyID, \
        S_ModelSizeID, S_Location, S_ModelDescription, S_ModelProductURL, S_OtherProperties, S_ModelStatus, B_ModelImage) \
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    val_ModelInfo = (S_ModelID, S_ManufacturerAccountID, S_ModelCategory, S_ManufacturerName, S_ModelName, S_ModelNumber, S_ModelSubCategory, S_WarrantyID, S_ModelSizeID,
    S_Location, S_ModelDescription, S_ModelProductURL, S_OtherProperties, "0", B_ModelImage)
    cursor.execute(sql_ModelInfo, val_ModelInfo)
    db.commit()
    
    # 這個時候還沒有檔案，所以沒有LOD資訊，當檔案建立的時候，就會有LOD資訊
    sql_Model_File_Info = ("INSERT INTO Model_File_Info(S_ModelID, I_ModelUnit, D_ModelStatus, I_Likes) VALUES(%s,%s,%s,%s)")
    val_Model_File_Info = (S_ModelID, I_ModelUnit, 0, 0)
    cursor.execute(sql_Model_File_Info, val_Model_File_Info)
    db.commit()

    sql_Model_Warranty = ("INSERT INTO Model_Warranty(S_WarrantyID, D_WarrantyDuration, S_WarrantyDescription) VALUES(%s,%s,%s)")
    val_Model_Warranty = (S_WarrantyID, D_WarrantyDuration, S_WarrantyDescription)
    cursor.execute(sql_Model_Warranty, val_Model_Warranty)
    db.commit()

    sql_Model_Size = ("INSERT INTO Model_Size(S_ModelSizeID, F_ModelHeight, F_ModelLength, F_ModelWidth, S_ModelMaterial) VALUES(%s,%s,%s,%s,%s)")
    val_Model_Size = (S_ModelSizeID, F_ModelHeight, F_ModelLength, F_ModelWidth, S_ModelMaterial)
    cursor.execute(sql_Model_Size, val_Model_Size)
    db.commit()
    db.close()
    return jsonify({"ModelID":S_ModelID}), status.HTTP_200_OK

def file_rule(Model_File, S_ModelID, I_ModelFormat, I_ModelLOD, S_ModelCover):
    # datetime object containing current date and time
    now = datetime.datetime.now()
    print("now =", now)
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dt_string)

    # 檔案命名規則 ： 類別 _製造商_設備名稱_型號_LOD_格式代號
    # 前端有的參數 Category, ModelName, ModelNumber
    # 搜尋資料庫內容
    db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    cursor = db.cursor()
    sql_find = "SELECT * from Model_Info WHERE S_ModelID = '%s'"%(S_ModelID)
    cursor.execute(sql_find)
    data = cursor.fetchall()
    json_data = []
    result_data = {}
    for row in data:
        result_data['S_ModelID'] = row[1]
        result_data['S_ManufacturerAccountID'] = row[2]
        result_data['S_ModelCategory'] = row[3]
        result_data['S_ManufacturerName'] = row[4]
        result_data['S_ModelName'] = row[5]
        result_data['S_ModelNumber'] = row[6]
        json_data.append(result_data)
    
    S_ModelCategory = result_data['S_ModelCategory']
    S_ModelName = result_data['S_ModelName']
    S_ModelNumber = result_data['S_ModelNumber']
    S_ManufacturerAccountID = result_data['S_ManufacturerAccountID']
    S_ManufacturerName = result_data['S_ManufacturerName']
    Model_File_Format = Model_File.filename.rsplit('.',1)[1] # 判斷附檔名是否符合規則 ，上傳檔案副檔名
    
    if ((Model_File_Format != 'obj') and (Model_File_Format != 'OBJ') and (Model_File_Format != 'gltf') and (Model_File_Format != 'dae') and (Model_File_Format != 'fbx') and (Model_File_Format != 'zip')):
        return jsonify({"error" : "File format not allowed"}), status.HTTP_400_BAD_REQUEST # 不符合規則回應錯誤

    Model_File_Name = Model_File.filename.rsplit('.',1)[0] # 取得 . 前面的名字 
    print("Model_File_Name", Model_File_Name)
    print("Model_File_Format ： ", Model_File_Format)
    print("Model_File_Format_Type ： ", type(Model_File_Format))
    Model_File_Name_LOD = Model_File_Name.split('_')[0] # 設備LOD
    if Model_File_Name_LOD != '1' and Model_File_Name_LOD != '2' and Model_File_Name_LOD != '3':
        return jsonify({"error" : "ModelLOD is not allowed"}), status.HTTP_400_BAD_REQUEST # LOD只有 1, 2, 3
    if Model_File_Name_LOD != I_ModelLOD:
        return jsonify({"error" : "Model Name LOD error"})
    Model_File_Name_Format_Number = Model_File_Name.split('_')[1] # 設備格式代號，後面會有檔案格式
    print("Model_File_Name_Format_Number", Model_File_Name_Format_Number)
    Model_File_Name_Format_Number = Model_File_Name_Format_Number.split('.')[0] # 從檔案抓出來的Model_Number，因為會多後面的副檔名，所以要刪掉
    print("Model_File_Name_Format_Number", Model_File_Name_Format_Number)
    print("I_ModelFormat", I_ModelFormat)
    print("Type of ModelFormat", type(I_ModelFormat))
    if Model_File_Format == 'obj' and Model_File_Name_Format_Number == '01' and I_ModelFormat == '1':
        print("01")
    elif Model_File_Format == 'OBJ' and Model_File_Name_Format_Number == '01' and I_ModelFormat == '1':
        print("01")
    elif Model_File_Format == 'fbx' and Model_File_Name_Format_Number == '02' and I_ModelFormat == '2':
        print("02")
    elif Model_File_Format == 'gltf' and Model_File_Name_Format_Number == '03' and I_ModelFormat == '3':
        print("03")
    elif Model_File_Format == 'dae' and Model_File_Name_Format_Number == '04' and I_ModelFormat == '4':
        print("04")
    elif Model_File_Format == 'zip': #== I_ModelFormat:
        print("05")
    else:
        return jsonify({"error" : "格式代號與檔案命名規則不符合"}), status.HTTP_400_BAD_REQUEST
    i = 0
    # 檔案路徑
    File_Dir = os.path.join("/home/rt/Model_Library/"+ S_ModelCategory + "/" + S_ManufacturerName + \
        "/" + S_ModelName + "/" + S_ModelNumber)
    if not os.path.exists(File_Dir): # 檔案路徑是否存在
        os.makedirs(File_Dir)
    print("File dir", File_Dir)
    print("type of file dir", type(File_Dir))
    sql_update1 = ("UPDATE Model_Info SET S_ModelFilePath = %s WHERE S_ModelID = %s")# update model file path
    val_update1 = (File_Dir, S_ModelID)
    cursor.execute(sql_update1, val_update1)
    db.commit()
    File_Name_Check = Model_File_Name_LOD + "_" + Model_File_Name_Format_Number
    print("File_Name_Check : ", File_Name_Check)
    if Model_File_Name != File_Name_Check:
        return jsonify({"error":"File Name is not allowed"}), status.HTTP_400_BAD_REQUEST
    print("是否覆蓋的參數：", S_ModelCover)
    # 檔案上傳處理以及資料進入資料庫
    if S_ModelCover == None: # 裡面沒有檔案
        print("check file exist : ",os.path.isfile(File_Dir + "/" + File_Name_Check + "_" + str(i) + "." + Model_File_Format) )
        if os.path.isfile(File_Dir + "/" + File_Name_Check + "_" + str(i) + "." + Model_File_Format) is True: #確認檔案是否存在
            db.close()
            return jsonify({"S_ModelCover" : "Do you want to Cover"})
        else:
            S_FileName = str(File_Name_Check)
            save_file_time_start = time.time()
            Model_File.save(os.path.join(File_Dir, File_Name_Check + "_" + str(i) + "." + Model_File_Format))
            save_file_time_end = time.time()
            print("save file time :", save_file_time_end - save_file_time_start)
            sql_insert = ("INSERT INTO Model_File_Info(S_ModelID, S_FileName, I_ModelLOD, I_ModelFormat, I_Downloads, I_Version, I_Likes, D_UploadTime) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)")
            val_insert = (S_ModelID, S_FileName, I_ModelLOD, I_ModelFormat, 0, str(i), 0, dt_string)
            # sql_update = ("UPDATE Model_File_Info SET S_FileName = %s, I_ModelLOD = %s, I_ModelFormat = %s, S_UploadTime = %s WHERE S_ModelID = %s")
            # val_update = (S_FileName, I_ModelLOD, I_ModelFormat, dt_string, S_ModelID)
            cursor.execute(sql_insert, val_insert)
            db.commit()
            db.close()
            return jsonify({"Upload":"Success"}), status.HTTP_200_OK
    else:
        print("S_ModelCover : ", S_ModelCover)
        print("S_ModelCover Type : ", type(S_ModelCover))
        if S_ModelCover == '1' and S_ModelCover != "":
            S_FileName = str(File_Name_Check)
            save_file_time_start = time.time()
            Model_File.save(os.path.join(File_Dir, File_Name_Check + "_" + str(i) + "." + Model_File_Format))
            save_file_time_end = time.time()
            print("save file time :", save_file_time_end - save_file_time_start)
            sql_insert = ("INSERT INTO Model_File_Info(S_ModelID, S_FileName, I_ModelLOD, I_ModelFormat, I_Downloads, I_Version, I_Likes, D_UploadTime) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)")
            val_insert = (S_ModelID, S_FileName, I_ModelLOD, I_ModelFormat, 0, str(i), 0, dt_string)
            # sql_update = ("UPDATE Model_File_Info SET S_FileName = %s, I_ModelLOD = %s, I_ModelFormat = %s, S_UploadTime = %s WHERE S_ModelID = %s")
            # val_update = (S_FileName, I_ModelLOD, I_ModelFormat, dt_string, S_ModelID)
            cursor.execute(sql_insert, val_insert)
            db.commit()
            db.close()
            return jsonify({"Upload":"Success"}), status.HTTP_200_OK
        elif S_ModelCover == '0' and S_ModelCover != "":
            for i in range(100):
                if os.path.isfile(File_Dir + "/" + File_Name_Check + "_" + str(i) + "." + Model_File_Format) is False:
                    save_file_time_start = time.time()
                    Model_File.save(os.path.join(File_Dir, File_Name_Check + "_" + str(i) + "." + Model_File_Format))
                    save_file_time_end = time.time()
                    print("save file time :", save_file_time_end - save_file_time_start)
                    S_FileName = str(File_Name_Check)
                    sql_insert = ("INSERT INTO Model_File_Info(S_ModelID, S_FileName, I_ModelLOD, I_ModelFormat, I_Version, I_Downloads, I_Likes, D_UploadTime) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)")
                    val_insert = (S_ModelID, S_FileName, I_ModelLOD, I_ModelFormat, i, 0, 0, dt_string)
                    cursor.execute(sql_insert, val_insert)
                    db.commit()
                    db.close()
                    return jsonify({"Upload":"Success"}), status.HTTP_200_OK
        else:
            return jsonify({"error" : "S_ModelCover not allow"}), status.HTTP_400_BAD_REQUEST
        