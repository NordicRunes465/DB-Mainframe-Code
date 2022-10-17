#Robert Ball
#9/17/21
#Version 1.0
#Process Grades
#This program is used to send interim grade reports to the teachers. Each teacher will get a spread sheet
#attachment with all their students' grades for the classes for that teacher

import pandas as pd
import PySimpleGUI as sg
import GradesForTeachers as gForT
import copy
import logging
import sglyDB as Jdb
import JrtiLogon as login



sg.LOOK_AND_FEEL_TABLE['JRTI'] = {'BACKGROUND': '#2E75B6',
                                        'TEXT': 'black',
                                        'INPUT': '#FFFFFF',
                                        'TEXT_INPUT': '#000000',
                                        'SCROLL': '#41719C',
                                        'BUTTON': ('black', '#41719C'),
                                        'PROGRESS': ('#003058', '#FFFFFF'),
                                        'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 1,
                                        }
sg.theme('JRTI')

'''
from openpyxl import Workbook
from base64 import urlsafe_b64encode
import os.path

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
'''


import workdays

logging.basicConfig(filename='GradeManagement.log', format='%(asctime)s - %(message)s', level=logging.INFO)

class schoolData():
    def __init__(self):
        self.attData = None
        self.db = Jdb.jrtiDB()

    def getSchoolName(self,schoolCode):
        Musslemen = "MUHS"
        Washington = "WAHS"
        Jefferson = "JEHS"
        Martinsburg = "MAHS"
        Springmills = "SMHS"
        BerkeleySprings = "BSHS"
        PawPaw = "PPHS"
        Hedgesville = "HEHS"
        HomeSchool = "HOME"
        Missing = "miss"

        if schoolCode == Musslemen:
            return "Musslemen"
        elif schoolCode == Washington:
            return "Washington"
        elif schoolCode == Jefferson:
            return "Jefferson"
        elif schoolCode == Martinsburg:
            return "Martinsburg"
        elif schoolCode == Springmills:
            return "Springmills"
        elif schoolCode == BerkeleySprings:
            return "Berkeley Springs"
        elif schoolCode == PawPaw:
            return "Paw Paw"
        elif schoolCode == Hedgesville:
            return "Hedgesville"
        elif schoolCode == HomeSchool:
            return "Home Schooled"
        elif schoolCode == Missing:
            return "Missing"
        else:
            return "Faculty"

    def loadAttData(self):
        fLayout =  [[sg.In() ,sg.FileBrowse(file_types=(("CSV Files", "*.csv"),),key='-IN-')],
                    [sg.Button("Submit", key="Submit")]]
        fileWindow = sg.Window("My File Browser",fLayout, size = (600, 150))
        while True:
            event, values = fileWindow.read()
            if event == sg.WINDOW_CLOSED or event == "Exit":
                break
            elif event == "Submit":
                if values["-IN-"] == "":
                    sg.popup_ok("Please select a file before submitting")
                else:
                    attData = values["-IN-"]
                    data = pd.read_csv(attData, encoding = 'cp1252')
                    fileWindow.close()
                    return data

    def loadAttendanceDB(self,aData):
        window["abar"].update(0,visible=True)
        dataAmount = len(aData)
        increment = 100 / dataAmount
        total = 0.0
        for index, row in aData.iterrows():
            total += increment
            window["abar"].update(total)
            userId = row["Unique User ID"]
            date = row["Date"]
            firstName = row["First Name"]
            lastName = row["Last Name"]
            courseName = row["Course Name"]
            sectionName = row["Section Name"]
            sectionCode = row["Section Code"]
            status = row["Attendance"]
            comment = row["Comment"]
            if type(userId) == float:
                schoolCode = "miss"
            else:
                schoolCode = userId[:4]
                if schoolCode == "BEHS":
                    schoolCode = "BSHS"
                elif schoolCode == "HGHS":
                    schoolCode = "HEHS"
                elif schoolCode == "JESH":
                    schoolCode = "JEHS"
            schoolName = self.getSchoolName(schoolCode)
            results = self.db.loadAttendanceData(userId,date,firstName,
                                                 lastName,courseName,sectionName,sectionCode,status,
                                                 comment,schoolName)
        window["status"].update("")
        window["abar"].update(0,visible=False)
        sg.popup_ok("Attendance Data has been loaded!")
        return results

    def loadXrefTable(self,pCount,gradeData):
            gMaster = copy.deepcopy(gradeData)
            dataAmount = len(gMaster)
            print(f"Data amount is : {dataAmount}")
            increment = 20 / dataAmount
            window["status"].update("Loading Xref Table")
            sectionList = []
            for index, row in gMaster.iterrows():
                pCount += increment
                window["pBar"].update(pCount)
                courseName = row["Course Name"]
                sectionName = row["Section Name"]
                if sectionName not in sectionList:
                    sectionList.append(sectionName)
                    self.db.loadCourseTeachXref(sectionName,courseName)
            window["status"].update("")
            return pCount

    def loadAssignmentTable(self,gradeData,pCount):
            pCount = self.loadXrefTable(pCount,gradeData)
            AssignmentsOnly = ['Mkp 1', 'Mkp 2', 'Mkp 3', 'Mkp 4']
            gMaster = copy.deepcopy(gradeData)
            gList = gMaster.loc[
                (gMaster['Grading Period'].isin(AssignmentsOnly))]      # Gets rows if columns have specific data
            dataAmount = len(gList)
            print(f"Data amount is : {dataAmount}")
            total = 0
            increment = 20 // int(dataAmount)
            window['status'].update("Loading assignments")
            for index, row in gList.iterrows():
                pCount = pCount + increment
                window["pBar"].update(pCount)
                UniqueUserId = row["Unique User ID"]
                role = row["Role"]
                courseName = row["Course Name"]
                courseCode = row["Course Code"]
                sectionName = row["Section Name"]
                firstName = row["First Name"]
                lastName = row["Last Name"]
                mPeriod = row["Grading Period"]
                titles = row["Titles"]
                grades = row["Grades"]
                dueDates = row["Due Dates"]
                maxPoints = row["Max Points"]
                letterGrade = row["Letter Grades"],
                comments = row["Comments"]
                if role == 'Student':
                    self.db.loadAssignment(UniqueUserId,courseName,mPeriod,firstName,
                            lastName,role,courseCode,sectionName,titles,dueDates,maxPoints,
                            grades,letterGrade,comments)
                    total += 1
            return

    def loadStudentTable(self,gradeData):
        window["pBar"].update(0)
        total = 0.0
        totalsOnly = ['*Overall','*Mkp 1', '*Mkp 2', '*Mkp 3', '*Mkp 4']
        gMaster = copy.deepcopy(gradeData)
        gList = gMaster.loc[
            (gMaster['Titles'].isin(totalsOnly))]      # Gets rows if columns have specific data
        load = self.db.updateLastUpdateDate()
        dataAmount = len(gList)
        increment = 30 / dataAmount
        for index, row in gList.iterrows():
            total += increment
            window["pBar"].update(total)
            UniqueUserId = row["Unique User ID"]
            sEmail = row["Email"]
            schoolCode = UniqueUserId[:4]
            if schoolCode == "BEHS":
                schoolCode = "BSHS"
            elif schoolCode == "HGHS":
                schoolCode = "HEHS"
            elif schoolCode == "JESH":
                schoolCode = "JEHS"
            role = row["Role"]
            schoolName = self.getSchoolName(schoolCode)
            courseName = row["Course Name"]
            sectionName = row["Section Name"]
            sectionCode = row["Section Code"]
            firstName = row["First Name"]
            lastName = row["Last Name"]
            mPeriod = row["Titles"]
            grades = row["Grades"]
            if role == 'Student':
                if not schoolCode.isalpha():
                    schoolName = "Missing"
                self.db.loadStudentData(UniqueUserId,firstName,lastName,sEmail,schoolName,mPeriod,grades)
                self.db.loadClassGrades(UniqueUserId,courseName,sectionName,mPeriod,grades,firstName,lastName)
        return total

    def loadClassData(self,gradeData,pCount):
        overAll = ['*Overall']
        clMaster = copy.deepcopy(gradeData)
        OverOnly = clMaster.loc[
            (clMaster['Titles'].isin(overAll))]      # Gets rows if columns have specific data
        dataAmount = len(OverOnly)
        total = pCount
        increment = 30 / dataAmount
        for index, row in OverOnly.iterrows():
            total += increment
            window["pBar"].update(total)
            UniqueUserId = row["Unique User ID"]
            schoolCode = UniqueUserId[:4]
            if schoolCode == "BEHS":
                schoolCode = "BSHS"
            elif schoolCode == "HGHS":
                schoolCode = "HEHS"
            elif schoolCode == "JESH":
                schoolCode = "JEHS"
            role = row["Role"]
            courseName = row["Course Name"]
            section = row["Section Name"]
            markingPeriod = row["Titles"]
            schoolName = self.getSchoolName(schoolCode)
            firstName = row["First Name"]
            lastName = row["Last Name"]
            if role == 'Student' and markingPeriod == "*Overall":
                if not schoolCode.isalpha():
                    schoolName = "Missing"
                loaded = self.db.loadStudentClasses(UniqueUserId,firstName,lastName,courseName,schoolName,section)
        return total

    def refreshUserListDB(self,Teachers=False):
        if Teachers:
            userList = self.db.get_user_list(True)
            window["teachTable"].update(userList)
        else:
            userList = self.db.get_user_list()
            window["usertable"].update(userList)
        return userList

    def studentSearch(self,pstring):
        self.pString = pstring
        nameList = self.db.studentSearch(self.pString)
        return nameList

    def countStudents(self):
        highSchoolList = self.db.getHighSchooList()
        highSchoolCount = {}
        for school in highSchoolList:
            schoolName = school[0]
            count, tCount = self.db.getSchoolCount(schoolName)
            highSchoolCount[schoolName] = (int(count))
        return highSchoolCount, tCount

    def addUser(self,userID,passwd,security,fname,lname,isTeacher,subject):
        self.userId = userID
        self.passWd = passwd
        self.secLevel = security
        self.fName = fname
        self.lName = lname
        self.subject = subject
        if isTeacher:
            self.teacher = "Y"
        else:
            self.teacher = "N"

        success = self.db.add_user(self.fName,self.lName,self.userId,self.secLevel,self.passWd,self.teacher,self.subject)

        if success: return True
        else: return False

    def deleteUser(self,userid):
        self.userid = userid
        response = sg.popup_ok_cancel("Are you sure you want to delete this user?",grab_anywhere=True)
        if response.upper() == 'OK':
               self.db.remove_user(self.userid)
        else:
            sg.popup_ok("Delete User Id was cancelled!")



    def loadMarkingPeriod(self,gradeData):
        mpList = []
        for index, row in gradeData.iterrows():
            UniqueUserId = row["Unique User ID"]
            markingPeriod = row['Titles']
            if markingPeriod not in mpList:
                mpList.append(markingPeriod)
        return mpList


    def getStudentInfo(self,searchLastName,searchFirstName):
        studentList, stuDetail, aCount, lCount = self.db.getStudentDetails(searchFirstName,searchLastName)
        print(stuDetail)
        sUid = stuDetail[0][0]
        print(sUid)
        allDay = False
        sSchedule, sTeach = self.db.getTechProgramData(sUid)

        for tuple in sTeach:
            for sTuple in  sSchedule:
                if tuple[0] in sTuple[0]:
                    techProgram = tuple[1]
                    print(f"Found a match: {tuple[0]}  and {sTuple}")
                if 'KBall' in sTuple[0]:
                    allDay = True

        sSingleGrades = self.db.getStuGrades(sUid)

        print(sSchedule)
        print(sTeach)
        return studentList, stuDetail, aCount,lCount,techProgram, allDay,sSingleGrades


    def findNoSchoolStudents(self,gradeData):
        studentList = []
        for index, row in gradeData.iterrows():
            UniqueUserId = row["Unique User ID"]
            schoolCode = UniqueUserId[:4]
            if schoolCode == "BEHS":
                schoolCode = "BSHS"
            elif schoolCode == "HGHS":
                schoolCode = "HEHS"
            elif schoolCode == "JESH":
                schoolCode = "JEHS"
            schoolName = self.getSchoolName(schoolCode)
            firstName = row["First Name"]
            lastName = row["Last Name"]
            role = row['Role']
            courseName = row['Course Name']
            markingPeriod = row['Titles']
            sectionName = row["Section Name"]
            grade = row['Grades']
            fgrade = float(grade)
            sgrade = str(grade)
            letterGrade = row["Letter Grades"]
            lgrade = str(letterGrade)
            if (role == 'Student') and (schoolName == "Faculty"):
                sItem = f"{firstName} {lastName} does not have a school code : {UniqueUserId}\n"
                studentList.append(sItem)
        if len(studentList) == 0:
            studentList.append("No Students with out a school")
        return studentList

    def missingGradeTeacher(self,gradeData,Teacher):
        courseList = []
        for index, row in gradeData.iterrows():
            UniqueUserId = row["Unique User ID"]
            schoolCode = UniqueUserId[:4]
            if schoolCode == "BEHS":
                schoolCode = "BSHS"
            elif schoolCode == "HGHS":
                schoolCode = "HEHS"
            elif schoolCode == "JESH":
                schoolCode = "JEHS"
            schoolName = self.getSchoolName(schoolCode)
            firstName = row["First Name"]
            lastName = row["Last Name"]
            role = row['Role']
            courseName = row['Course Name']
            markingPeriod = row['Titles']
            sectionName = row["Section Name"]
            grade = row['Grades']
            fgrade = float(grade)
            sgrade = str(grade)
            letterGrade = row["Letter Grades"]
            lgrade = str(letterGrade)
            if (role == 'Student') and (schoolName != "Faculty") and (Teacher.upper() in sectionName.upper()):
                if "OVERALL" in markingPeriod.upper():
                    if pd.isna(fgrade):
                        lItem = f"Grade Missing for {firstName} {lastName} in {courseName}\n"
                        courseList.append(lItem)

        return courseList

    def getStuAbsTot(self,StartDate = None,EndDate = None):
        wDays,stCount,abCount = self.db.getwkDaysandStuCount()
        fwDays = float(wDays)
        fstCount = float(stCount)
        fabCount = float(abCount)
        attendanceRate = 100 - round((fabCount/(fwDays * fstCount)),2)
        return wDays,stCount,abCount,str(attendanceRate)

    def getTeacherStats(self):
            sList,aList = self.db.getTeachStats()
            window["teachTable"].update(sList)
            print(sList)


    def schoolCountandTotal(self):
        highSchoolList = self.db.getHighSchooList()
        schoolGradeAverage = {}
        for school in highSchoolList:
            schoolName = school[0]
            schoolAvg,totalAvg = self.db.getSchoolAvgGrade(schoolName)
            schoolGradeAverage[schoolName] = round(float(schoolAvg),2)
        return schoolGradeAverage, totalAvg

    def getStuAbsDetail(self,stuId):
        self.stuId = stuId
        stADtlHeadings = ['Student ID','Date','First Name','Last Name','Course Name','Section Name','Attendance Status']
        stAdtlDataValues = [['','','','','','',''],['','','','','','','']]
        stADtlWidths = [10,10,12,12,30,30,15]

        StudentAtDetailLayout = [[sg.Text("Student Attendance Details",justification="center",font=("Arial",18))],
                              [sg.Table(values=stAdtlDataValues,headings=stADtlHeadings,col_widths=stADtlWidths,
                                        auto_size_columns=False, num_rows=15,justification='left',key="stAtDtl",
                                        enable_events=False,size=(900,200))],
                              [sg.Button("Quit",key="quit",enable_events=True), sg.Text("Absent: "),sg.Text("",key="totAbsent"),sg.Text("Excused: "),sg.Text("",key="totExcused"),
                                                    sg.Text("Late: "),sg.Text("",key='totLate')]]

        attDetail,aCount,eCount,tCount = self.db.getAttDetail(self.stuId)
        aWindow = sg.Window("Student Attendance Detail",layout=StudentAtDetailLayout,size=(1200,350),modal=True,
                            finalize=True,resizable=True)
        aWindow["stAtDtl"].update(attDetail)
        aWindow["totAbsent"].update(aCount[0])
        aWindow["totExcused"].update(eCount[0])
        aWindow["totLate"].update(tCount[0])
        while True:
            event, values = aWindow.read()
            if event == sg.WINDOW_CLOSED or event == "Exit":
                break
            elif event == "quit":
                aWindow.close()
                break


    def getSingleStuGrades(self,stuId):
        self.stuId = stuId
        stGradeHeadings = ['Student ID','First Name','Last Name','Course Name','Section Name','Mkp','Grade']
        stGradeDataValues = [['','','','','','',''],['','','','','','','']]
        stGradeWidths = [10,15,15,35,25,15,8]

        #fixme

        StudentGradeLayout = [[sg.Text("Student Current Grades",justification="center",font=("Arial",18))],
                              [sg.Table(values=stGradeDataValues,headings=stGradeHeadings,col_widths=stGradeWidths,
                                        auto_size_columns=False, num_rows=10,justification='left',key="stGrade",
                                        enable_events=False,size=(1100,250))],
                              [sg.Button("Quit",key="gradebutton",enable_events=True)]]

        studentGrades = self.db.getReportCard(self.stuId)
        gWindow = sg.Window("Student Grade List",layout=StudentGradeLayout,size=(1200,275),modal=True,
                            finalize=True,resizable=True)
        gWindow["stGrade"].update(studentGrades)
        usingWindow = True
        while usingWindow:
            event, values = gWindow.read()
            if event == sg.WINDOW_CLOSED or event == "Exit":
                break
            elif event == "gradebutton":
                gWindow.close()
                usingWindow = False

    def pullSchoolAbsences(self):
        schoolList = self.db.getAbsenceBySchool()
        return schoolList

#######################################
#
# This sets the security base on user Role
#
#######################################
    def setSecurity(self,role):
        self.role = role
        if role == "user":
            window["gradeTab"].update(disabled=True,visible=False)
            window["attendTab"].update(disabled=True,visible=False)
            window["schedTab"].update(disabled=False,visible=True)
            window["teachTab"].update(disabled=True,visible=False)
            window["uAdminTab"].update(disabled=True,visible=False)
            window["aload"].update(disabled=True,visible=False)
            window["afilemessage"].update(disabled=True,visible=False)
            window["-Load-"].update(disabled=True,visible=False)
            window["-FileMessage-"].update(disabled=True,visible=False)
            window["Grades"].update( visible=False)
        elif role == "Teacher":
            window["gradeTab"].update(disabled=False,visible=True)
            window["attendTab"].update(disabled=False,visible=True)
            window["schedTab"].update(disabled=False,visible=True)
            window["teachTab"].update(disabled=True,visible=False)
            window["uAdminTab"].update(disabled=True,visible=False)
            window["aload"].update(disabled=True,visible=False)
            window["afilemessage"].update(disabled=True,visible=False)
            window["-Load-"].update(disabled=True,visible=False)
            window["-FileMessage-"].update(disabled=True,visible=False)
            window["Grades"].update(visible = False)
        elif role == "Admin":
            window["gradeTab"].update(disabled=False,visible=True)
            window["attendTab"].update(disabled=False,visible=True)
            window["schedTab"].update(disabled=False,visible=True)
            window["teachTab"].update(disabled=False,visible=True)
            window["uAdminTab"].update(disabled=True,visible=False)
            window["aload"].update(disabled=False,visible=True)
            window["afilemessage"].update(visible=True)
            window["-Load-"].update(disabled=False,visible=True)
            window["-FileMessage-"].update(visible=True)
            window["Grades"].update(visible=True)
        elif role == "Ink":
            window["gradeTab"].update(disabled=False,visible=True)
            window["attendTab"].update(disabled=False,visible=True)
            window["schedTab"].update(disabled=False,visible=True)
            window["teachTab"].update(disabled=False,visible=True)
            window["uAdminTab"].update(disabled=False,visible=True)
            window["aload"].update(disabled=False,visible=True)
            window["afilemessage"].update(visible=True)
            window["-Load-"].update(disabled=False,visible=True)
            window["-FileMessage-"].update(visible=True)
            window["Grades"].update( visible=True)

#######################################
#
#This is the initial load, when the program starts
#
#######################################


    def initialLoadDb(self):
        window['status'].update("Counting Students...")
        studentCount, schoolCount = gradeObj.countStudents()
        window["tStudents"].update(schoolCount)
        window["MUHS"].update(studentCount["Musslemen"])
        window["WAHS"].update(studentCount["Washington"])
        window["JEHS"].update(studentCount["Jefferson"])
        window["MAHS"].update(studentCount["Martinsburg"])
        window["SMHS"].update(studentCount["Springmills"])
        window["BSHS"].update(studentCount["Berkeley Springs"])
        window["PPHS"].update(studentCount["Paw Paw"])
        window["HEHS"].update(studentCount["Hedgesville"])
        window["HOME"].update(studentCount["Home Schooled"])
        window['status'].update("Getting Grade Average by School")
        ################################################################################
        schoolAvg,totalAvg = gradeObj.schoolCountandTotal()
        window["MUHS-Avg"].update(round(schoolAvg["Musslemen"],2))
        window["WAHS-Avg"].update(round(schoolAvg["Washington"],2))
        window["JEHS-Avg"].update(round(schoolAvg["Jefferson"],2))
        window["MAHS-Avg"].update(round(schoolAvg["Martinsburg"],2))
        window["SMHS-Avg"].update(round(schoolAvg["Springmills"],2))
        window["BSHS-Avg"].update(round(schoolAvg["Berkeley Springs"],2))
        window["HEHS-Avg"].update(round(schoolAvg["Hedgesville"],2))
        window["PPHS-Avg"].update(round(schoolAvg["Paw Paw"],2))
        window["HOME-Avg"].update(round(schoolAvg["Home Schooled"],2))
        window["School-Avg"].update(round(totalAvg,2))
        ##################################################################################
        listOfFailingStudents = self.db.getFailingStudents('60.0')
        window['fail'].update(listOfFailingStudents)
        ###################################################################################
        ldate = self.db.getLastUpdateDate()
        window['updateDate'].update(ldate[0])
        ###################################################################################
        listStudentAbsent = self.db.getAbscenceData("Absent")
        window['absTable'].update(listStudentAbsent)
        listStudentLate = self.db.getAbscenceData("Late")
        window['lateTable'].update(listStudentLate)
        ###################################################################################
        schoolAbsList = gradeObj.pullSchoolAbsences()
        schoolList =[]
        for tuples in schoolAbsList:
            schoolList.append(list(tuples))

        for school in schoolList:
            if school[0] == "Berkeley Springs":
                window["berkeleySprings"].update((school[1]))
            elif school[0] == "Faculty":
                window["faculty"].update(school[1])
            elif school[0] == "Hedgesville":
                window["hedgesville"].update(school[1])
            elif school[0] == "Home Schooled":
                window["home"].update(school[1])
            elif school[0] == "Jefferson":
                window["jefferson"].update(school[1])
            elif school[0] == "Martinsburg":
                window["martinsburg"].update(school[1])
            elif school[0] == "Musslemen":
                window["musselman"].update(school[1])
            elif school[0] == "Paw Paw":
                window["PawPaw"].update(school[1])
            elif school[0] == "Springmills":
                window["springMills"].update(school[1])
            elif school[0] == "Washington":
                window["washington"].update(school[1])

#######################################
#
#   Main Code
#
#######################################

#Todo get teacher names into a Db
teacherList = ['Albright','Arntz','Bennett','Brown','Butcher','Christman','Cunningham','Eisenhart','Files','Gerda',
                'Harris','Heath', 'Jlockhart','KBall','lantz','LAYHEW','Morgan','Odom','Price','RBall','Rlockhart','SULLIVAN',
                'Ware','Zeger','Vanorsdale']

#Todo - Get Teacher emails into a Db
teacherEmail = {'ALBRIGHT' : 'kyle.albright@k12.wv.us','ARNTZ' : 'carntz@k12.wv.us','BENNETT' : 'wybennet@k12.wv.us',
                    'BROWN' : 'sjbrown@k12.wv.us','BUTCHER' : 'jlbutche@k12.wv.us','CHRISTMAN' : 'vchristm@k12.wv.us' ,
                    'CUNNINGHAM' : 'lauren.cunningham@k12.wv.us','EISENHART': 'paul.eisenhart@k12.wv.us',
                    'FILES' : 'afiles@k12.wv.us','GERDA' : 'dgerda@k12.wv.us', 'HARRIS' : 'steven.harris@k12.wv.us',
                    'JLOCKHART' : 'jlockhart@k12.wv.us','KBALL' : 'kenda.ball@k12.wv.us','LANTZ' : 'llantz@k12.wv.us',
                    'LAYHEW' : 'llayhew@k12.wv.us','MORGAN' : 'm.d.morgan@k12.wv.us','ODOM' :'rodom@k12.wv.us',
                    'PRICE' : 'kwprice@k12.wv.us','RBALL': 'Robert.w.ball@k12.wv.us','RLOCKHART' : 'rebecca.lockhart@k12.wv.us',
                    'SULLIVAN' : 'mrsulliv@k12.wv.us', 'WARE' : 'jeware@k12.wv.us', 'ZEGER' : 'bzeger@k12.wv.us',
                    'VANORSDALE' : 'jvanorsd@k12.wv.us','HEATH' : 'betsy.heath@k12.wv.us'}

#######################################
#
# Main Code
#
#######################################

# Set the JRTI Them,e

sg.LOOK_AND_FEEL_TABLE['JRTI'] = {'BACKGROUND': '#2E75B6',
                                        'TEXT': 'black',
                                        'INPUT': '#FFFFFF',
                                        'TEXT_INPUT': '#000000',
                                        'SCROLL': '#41719C',
                                        'BUTTON': ('white', '#345878'),
                                        'PROGRESS': ('#003058', '#FFFFFF'),
                                        'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 1,
                                        'TABLE':''}
sg.theme('JRTI')
nwidth = 11
cwidth = 4
gradesLoaded = False


stInfoDataValues = []
stInfoHeadings =['Class Name','Period']
stLookUpHeadings = ['First Name','Last Name', "Home School"]
stInfoDataValues = [['',''],['','']]
stLookupValues = [['','',''],['','','']]
dataColWidths = [35,40]
stInfoWidths = [26,25,25]


#######################################
#
#Teacher Tab Layouts
#
#######################################

teachHeadings = ['First Name','Last Name','Subject','Student Count','Avg Grade/Student','Total Assignments']
teachValues = [['','','','','',''],['','','','','','']]
teachwidths = [15,15,25,10,10,20]
teachTableLayout =[[sg.Table(values=teachValues,headings=teachHeadings,col_widths=teachwidths,auto_size_columns=True,
                             num_rows=20,justification='left',key="teachTable",enable_events=True,size=(800,25))]]
teacherLayout = [[sg.Frame("Teacher Data",teachTableLayout,size=(700,25))]]

#######################################
#
#Layout for Grade Dashboard Tab
#
#######################################
stFailHeadings = ['Student ID','First Name','Last Name','Subject','Section','Mkp','Grade']
stFailDataValues = [['','','','','','',''],['','','','','','','']]
stFailWidths = [10,12,12,30,20,10,10]

failListLayout = [[sg.Table(values=stFailDataValues,headings=stFailHeadings,key="fail",col_widths=stFailWidths,auto_size_columns=False,
                            num_rows=15,justification='left',enable_events=True)]]

noSchoolLayout = [[sg.Multiline("",size=(95,6),background_color="light grey",do_not_clear=True,key="noschool")]]
schoolFrameLayout = [[sg.Text('Berkeley Springs : ',justification=("left"),size = (12,1)),sg.Text("",key='BSHS')],
                    [sg.Text('Hedgesville : ',justification=("left"),size = (12,1)), sg.Text("",key='HEHS')],
                    [sg.Text('Jefferson : ', justification=("left"),size = (12,1)), sg.Text("", key ='JEHS')],
                    [sg.Text('Martinsburg : ', justification=("left"),size = (12,1)),sg.Text("",key= 'MAHS')],
                    [sg.Text('Musselman : ', justification=("left"),size = (12,1)), sg.Text("", key = 'MUHS')],
                    [sg.Text('Paw Paw : ', justification=("left"),size = (12,1)), sg.Text("",key='PPHS')],
                    [sg.Text('Spring Mills : ', justification=("left"),size = (12,1)),sg.Text("",key='SMHS')],
                     [sg.Text('Home : ', justification=("left"),size = (12,1)), sg.Text("",key = 'HOME')],
                     [sg.Text('Washington : ', justification=("left"),size = (12,1)), sg.Text("", key = 'WAHS')],
                     [sg.Text('Total Students : ', justification=("left"),size = (12,1)), sg.Text("",key = 'tStudents', relief = "sunken")]]

schoolAvgLayout = [[sg.Text('Berkeley Springs : ',justification=("left"),size = (12,1)),sg.Text("",key='BSHS-Avg')],
                    [sg.Text('Hedgesville : ',justification=("left"),size = (12,1)), sg.Text("",key='HEHS-Avg')],
                    [sg.Text('Jefferson : ', justification=("left"),size = (12,1)), sg.Text("", key ='JEHS-Avg')],
                    [sg.Text('Martinsburg : ', justification=("left"),size = (12,1)),sg.Text("",key= 'MAHS-Avg')],
                    [sg.Text('Musselman : ', justification=("left"),size = (12,1)), sg.Text("", key = 'MUHS-Avg')],
                    [sg.Text('Paw Paw : ', justification=("left"),size = (12,1)), sg.Text("",key='PPHS-Avg')],
                    [sg.Text('Spring Mills : ', justification=("left"),size = (12,1)),sg.Text("",key='SMHS-Avg')],
                     [sg.Text('Home : ', justification=("left"),size = (12,1)), sg.Text("",key = 'HOME-Avg')],
                     [sg.Text('Washington : ', justification=("left"),size = (12,1)), sg.Text("", key = 'WAHS-Avg')],
                     [sg.Text('Avg Grade all Schools : ', justification=("left"),size = (12,1)), sg.Text("",key = 'School-Avg', relief = "sunken")]]

layout = [[sg.Text("JRTI Schoology Dashboard",font=("Arial",35), justification="left", relief = "flat"),
           sg.Stretch(),sg.Image(filename=".\JRTISD-Logo-s.png",size=(250,100))],
          [sg.Text("No File has been loaded.  Please load a file before proceeding",key="-FileMessage-"), sg.Button("Load Grades",enable_events=True,key="-Load-")],
          [sg.Checkbox("Hide failing student list",enable_events=True,key="hide"),sg.Text("Last Update: "),
            sg.Text("",key="updateDate",font=("Arial",16), size=(10,1))],
          [sg.HorizontalSeparator()],
          [sg.Frame("Students by High School",schoolFrameLayout),
            sg.Frame("Average Grade by School", schoolAvgLayout),
            sg.Frame("Failing Students",failListLayout,key='failframe')],
          [sg.ProgressBar(100,orientation='horizontal',size=(1000,10), style='default',bar_color=("blue","white"),key='pBar')],
          [sg.Button("No School Code",enable_events=True,key="noschool"),sg.Button("Teacher Interims",key= "tinterim"),sg.Button("Student Interims", key="sinterim"),
           sg.Combo(["Marking Period 1","Marking Period 2","Marking Period 3","Marking Period 4"],readonly = True)],
          [sg.StatusBar("",key="status",size = (1000,1))]]

#######################################
#
#Attendance Dashboard Tab  Layouts
#
#######################################




#######################################
#
#Student Info Tab  Layouts
#
#######################################
studentLookupLayout =[[sg.Table(values = stLookupValues, headings=stLookUpHeadings, key="slook",
                                col_widths=stInfoWidths, auto_size_columns=False, num_rows=10,pad=((0,45),(0,0)) ,justification='left', enable_events=True)],
                      [sg.Text("Please Enter last name"), sg.InputText("",size=(20,1),enable_events=True,key="sSearch")],
                      [sg.Button("Search",enable_events=True,bind_return_key=True,key="bSearch",disabled=True)]]

studentInfoLayout = [[sg.Text("Student Name",font=("Arial",16),key='stName'),sg.Text("  :  ",font=("Arial",16)),
                      sg.Text("Home School",font=("Arial",16),size=(45,1),key='hsName')],
                     [sg.Table(values = stInfoDataValues,headings=stInfoHeadings,key="schedule",
                               col_widths=dataColWidths,auto_size_columns=False,justification='left')]]

studentdetLableCol = [[sg.Text("UserId (Schoology)")],
                                         [sg.Text("First Name")],
                                        [sg.Text("Last Name")],
                                        [sg.Text("Email Address")],
                                        [sg.Text("Home School")],
                                        [sg.Text("Technical Program")],
                                         [sg.Text("Days Absent")],
                                        [sg.Text("Days Tardy")]]


studentDetInputCol = [[sg.InputText("",size = (20,1),key=("sUserId"))],
                   [sg.InputText("",size=(30,1),key="sFirst")],
                   [sg.InputText("",size=(30,1),key="sLast")],
                   [sg.InputText("",size=(30,1),key="sEmail")],
                   [sg.InputText("", size=(30, 1), key="sHomeSchool")],
                   [sg.InputText("", size=(30, 1), key="sTprogram")],
                   [sg.InputText("", size=(30, 1), key="sAbsent")],
                   [sg.InputText("", size=(30, 1), key="sTardy")]]



stGradeHeadings = ['Course Name','Overall Grade']
stGradeDataValues = [['',''],['','']]
stGradeWidths = [40,10]

studentGradeFrame = [[sg.Table(values = stGradeDataValues,headings=stGradeHeadings,col_widths=stGradeWidths,
                                key="grades",auto_size_columns=False, num_rows=10,enable_events=False,size=(20,10))]]

StudentDetColumn= [[sg.Column(studentdetLableCol),sg.Column(studentDetInputCol)],
                [sg.Checkbox("All Day Student",key="sAllDay")],
                [sg.Frame("Grades",studentGradeFrame,size=(200,25),key="Grades")]]


schedulingFrames = [[sg.Frame("Student Info",studentInfoLayout)],
                    [sg.Frame("Student Lookup",studentLookupLayout)]]

infoColumn = [[sg.Column(schedulingFrames)]]

schedulingLayout = [[sg.Frame('Student Schedules',infoColumn),sg.Frame("Student Details",StudentDetColumn,size=(500,9))]]




#######################################
#
#Attendance Tab layout
#
#######################################
stAbsHeadings = ['Id','First Name','Last Name','Absences']
stAbsDataValues = [['','','',''],['','','','']]
stAbsWidths = [10,15,15,5]
stLateHeadings = ['Id','First Name','Last Name','Late']
stLateDataValues = [['','','',''],['','','','']]
stLateWidths = [10,15,15,5]
absentLayout = [[sg.Table(values = stAbsDataValues,headings= stAbsHeadings,key='absTable',col_widths=stAbsWidths,
                          auto_size_columns=False,num_rows=15,justification='left',enable_events=True)]]

lateLayout = [[sg.Table(values = stLateDataValues,headings= stLateHeadings,key='lateTable',col_widths=stLateWidths,
                          auto_size_columns=False,num_rows=15,justification='left',enable_events=True)]]

absentLayout = [[sg.Table(values = stAbsDataValues,headings= stAbsHeadings,key='absTable',col_widths=stAbsWidths,
                          auto_size_columns=False,num_rows=15,justification='left',enable_events=True)]]


scAbsHeadings = ['School','Total by School','% of Total']
scAbsDataValues = [['','',''],['','','']]
scAbsWidths = [20,15,10]
labelCol = [[sg.Text("Student Count:")],
            [sg.Text("# School Days:")],
            [sg.Text("# Absences:")],
            [sg.Text("Attendance Rate")]]

fieldCol = [[sg.InputText("",size=(10,1),readonly=True,key="stuCount")],
            [sg.InputText("",size=(10,1),readonly=True,key="nSchoolDays")],
            [sg.InputText("",size=(10,1),readonly=True,key="nAbsenses")],
            [sg.InputText("",size =(10,1),readonly=True,key="AbsRate")]]

schLabelCol = [[sg.Text("Berkeley Springs")],
               [sg.Text("Faculty")],
               [sg.Text("Hedgesville")],
               [sg.Text("Home Schooled")],
               [sg.Text("Jefferson")],
               [sg.Text("Martinsburg")],
               [sg.Text("Musselman")],
               [sg.Text("Paw Paw")],
               [sg.Text("Spring Mills")],
               [sg.Text("Washington")],
               [sg.Text(" ", size = (10,2))]]

schFieldCol = [[sg.InputText("",size=(5,1),readonly=True,key="berkeleySprings")],
               [sg.InputText("",size=(5,1),readonly=True,key="faculty")],
            [sg.InputText("",size=(5,1),readonly=True,key="hedgesville")],
            [sg.InputText("",size=(5,1),readonly=True,key="home")],
            [sg.InputText("",size =(5,1),readonly=True,key="jefferson")],
            [sg.InputText("",size=(5,1),readonly=True,key="martinsburg")],
            [sg.InputText("",size=(5,1),readonly=True,key="musselman")],
            [sg.InputText("",size =(5,1),readonly=True,key="PawPaw")],
            [sg.InputText("",size=(5,1),readonly=True,key="springMills")],
            [sg.InputText("",size =(5,1),readonly=True,key="washington")],
            [sg.Text(" ",size= (10,2))]]

schoolAbsLayout = [[sg.Column(layout=schLabelCol),
                    sg.Column(layout=schFieldCol)]]

absentStatsLayout = [[sg.Column(layout=labelCol),sg.Column(layout=fieldCol)],
                    [sg.HorizontalSeparator()]]


aLayout = [[sg.Image(filename=".\dashTitle.png"),sg.Stretch(),sg.Image(filename=".\JRTISD-Logo-s.png",size=(250,100))],
          [sg.Text("No File has been loaded.  Please load a file before proceeding",key="afilemessage"), sg.Button("Load Attendance",enable_events=True,key="aload")],
          [sg.ProgressBar(100, orientation="horizontal",size = (500,10),bar_color=("blue","white"),key="abar")],
          [sg.HorizontalSeparator()],
          [sg.Frame("Student Absences",absentLayout,pad=((0,0),(0,45))),
           sg.Frame("Attendance Statistics:",absentStatsLayout,pad=((8,5),(0,192))),
           sg.Frame("Absences by School",schoolAbsLayout),
           sg.Frame("Late Students",lateLayout,pad=((0,0),(0,40)))],
           [sg.StatusBar("",key="abstatus",size=(1000,1))]]

#######################################
#
#  User tab Layouts
#
#######################################

userHeadings = ['Email (ID)','First Name','Last Name','Password','Role','Teacher','Subject']
userValues = [['','','','','','',''],['','','','','','','']]
userWidths = [25,15,15,15,10,7,15]
userdetLableCol = [[sg.Text("UserId (Email)")],
                   [sg.Text("First Name")],
                   [sg.Text("Last Name")],
                   [sg.Text("Password")],
                   [sg.Text("Role")]]
roleDrop = ['user','Teacher','admin','Ink']
subjectDrop = ['Coding','Cisco','English','Welding','Pro-start']

userDetInputCol = [[sg.InputText("",size = (20,1),key=("aUserId"))],
                   [sg.InputText("",size=(20,1),key="aFirst")],
                   [sg.InputText("",size=(20,1),key="aLast")],
                   [sg.InputText("",size=(20,1),key="aPass")],
                   [sg.Combo(roleDrop,default_value="user",key="aRole")]]
userDetFrame = [[sg.Column(userdetLableCol),sg.Column(userDetInputCol)],
                [sg.Checkbox("Teacher",key="isTeacher"),sg.Combo(subjectDrop,key="subject")],
                [sg.Button("New",key="aNew"),sg.Button("Save",key="aSave"),sg.Stretch(),sg.Button("Delete",key="aDelete")]]

userAdminLayout = [[sg.Text("JRTI User Administration",font=("Arial",35),justification="left",relief="flat"),
              sg.Stretch(),sg.Image(filename=".\JRTISD-Logo-s.png",size=(250,100))],
             [sg.Table(values = userValues,headings=userHeadings,key="usertable",select_mode='browse',enable_events=True,
                col_widths=userWidths,auto_size_columns=False,justification='left',num_rows=20),
                sg.Frame("User Details",userDetFrame,vertical_alignment="top")]]

#######################################
#
# set up the Tab group for the entire fLayout
#
#######################################

tabgrp = [[sg.TabGroup([[sg.Tab("Grade DashBoard",layout,key="gradeTab"),sg.Tab("Attendance DashBoard",
                aLayout,key="attendTab"),sg.Tab("Student Information",schedulingLayout,key="schedTab"),
                sg.Tab("Teachers",teacherLayout,key="teachTab"),
                sg.Tab("User Admin",userAdminLayout,key="uAdminTab")]],enable_events=True,key="tab")]]

upperTeachers = []
validated = False

validated,role = login.Login()
if not validated:
    sg.popup_ok("User not validated, Please see JRTI Software Development")
else:
    for name in teacherList:
        upperTeachers.append(name.upper())
    window = sg.Window("JRTI Schoology Dashboard",tabgrp,finalize=True,resizable=True,size = (1400,600))
    window['pBar'].update(0,visible=False)
    gradeObj = schoolData()

    window['noschool'].update(disabled=True)
    window['tinterim'].update(disabled=False)
    window['sinterim'].update(disabled=True)

    gradeObj.setSecurity(role)
    gradeObj.initialLoadDb()

    while True:
        event,values = window.read()
        tName = str(event)
        tName = tName.replace(":","")
        tName = tName.replace("{}","")
        tName = tName.rstrip()
        tName = tName.upper()

        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
        elif event == "tinterim":
            gForT.interimToTeachers()
        elif event == "aSave":
            userid = values["aUserId"]
            first = values["aFirst"]
            last = values["aLast"]
            pwrd = values["aPass"]
            role = values["aRole"]
            teacher = values["isTeacher"]
            subject = values["subject"]
            gradeObj.addUser(userid,pwrd,role,first,last,teacher,subject)
            gradeObj.refreshUserListDB()
        elif event == "aDelete":
            userid = values["aUserId"]
            gradeObj.deleteUser(userid)
            userList = gradeObj.refreshUserListDB()
        elif event == "usertable":
            rowNum = values["usertable"]
            rows = window["usertable"].get()
            row = int(rowNum[0])
            selRow = (rows[row])
            window["aUserId"].update(selRow[0])
            window["aFirst"].update(selRow[1])
            window["aLast"].update(selRow[2])
            window["aPass"].update(selRow[3])
            window["aRole"].update(selRow[4])
        elif event == "fail":
            rowNum = values["fail"]
            rows = window["fail"].get()
            row = int(rowNum[0])
            selRow = (rows[row])
            UserId = selRow[0]
            gradeObj.getSingleStuGrades(UserId)
        elif event == "absTable":
            rowNum = values["absTable"]
            rows = window["absTable"].get()
            row = int(rowNum[0])
            selRow = (rows[row])
            UserId = selRow[0]
            gradeObj.getStuAbsDetail(UserId)
        elif event == 'hide':
            if window["hide"].get():
                window["failframe"].update(visible=False)
            else:
                window["failframe"].update(visible=True)

        elif event == "sSearch":
            subString = values['sSearch']
            tValues = gradeObj.studentSearch(subString)
            if tValues == "Not Found":
                pass
            else:
                window["slook"].update(values=tValues)
                if len(tValues) == 1:
                    window['bSearch'].update(disabled=False)
        elif tName in upperTeachers:
            sList = gradeObj.missingGradeTeacher(gradeData, tName)
            text = window['info']
            text.update("")
            for missing in sList:
                text.update(text.get() + "\n" + missing)
        elif event == "aNew":
            window["aUserId"].update("")
            window["aFirst"].update("")
            window["aLast"].update("")
            window["aPass"].update("")
            window["aRole"].update("")

        elif event == "bSearch" or event == 'slook':
            if event == 'bSearch':
                indx3 = 0
            else:
                indx = (values['slook'])
                indx1 = (str(indx))
                indx2 = indx1.replace("[","")
                indx2 = indx2.replace("]", "")
                indx3 = int(indx2)
            nlist = window['slook'].get()
            targetName = nlist[indx3]
            fName = targetName[0]
            lName = targetName[1]
            hschool = targetName[2]

            sInfo, sdetail,aCount,lCount, techProgram,allDay,gList = gradeObj.getStudentInfo(lName,fName)
            print(gList)
            window['schedule'].update(values=sInfo)
            window['stName'].update(fName + " " + lName)
            window['hsName'].update(hschool)
            window['sFirst'].update(fName)
            window['sLast'].update(lName)
            window['sHomeSchool'].update(hschool)
            window['sUserId'].update(sdetail[0][0])
            window['sEmail'].update(sdetail[0][1])
            window['sAbsent'].update(aCount[0])
            window['sTardy'].update(lCount[0])
            window['sTprogram'].update(techProgram)
            window['sAllDay'].update(allDay)
            window['grades'].update(values=gList)
            print(sdetail)
            print (aCount, lCount)

        elif event == "tab":
            if values["tab"] == "uAdminTab":
                userList = gradeObj.refreshUserListDB()
            elif values["tab"] == "teachTab":
                tList = gradeObj.getTeacherStats()
            elif values["tab"] == "attendTab":
                wDays, stCount, abCount, attRate = gradeObj.getStuAbsTot()
                window["nSchoolDays"].update(wDays)
                window["stuCount"].update(stCount)
                window["nAbsenses"].update(abCount)
                window["AbsRate"].update(attRate)
        elif event == "aload":
            window['status'].update("Loading Attendance!!")
            aData = gradeObj.loadAttData()
            result = gradeObj.loadAttendanceDB(aData)
            window['status'].update("")
        elif event == "-Load-":
            loadCount = 0
            #
            # Loading student into data frame and then the database
            #
            window['pBar'].update(loadCount,visible=True)
            window['status'].update("Loading Data into Data Frame")
            gradeData = gradeObj.loadAttData()
            searchData = copy.deepcopy((gradeData))
            searchData.drop_duplicates(subset=['First Name','Last Name'],inplace=True)
            searchData.fillna("",inplace=True)
            window['status'].update("Loading student table in the database")
            pCount = gradeObj.loadStudentTable(gradeData)
            #
            # Loading Marking period data in to fLayout todo Pull this from the data base
            #
            window['status'].update("Loading marking period data")
            TermList = gradeObj.loadMarkingPeriod(gradeData)
            #
            # Load the class schedule data to the database
            #
            window['status'].update("Loading class schedule data")
            pCount = gradeObj.loadClassData(gradeData,pCount)
            #
            window['status'].update("Loading Assignment data.")
            pCount = gradeObj.loadAssignmentTable(gradeData,pCount)
            #
            window['status'].update("Getting missing Grades List and number of Grades")
            #
            #
            #
            window['-FileMessage-'].update("File has been Loaded!!")
            window['-Load-'].update(disabled=True)
            window['pBar'].update(0,visible=False)
            window['noschool'].update(disabled=False)
            window['tinterim'].update(disabled=True)
            window['sinterim'].update(disabled=True)
            window['bSearch'].update(disabled = False)
            window['status'].update("Data Loaded")
            gradesLoaded=True
        else:
            print (event,values)










