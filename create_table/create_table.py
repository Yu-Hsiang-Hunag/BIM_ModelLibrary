import pymysql, json, configparser, os ,datetime

def create_database():
    path = os.path.abspath('.')
    cfgpath = path.split('python_code')[0] + 'python_code/config.ini'
    config = configparser.ConfigParser()
    config.read(cfgpath)
    # connect to mysql , mysql = pymysql.connect("localhost","root","rt-dev-1234;","test" )
    mysql = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]))
    #mysql = pymysql.connect("localhost","root","rt-dev-1234;","test" )# 這行可行
    cursor = mysql.cursor()
    # Create Database
    cursor.execute('''CREATE DATABASE IF NOT EXISTS ModelLibrary;''')
    mysql.commit() #execute
    cursor.close() #close execute

    # connect to database (have database)
    mysql = pymysql.connect(host = config['MYSQL']["host"], user = config['MYSQL']["user"], password = config['MYSQL']["password"], port = int(config['MYSQL']["port"]), db = config['MYSQL']["database"])
    #mysql = pymysql.connect("localhost","root","rt-dev-1234;","test" )# 這行可行
    cursor = mysql.cursor()
    # Create Model Info
    sql = """CREATE TABLE IF NOT EXISTS `Model_Info`(
        I_Index INT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
        S_ModelID CHAR(100),
        S_ManufacturerAccountID VARCHAR(100),
        S_ModelCategory VARCHAR(500),
        S_ManufacturerName text, 
        S_ModelName text, 
        S_ModelNumber VARCHAR(100),
        S_ModelSubCategory VARCHAR(1000),
        S_WarrantyID VARCHAR(100),
        S_ModelSizeID VARCHAR(100),
        S_Location text,
        S_ModelDescription text,
        B_ModelImage text,
        S_ModelFilePath VARCHAR(300),
        S_ModelProductURL text,
        S_OtherProperties text,
        S_ModelStatus VARCHAR(10),
        Hashcode VARCHAR(300),
        Remark text
        )ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""
    cursor.execute(sql)
    mysql.commit()

    #Create FileInfo
    sql = """CREATE TABLE IF NOT EXISTS `Model_File_Info`(
        I_Index INT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
        S_ModelID text(100),
        I_ModelFormat int(10),
        I_ModelLOD int(10),
        I_Likes int(100), 
        I_ModelUnit int(10),
        I_Downloads int(10), 
        S_FileName text(100),
        I_Version int(100),
        D_UploadTime VARCHAR(50),
        D_ModelStatus int(10),
        S_ModelStatus VARCHAR(10000),
        Hashcode VARCHAR(200),
        Remark text
        )ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""
    cursor.execute(sql)
    mysql.commit()

    # Create Manufacturer Info
    sql = """CREATE TABLE IF NOT EXISTS `Manufacturer_Manager`(
        I_Index INT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
        S_ManufacturerAccountID VARCHAR(100),
        S_ManufacturerName VARCHAR(100),
        B_ManufacturerLogo LongBlob,
        S_ManufacturerLocation text,
        S_ManufacturerContact text,
        S_ManufacturerDescription text,
        Hashcode VARCHAR(200),
        D_TimestampstatusChange text,
        S_Manufacturerstatus VARCHAR(20),
        Remark text
        )ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""
    cursor.execute(sql)
    mysql.commit()


    # Create Model_Warranty
    sql = """CREATE TABLE IF NOT EXISTS `Model_Warranty`(
        I_Index INT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
        S_WarrantyID VARCHAR(100),
        D_WarrantyStart VARCHAR(300),
        D_WarrantyDuration VARCHAR(100),
        S_WarrantyDescription text,
        Hashcode VARCHAR(100),
        Remark text
        )ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""
    cursor.execute(sql)
    mysql.commit()


    # Create Model_Size
    sql = """CREATE TABLE IF NOT EXISTS `Model_Size`(
        I_Index INT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
        S_ModelSizeID VARCHAR(100),
        F_ModelHeight FLOAT,
        F_ModelLength FLOAT,
        F_ModelWidth FLOAT,
        S_ModelMaterial VARCHAR(200),
        Hashcode VARCHAR(100),
        Remark VARCHAR(100)
        )ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""
    cursor.execute(sql)
    mysql.commit()

    #disconnect database
    mysql.close()
