from mysql.connector import connect
import mysql.connector
from mysql.connector import Error
import Background_Changer

def Connect_to_Database():
    try:
        connection = mysql.connector.connect(host="10.277.160.98",
                                             user="Student",
                                             password="Jrti2022!",
                                             database="edesktopdb",
                                             port="3306"
                                             )
        return connection
    except Error as e:
        print(e)


def Add_SubTask(Task_Name, Sub_Name, Sub_DDate, Sub_Desc, Sub_Status):
    task_Sql = f"insert into sub_task (Name, Sub_Name, Sub_DDate, Sub_Desc, Sub_Status) values('{Task_Name}','{Sub_Name}', '{Sub_DDate}', '{Sub_Desc}', '{Sub_Status}')"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(task_Sql)
    connection.commit()
    cursor.close()
    return True


def Get_SubTask_Data():
    try:
        connection = mysql.connector.connect(host="10.277.160.98",
                                             user="Student",
                                             password="Jrti2022!",
                                             database="edesktopdb",
                                             port="3306"
                                             )
        connected = True
    except Error as e:
        print(e)

    task_Sql = f"select * from sub_task;"

    if connected:
        try:
            cursor = connection.cursor()
            cursor.execute(task_Sql)
            sInfo = cursor.fetchall()
            if len(sInfo) == 0:
                print("Nothing Found")
            else:
                print(sInfo)
                return sInfo

        except Error as e:
            print(e)
            return e


def Edit_Subs_FromTask(Task_Name):
    task_Sql = f"update sub_task set Name = '{Task_Name}'"
    connection = get_Connection()
    cursor = connection.cursor()
    cursor.execute(task_Sql)
    connection.commit()
    cursor.close()


def Delete_Subs_FromTask(Delete):
    task_Sql = f"delete from sub_task where Name = '{Delete}'"
    connection = get_Connection()
    cursor = connection.cursor()
    cursor.execute(task_Sql)
    connection.commit()
    cursor.close()


def Delete_Sub_Task(Delete):
    task_Sql = f"delete from sub_task where Sub_Name = '{Delete}'"
    connection = get_Connection()
    cursor = connection.cursor()
    cursor.execute(task_Sql)
    connection.commit()
    cursor.close()


def Get_SubTasks(Task_Name):
    task_Sql = f"select Sub_Name,Sub_DDate,Sub_Status from sub_task where Name = '{Task_Name}';"
    connection = get_Connection()
    cursor = connection.cursor()
    try:
        cursor.execute(task_Sql)
        task_List = cursor.fetchall()
        cursor.close()
        return task_List

    except Error as e:
        print(e)


###################################
# Tasks
###################################
def Add_Task(Task_Name, Description, Status, Due_Date, Start_Date):
    task_Sql = f"insert into task (Name,Description,Status,Due_Date, Start_Date) values('{Task_Name}', '{Description}', '{Status}', '{Due_Date}', '{Start_Date}')"
    connection = get_Connection()
    cursor = connection.cursor()
    cursor.execute(task_Sql)
    connection.commit()
    cursor.close()
    return True


def Delete_Task(Delete):
    task_Sql = f"delete from task where Name = '{Delete}'"
    connection = get_Connection()
    cursor = connection.cursor()
    cursor.execute(task_Sql)
    connection.commit()
    cursor.close()


def Get_Task_Desc(Task_Name):
    task_Sql = f"select Description from task where Name = '{Task_Name}';"
    connection = get_Connection()
    cursor = connection.cursor()
    try:
        cursor.execute(task_Sql)
        task_List = cursor.fetchall()
        cursor.close()
        return task_List

    except Error as e:
        print(e)


def GetTask_Active():
    task_Sql = f"select Name,Due_Date,Status from task where Status != 'Completed';"
    connection = get_Connection()
    cursor = connection.cursor()
    try:
        cursor.execute(task_Sql)
        task_List = cursor.fetchall()
        cursor.close()
        return task_List

    except Error as e:
        print(e)


def GetTask_Completed():
    task_Sql = f"select Name,Due_Date,Status from task where Status = 'Completed';"
    connection = get_Connection()
    cursor = connection.cursor()
    try:
        cursor.execute(task_Sql)
        task_List = cursor.fetchall()
        cursor.close()
        return task_List

    except Error as e:
        print(e)


def GetTask_Waiting():
    task_Sql = f"select Name,Due_Date,Status from task where Status = 'Waiting on';"
    connection = get_Connection()
    cursor = connection.cursor()
    try:
        cursor.execute(task_Sql)
        task_List = cursor.fetchall()
        cursor.close()
        return task_List

    except Error as e:
        print(e)


def GetTask_Data():
    try:
        connection = mysql.connector.connect(host="10.277.160.98",
                                             user="Student",
                                             password="Jrti2022!",
                                             database="edesktopdb",
                                             port="3306"
                                             )
        connected = True
    except Error as e:
        print(e)

    task_Sql = f"select * from task;"

    if connected:
        try:
            cursor = connection.cursor()
            cursor.execute(task_Sql)
            sInfo = cursor.fetchall()
            if len(sInfo) == 0:
                print("Nothing Found")
            else:
                print(sInfo)
                return sInfo

        except Error as e:
            print(e)
            return e


def get_Connection():
    pass


def Edit_Task(tName, Task_Name, dDate, Task_DDate, status, Task_Status):
    task_Sql = f"update task set Name='{Task_Name}', Due_Date='{Task_DDate}', Status='{Task_Status}' where Name='{tName}' and Due_Date='{dDate}' and Status='{status}'"
    connection = get_Connection()
    cursor = connection.cursor()
    cursor.execute(task_Sql)
    connection.commit()
    cursor.close()
