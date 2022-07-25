import datetime, time, keyboard, json, pymysql, os, re, math, datetime, requests, configparser
from flask import Flask, request, redirect, url_for, jsonify, request, render_template, send_from_directory
from flask_api import status
from werkzeug.utils import secure_filename
import pandas as pd
import uuid

path = os.path.abspath('.')
cfgpath = path.split('python_code')[0] + 'python_code/config.ini'

config = configparser.ConfigParser()
config.read(cfgpath)

def query(*info):
    count = 0
    index = []
    sql_key = []
    for i in range(len(info)): # 判斷有幾個不是None
        if info[i] != None:
            index.append(i)
            if i == 0:
                sql_key.append("S_ModelID")
            elif i == 1:
                sql_key.append("S_ModelCategory")
            elif i == 2:
                sql_key.append("S_ManufacturerName")
            elif i == 3:
                sql_key.append("S_Location")
            elif i == 4:
                sql_key.append("S_ModelSubCategory")
            elif i ==5:
                sql_key.append("I_ModelFormat")
            count = count + 1
        elif count == 6:
            break
    return_to = number_to_strings(count, info, index, sql_key)
    return jsonify(return_to), status.HTTP_200_OK

def zero():
    # connect to database
    db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    cursor = db.cursor()
    sql_find_Model_Info = "SELECT * from Model_Info"
    cursor.execute(sql_find_Model_Info)
    data = cursor.fetchall()
    json_data = []
    for row in data:
        result_data = {}
        result_data["S_ModelID"] = row[1]
        result_data["S_ManufacturerAccountID"] = row[2] # 後來新增
        result_data["S_ManufacturerName"] = row[4]
        result_data["S_ModelName"] = row[5]
        result_data["B_ModelImage"] = row[12]
        json_data.append(result_data)
    db.close()
    return json_data

def one(info, index, sql_key):
    db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    cursor = db.cursor()
    if sql_key[0] == "S_ModelID": # 跳到次頁
        sql_find = "SELECT * from Model_Info WHERE " + sql_key[0] + "='%s'"%(info[index[0]])
        cursor.execute(sql_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data1 = {}
            result_data_File_Info = {}
            result_data1["S_ModelID"] = row[1]
            result_data1["S_ManufacturerAccountID"] = row[2]
            result_data1["S_ModelCategory"] = row[3]
            result_data1["S_ManufacturerName"] = row[4]
            result_data1["S_ModelName"] = row[5]
            result_data1["S_ModelNumber"] = row[6]
            result_data1["S_ModelSubCategory"] = row[7]
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
            data_Model_File_list4 = [] # ModelVersion
            data_Model_File_list5 = [] # ModelDownloads
            for row1 in data_Model_File_Info: # Model_FileName, Model_Format, Model_LOD要回傳list
                if row1[2] != None:
                    data_Model_File_list1.append(row1[2])
                    result_data_File_Info["I_ModelFormat"] = data_Model_File_list1
                if row1[3] != None:
                    data_Model_File_list2.append(row1[3])
                    result_data_File_Info["I_ModelLOD"] = data_Model_File_list2
                result_data1["I_Likes"] = row1[4]
                if row1[5] != None:
                    result_data1["I_ModelUnit"] = row1[5]
                if row1[6] != None:
                    data_Model_File_list5.append(row1[6])
                    result_data_File_Info["I_Downloads"] = data_Model_File_list5
                if row1[7] != None:
                    data_Model_File_list3.append(row1[7])
                    result_data_File_Info["S_FileName"] = data_Model_File_list3
                if row1[8] != None:
                    data_Model_File_list4.append(row1[8])
                    result_data_File_Info["I_Version"] = data_Model_File_list4
                result_data1["File_Info"] = result_data_File_Info
                
            json_data.append(result_data1)
        db.close()
        return json_data
    elif sql_key[0] == "I_ModelFormat":
        sql_find = "SELECT * from Model_Info, Model_File_Info WHERE Model_File_Info.I_ModelFormat = '%s' and Model_File_Info.S_ModelID = Model_Info.S_ModelID"%(info[index[0]])
        cursor.execute(sql_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data1 = {}
            result_data1["S_ModelID"] = row[1]
            result_data1["S_ManufacturerAccountID"] = row[2]
            result_data1["S_ManufacturerName"] = row[4]
            result_data1["S_ModelName"] = row[5]
            result_data1["B_ModelImage"] = row[12]
            json_data.append(result_data1)
        db.close()
        return json_data
    elif sql_key[0] == "S_ModelCategory": # 若參數是Category，需要多回傳SubCategory內容
        sql_find = "SELECT * from Model_Info WHERE " + sql_key[0] + "='%s'"%(info[index[0]])
        cursor.execute(sql_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data1 = {}
            result_data1["S_ModelID"] = row[1]
            result_data1["S_ManufacturerAccountID"] = row[2]
            result_data1["S_ManufacturerName"] = row[4]
            result_data1["S_ModelName"] = row[5]
            result_data1["B_ModelImage"] = row[12]
            json_data.append(result_data1)
        sql_find_subcategory = ("SELECT DISTINCT S_ModelSubCategory from Model_Info WHERE S_ModelCategory = '%s'")%(info[index[0]]) # DISTINCT會直接將重複的值過濾掉
        cursor.execute(sql_find_subcategory)
        data_subcategory = cursor.fetchall()
        subcategory_list = []
        for row1 in data_subcategory:
            result_subcategory = {}
            if row1[0] != None:
                subcategory_list.append(row1[0])
        result_subcategory["S_ModelSubCategory"] = subcategory_list
        json_data.append(result_subcategory)
        db.close()
        return json_data
    else:
        sql_find = "SELECT * from Model_Info WHERE " + sql_key[0] + "='%s'"%(info[index[0]])
        cursor.execute(sql_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data1 = {}
            result_data1["S_ModelID"] = row[1]
            result_data1["S_ManufacturerAccountID"] = row[2]
            result_data1["S_ManufacturerName"] = row[4]
            result_data1["S_ModelName"] = row[5]
            result_data1["B_ModelImage"] = row[12]
            json_data.append(result_data1)
        db.close()
        return json_data

def two(info, index, sql_key):
    db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    cursor = db.cursor()
    if index[0] == 1 and index[1] == 5: # index = 4 代表filter參數有I_ModelFormat
        sql_find = "SELECT * from Model_Info, Model_File_Info WHERE Model_File_Info.I_ModelFormat = %s and Model_File_Info.S_ModelID = Model_Info.S_ModelID and Model_Info." + sql_key[0] + "=%s"
        val_find = (info[index[1]], info[index[0]])
        cursor.execute(sql_find, val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data2 = {}
            result_data2["S_ModelID"] = row[1]
            result_data2["S_ManufacturerAccountID"] = row[2]
            result_data2["S_ManufacturerName"] = row[4]
            result_data2["S_ModelName"] = row[5]
            result_data2["B_ModelImage"] = row[12]
            json_data.append(result_data2)
        sql_find_subcategory = ("SELECT DISTINCT S_ModelSubCategory from Model_Info WHERE S_ModelCategory = '%s'")%(info[index[0]]) # DISTINCT會直接將重複的值過濾掉
        cursor.execute(sql_find_subcategory)
        data_subcategory = cursor.fetchall()
        subcategory_list2 = []
        result_subcategory2 = {}
        for row1 in data_subcategory:
            if row1[0] != None:
                subcategory_list2.append(row1[0])
        result_subcategory2["S_ModelSubCategory"] = subcategory_list2
        json_data.append(result_subcategory2)
        db.close()
        return json_data
    elif index[0] == 1 and index[1] == 4:
        sql_find = "SELECT * from Model_Info WHERE " + sql_key[0] + "=%s and " + sql_key[1] + " = %s"
        val_find = (info[index[0]], info[index[1]])
        cursor.execute(sql_find, val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data2 = {}
            result_data2["S_ModelID"] = row[1]
            result_data2["S_ManufacturerAccountID"] = row[2]
            result_data2["S_ManufacturerName"] = row[4]
            result_data2["S_ModelName"] = row[5]
            result_data2["B_ModelImage"] = row[12]
            json_data.append(result_data2)
        db.close()
        return json_data
    elif index[0] == 1:
        sql_find = "SELECT * from Model_Info WHERE " + sql_key[0] + "=%s and " + sql_key[1] + "=%s"
        val_find = (info[index[0]], info[index[1]])
        cursor.execute(sql_find,val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data2 = {}
            result_data2["S_ModelID"] = row[1]
            result_data2["S_ManufacturerAccountID"] = row[2]
            result_data2["S_ManufacturerName"] = row[4]
            result_data2["S_ModelName"] = row[5]
            result_data2["B_ModelImage"] = row[12]
            json_data.append(result_data2)
        sql_find_subcategory = ("SELECT DISTINCT S_ModelSubCategory from Model_Info WHERE S_ModelCategory = %s and " + sql_key[1] + "=%s") # DISTINCT會直接將重複的值過濾掉
        val_find_subcategory = (info[index[0]], info[index[1]])
        cursor.execute(sql_find_subcategory, val_find_subcategory)
        data_subcategory = cursor.fetchall()
        result_subcategory2 = {}
        subcategory_list2 = []
        for row1 in data_subcategory:
            if row1[0] != None:
                subcategory_list2.append(row1[0])
        result_subcategory2["S_ModelSubCategory"] = subcategory_list2
        json_data.append(result_subcategory2)
        db.close()
        return json_data
    elif index[1] == 5:
        sql_find = "SELECT * from Model_Info, Model_File_Info WHERE Model_File_Info.I_ModelFormat = %s and Model_File_Info.S_ModelID = Model_Info.S_ModelID and Model_Info." + sql_key[0] + "=%s"
        val_find = (info[index[1]], info[index[0]])
        cursor.execute(sql_find, val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data2 = {}
            result_data2["S_ModelID"] = row[1]
            result_data2["S_ManufacturerAccountID"] = row[2]
            result_data2["S_ManufacturerName"] = row[4]
            result_data2["S_ModelName"] = row[5]
            result_data2["B_ModelImage"] = row[12]
            json_data.append(result_data2)
        sql_find_subcategory = ("SELECT DISTINCT S_ModelSubCategory from Model_Info WHERE S_ModelCategory = '%s'")%(info[index[0]]) # DISTINCT會直接將重複的值過濾掉
        cursor.execute(sql_find_subcategory)
        data_subcategory = cursor.fetchall()
        subcategory_list2 = []
        result_subcategory2 = {}
        for row1 in data_subcategory:
            if row1[0] != None:
                subcategory_list2.append(row1[0])
        result_subcategory2["S_ModelSubCategory"] = subcategory_list2
        json_data.append(result_subcategory2)
        db.close()
        return json_data
    else:
        sql_find = "SELECT * from Model_Info WHERE " + sql_key[0] + "=%s and " + sql_key[1] + "=%s"
        val_find = (info[index[0]], info[index[1]])
        cursor.execute(sql_find, val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data2 = {}
            result_data2["S_ModelID"] = row[1]
            result_data2["S_ManufacturerAccountID"] = row[2]
            result_data2["S_ManufacturerName"] = row[4]
            result_data2["S_ModelName"] = row[5]
            result_data2["B_ModelImage"] = row[12]
            json_data.append(result_data2)
        db.close()
        return json_data

def three(info, index, sql_key):
    db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    cursor = db.cursor()
    if index[0] == 1 and index[2] == 5 and index[1] == 4: # 6 --> I_ModelFormat, 5 --> S_ModelSubCategory
        sql_find = "SELECT * from Model_Info, Model_File_Info WHERE Model_File_Info.S_ModelID = Model_Info.S_ModelID and Model_File_Info.I_ModelFormat = %s and Model_Info." + sql_key[0] + "=%s and Model_Info." + sql_key[1] + "=%s"
        val_find = (info[index[2]], info[index[0]], info[index[1]])
        cursor.execute(sql_find, val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data3 = {}
            result_data3["S_ModelID"] = row[1]
            result_data3["S_ManufacturerAccountID"] = row[2]
            result_data3["S_ManufacturerName"] = row[4]
            result_data3["S_ModelName"] = row[5]
            result_data3["B_ModelImage"] = row[12]
            json_data.append(result_data3)
        db.close()
        return json_data
    elif index[0] == 1  and index[2] == 5:
        sql_find = "SELECT * from Model_Info, Model_File_Info WHERE Model_File_Info.S_ModelID = Model_Info.S_ModelID and Model_File_Info.I_ModelFormat = %s and Model_Info." + sql_key[0] + "=%s and Model_Info." + sql_key[1] + "=%s"
        val_find = (info[index[2]], info[index[0]], info[index[1]])
        cursor.execute(sql_find, val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data3 = {}
            result_data3["S_ModelID"] = row[1]
            result_data3["S_ManufacturerAccountID"] = row[2]
            result_data3["S_ManufacturerName"] = row[4]
            result_data3["S_ModelName"] = row[5]
            result_data3["B_ModelImage"] = row[12]
            json_data.append(result_data3)
        sql_find_subcategory = ("SELECT DISTINCT S_ModelSubCategory from Model_Info WHERE S_ModelCategory = %s and " + sql_key[1] + "=%s") # DISTINCT會直接將重複的值過濾掉
        val_find_subcategory = (info[index[0]], info[index[1]])
        cursor.execute(sql_find_subcategory, val_find_subcategory)
        data_subcategory = cursor.fetchall()
        result_subcategory3 = {}
        subcategory_list3 = []
        for row1 in data_subcategory:
            if row1[0] != None:
                subcategory_list3.append(row1[0])
        result_subcategory3["S_ModelSubCategory"] = subcategory_list3
        json_data.append(result_subcategory3)
        db.close()
        return json_data
    elif index[0] == 1 and (index[1] == 4 or index[2] == 4):
        sql_find = "SELECT * from Model_Info WHERE " + sql_key[0] + "=%s and " + sql_key[1] + "=%s and " + sql_key[2] + "=%s"
        val_find = (info[index[0]], info[index[1]], info[index[2]])
        cursor.execute(sql_find, val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data3 = {}
            result_data3["S_ModelID"] = row[1]
            result_data3["S_ManufacturerAccountID"] = row[2]
            result_data3["S_ManufacturerName"] = row[4]
            result_data3["S_ModelName"] = row[5]
            result_data3["B_ModelImage"] = row[12]
            json_data.append(result_data3)
        db.close()
        return json_data
    elif index[2] == 5:
        sql_find = "SELECT * from Model_Info, Model_File_Info WHERE Model_File_Info.S_ModelID = Model_Info.S_ModelID and Model_File_Info.I_ModelFormat = %s and Model_Info." + sql_key[0] + "=%s and Model_Info." + sql_key[1] + "=%s"
        val_find = (info[index[2]], info[index[0]], info[index[1]])
        cursor.execute(sql_find, val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data3 = {}
            result_data3["S_ModelID"] = row[1]
            result_data3["S_ManufacturerAccountID"] = row[2]
            result_data3["S_ManufacturerName"] = row[4]
            result_data3["S_ModelName"] = row[5]
            result_data3["B_ModelImage"] = row[12]
            sql_ModelCategory = row[3]
            json_data.append(result_data3)
        # sql_find_subcategory = ("SELECT DISTINCT S_ModelSubCategory from Model_Info WHERE S_ModelCategory = %s and " + sql_key[0] + "=%s and " +sql_key[1] + "=%s") # DISTINCT會直接將重複的值過濾掉
        # val_find_subcategory = (sql_ModelCategory, info[index[0]], info[index[1]])
        # cursor.execute(sql_find_subcategory, val_find_subcategory)
        # data_subcategory = cursor.fetchall()
        # result_subcategory3 = {}
        # subcategory_list3 = []
        # for row1 in data_subcategory:
        #     if row1[0] != None:
        #         subcategory_list3.append(row1[0])
        # result_subcategory3["S_ModelSubCategory"] = subcategory_list3
        # json_data.append(result_subcategory3)
        return json_data
    elif index[0] == 1:
        sql_find = "SELECT * from Model_Info WHERE " + sql_key[0] + "=%s and " + sql_key[1] + "=%s and " + sql_key[2] + "=%s"
        val_find = (info[index[0]], info[index[1]], info[index[2]])
        cursor.execute(sql_find, val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data3 = {}
            result_data3["S_ModelID"] = row[1]
            result_data3["S_ManufacturerAccountID"] = row[2]
            result_data3["S_ManufacturerName"] = row[4]
            result_data3["S_ModelName"] = row[5]
            result_data3["B_ModelImage"] = row[12]
            json_data.append(result_data3)
        sql_find_subcategory = ("SELECT DISTINCT S_ModelSubCategory from Model_Info WHERE S_ModelCategory = %s and " + sql_key[1] + "=%s") # DISTINCT會直接將重複的值過濾掉
        val_find_subcategory = (info[index[0]], info[index[1]])
        cursor.execute(sql_find_subcategory, val_find_subcategory)
        data_subcategory = cursor.fetchall()
        result_subcategory3 = {}
        subcategory_list3 = []
        for row1 in data_subcategory:
            if row1[0] != None:
                subcategory_list3.append(row1[0])
        result_subcategory3["S_ModelSubCategory"] = subcategory_list3
        json_data.append(result_subcategory3)
        db.close()
        return json_data
    else:
        sql_find = "SELECT * from Model_Info WHERE " + sql_key[0] + "=%s and " + sql_key[1] + "=%s and " + sql_key[2] + "=%s"
        val_find = (info[index[0]], info[index[1]], info[index[2]])
        cursor.execute(sql_find, val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data3 = {}
            result_data3["S_ModelID"] = row[1]
            result_data3["S_ManufacturerAccountID"] = row[2]
            result_data3["S_ManufacturerName"] = row[4]
            result_data3["S_ModelName"] = row[5]
            result_data3["B_ModelImage"] = row[12]
            json_data.append(result_data3)
        db.close()
        return json_data

def four(info, index, sql_key):
    db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    cursor = db.cursor()
    if index[0] == 1 and index[2] == 4 and index[3] == 5:
        sql_find = "SELECT * from Model_Info, Model_File_Info WHERE Model_File_Info.S_ModelID = Model_Info.S_ModelID and Model_File_Info.I_ModelFormat = %s and Model_Info." + sql_key[0] + "=%s and Model_Info." + sql_key[1] + "=%s and Model_Info." + sql_key[2] + "=%s"
        val_find = (info[index[3]], info[index[0]], info[index[1]], info[index[2]])
        cursor.execute(sql_find,val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data4 = {}
            result_data4["S_ModelID"] = row[1]
            result_data4["S_ManufacturerAccountID"] = row[2]
            result_data4["S_ManufacturerName"] = row[4]
            result_data4["S_ModelName"] = row[5]
            result_data4["B_ModelImage"] = row[12]
            json_data.append(result_data4)
        db.close()
        return json_data
    elif index[0] == 1 and index[3] == 5:
        sql_find = "SELECT * from Model_Info, Model_File_Info WHERE Model_File_Info.S_ModelID = Model_Info.S_ModelID and Model_File_Info.I_ModelFormat = %s and Model_Info." + sql_key[0] + "=%s and Model_Info." + sql_key[1] + "=%s and Model_Info." + sql_key[2] + "=%s"
        val_find = (info[index[3]], info[index[0]], info[index[1]], info[index[2]])
        cursor.execute(sql_find,val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data4 = {}
            result_data4["S_ModelID"] = row[1]
            result_data4["S_ManufacturerAccountID"] = row[2]
            result_data4["S_ManufacturerName"] = row[4]
            result_data4["S_ModelName"] = row[5]
            result_data4["B_ModelImage"] = row[12]
            json_data.append(result_data4)
        sql_find_subcategory = ("SELECT DISTINCT S_ModelSubCategory from Model_Info WHERE S_ModelCategory = %s and " + sql_key[1] + "=%s and " + sql_key[2] + "=%s") # DISTINCT會直接將重複的值過濾掉
        val_find_subcategory = (info[index[0]], info[index[1]], info[index[2]])
        cursor.execute(sql_find_subcategory, val_find_subcategory)
        data_subcategory = cursor.fetchall()
        result_subcategory4 = {}
        subcategory_list4 = []
        for row1 in data_subcategory:
            if row1[0] != None:
                subcategory_list4.append(row1[0])
        result_subcategory4["S_ModelSubCategory"] = subcategory_list4
        json_data.append(result_subcategory4)
        db.close()
        return json_data
    elif index[3] == 5:
        sql_find = "SELECT * from Model_Info, Model_File_Info WHERE Model_File_Info.S_ModelID = Model_Info.S_ModelID and Model_File_Info.I_ModelFormat = %s and Model_Info." + sql_key[0] + "=%s and Model_Info." + sql_key[1] + "=%s and Model_Info." + sql_key[2] + "=%s"
        val_find = (info[index[3]], info[index[0]], info[index[1]], info[index[2]])
        cursor.execute(sql_find,val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data4 = {}
            result_data4["S_ModelID"] = row[1]
            result_data4["S_ManufacturerAccountID"] = row[2]
            result_data4["S_ManufacturerName"] = row[4]
            result_data4["S_ModelName"] = row[5]
            result_data4["B_ModelImage"] = row[12]
            sql_ModelCategory = row[3]
            json_data.append(result_data4)
        db.close()
        return json_data
    elif index[0] == 1 and index[3] == 4:
        sql_find = "SELECT * from Model_Info WHERE " + sql_key[0] + "=%s and " + sql_key[1] + "=%s and " + sql_key[2] + "=%s and " + sql_key[3] + "=%s"
        val_find = (info[index[0]], info[index[1]], info[index[2]], info[index[3]])
        cursor.execute(sql_find, val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data4 = {}
            result_data4["S_ModelID"] = row[1]
            result_data4["S_ManufacturerAccountID"] = row[2]
            result_data4["S_ManufacturerName"] = row[4]
            result_data4["S_ModelName"] = row[5]
            result_data4["B_ModelImage"] = row[12]
            json_data.append(result_data4)
        return json_data
    else:
        sql_find = "SELECT * from Model_Info WHERE " + sql_key[0] + "=%s and " + sql_key[1] + "=%s and " + sql_key[2] + "=%s and " + sql_key[3] + "=%s"
        val_find = (info[index[0]], info[index[1]], info[index[2]], info[index[3]])
        cursor.execute(sql_find, val_find)
        data = cursor.fetchall()
        json_data = []
        for row in data:
            result_data4 = {}
            result_data4["S_ModelID"] = row[1]
            result_data4["S_ManufacturerAccountID"] = row[2]
            result_data4["S_ManufacturerName"] = row[4]
            result_data4["S_ModelName"] = row[5]
            result_data4["B_ModelImage"] = row[12]
            json_data.append(result_data4)
        db.close()
        return json_data

def five(info, index, sql_key):
    db = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    cursor = db.cursor()
    sql_find = "SELECT * from Model_Info, Model_File_Info WHERE Model_File_Info.S_ModelID = Model_Info.S_ModelID and Model_File_Info.I_ModelFormat = %s and Model_Info." + sql_key[0] + "=%s and Model_Info." + sql_key[1] + "=%s and Model_Info." + sql_key[2] + "=%s and Model_Info." + sql_key[3] + "=%s"
    val_find = (info[index[4]], info[index[0]], info[index[1]], info[index[2]], info[index[3]])
    cursor.execute(sql_find, val_find)
    data = cursor.fetchall()
    json_data = []
    for row in data:
        result_data5 = {}
        result_data5["S_ModelID"] = row[1]
        result_data5["S_ManufacturerAccountID"] = row[2]
        result_data5["S_ManufacturerName"] = row[4]
        result_data5["S_ModelName"] = row[5]
        result_data5["B_ModelImage"] = row[12]
        json_data.append(result_data5)
    db.close()
    return json_data

def number_to_strings(argument, info, index, sql_key):
    switcher={
    0: zero,
    1: lambda: one(info, index, sql_key),
    2: lambda: two(info, index, sql_key),
    3: lambda: three(info, index, sql_key),
    4: lambda: four(info, index, sql_key),
    5: lambda: five(info, index, sql_key)
    }
    func = switcher.get(argument)
    return func()