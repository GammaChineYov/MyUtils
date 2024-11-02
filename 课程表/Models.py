# 以下是给数据类加上类注释和字段注释后的代码：
 
import json
import pandas as pd

class CourseTableSettings:
    """
    课程表设置类，用于存储课程表的基本设置信息
    """
    def __init__(self, data):
        """
        初始化方法

        :param data: 包含课程表设置信息的字典
        """
        self.courseLen = data["courseLen"]  # 课程数量
        self.id = data["id"]  # 课程表的唯一标识
        self.name = data["name"]  # 课程表名称
        self.sameBreakLen = data["sameBreakLen"]  # 与课程时间间隔相关的设置
        self.sameLen = data["sameLen"]  # 与课程时间间隔相关的设置
        self.theBreakLen = data["theBreakLen"]  # 课程间隔长度

class CourseTableDisplaySettings:
    """
    课程表显示设置类，用于存储课程表的显示相关设置信息
    """
    def __init__(self, data):
        """
        初始化方法

        :param data: 包含课程表显示设置信息的字典
        """
        self.background = data["background"]  # 课程表背景
        self.courseTextColor = data["courseTextColor"]  # 课程文本颜色
        self.id = data["id"]  # 课程表的唯一标识
        self.itemAlpha = data["itemAlpha"]  # 课程表项的透明度
        self.itemHeight = data["itemHeight"]  # 课程表项的高度
        self.itemTextSize = data["itemTextSize"]  # 课程表项的文字大小
        self.maxWeek = data["maxWeek"]  # 课程表涵盖的最大周数
        self.nodes = data["nodes"]  # 可能是预留的节点数量
        self.showOtherWeekCourse = data["showOtherWeekCourse"]  # 是否显示其他周课程
        self.showSat = data["showSat"]  # 是否显示周六课程
        self.showSun = data["showSun"]  # 是否显示周日课程
        self.showTime = data["showTime"]  # 是否显示时间
        self.startDate = data["startDate"]  # 课程开始日期
        self.strokeColor = data["strokeColor"]  # 课程表边框颜色
        self.sundayFirst = data["sundayFirst"]  # 是否周日排在首位
        self.tableName = data["tableName"]  # 课程表的实际名称
        self.textColor = data["textColor"]  # 文本颜色
        self.timeTable = data["timeTable"]  # 可能是课程表的某种标识
        self.type = data["type"]  # 课程表类型
        self.widgetCourseTextColor = data["widgetCourseTextColor"]  # 课程表小部件的课程文本颜色
        self.widgetItemAlpha = data["widgetItemAlpha"]  # 课程表小部件的课程表项透明度
        self.widgetItemHeight = data["widgetItemHeight"]  # 课程表小部件的课程表项高度
        self.widgetItemTextSize = data["widgetItemTextSize"]  # 课程表小部件的课程表项文字大小
        self.widgetStrokeColor = data["widgetStrokeColor"]  # 课程表小部件的课程表边框颜色
        self.widgetTextColor = data["widgetTextColor"]  # 课程表小部件的文本颜色

class CourseTimeNode:
    """
    课程时间节点类，用于存储课程的时间节点信息
    """
    def __init__(self, data):
        """
        初始化方法

        :param data: 包含课程时间节点信息的字典
        """
        self.endTime = data["endTime"]  # 课程节点的结束时间
        self.node = data["node"]  # 节点编号
        self.startTime = data["endTime"]  # 课程节点的开始时间
        self.timeTable = data["timeTable"]  # 与课程表的关联标识

class CourseInfo:
    """
    课程信息类，用于存储课程的基本信息
    """
    def __init__(self, data):
        """
        初始化方法

        :param data: 包含课程基本信息的字典
        """
        self.color = data["color"]  # 课程的颜色标识
        self.courseName = data["courseName"]  # 课程名称
        self.credit = data["credit"]  # 课程学分
        self.id = data["id"]  # 课程的唯一标识
        self.note = data["note"]  # 课程的备注信息
        self.tableId = data["tableId"]  # 课程所属的课程表标识

class CourseTeachingInfo:
    """
    课程授课信息类，用于存储课程的授课地点和教师等信息
    """
    def __init__(self, data):
        """
        初始化方法

        :param data: 包含课程授课信息的字典
        """
        self.day = data["day"]  # 课程授课的星期
        self.endTime = data["endTime"]  # 课程授课结束时间（可能为空）
        self.endWeek = data["endWeek"]  # 课程结束的周数
        self.id = data["id"]  # 课程的唯一标识
        self.level = data["level"]  # 可能是课程的某种级别
        self.ownTime = data["ownTime"]  # 可能是关于课程时间是否自定义的标识
        self.room = data["room"]  # 课程授课地点
        self.startNode = data["startNode"]  # 课程开始的节点编号
        self.startTime = data["startTime"]  # 课程授课开始时间（可能为空）
        self.startWeek = data["startWeek"]  # 课程开始的周数
        self.step = data["step"]  # 可能是课程授课的周期相关设置
        self.tableId = data["tableId"]  # 课程所属的课程表标识
        self.teacher = data["teacher"]  # 授课教师姓名
        self.type = data["type"]  # 课程的类型

def import_data(file_path):
    with open(file_path, 'r') as file:
        data_str = file.read()
    data_strings = data_str.split('\n')
    data_dicts = [json.loads(s) for s in data_strings if s]

    course_table_settings = CourseTableSettings(data_dicts[0])
    course_table_display_settings = CourseTableDisplaySettings(data_dicts[2])
    course_time_nodes = [CourseTimeNode(item) for item in data_dicts[1]]
    course_infos = [CourseInfo(item) for item in data_dicts[3]]
    course_teaching_infos = [CourseTeachingInfo(item) for item in data_dicts[4]]
    return course_table_settings, course_table_display_settings, course_time_nodes, course_infos, course_teaching_infos
