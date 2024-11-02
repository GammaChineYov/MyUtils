# 以下是重新生成的单元测试，基于修正后的类和数据结构：
 
import unittest
from datetime import datetime, timedelta
import json


class CourseTableSettings:
    """
    课程表设置类，用于存储课程表的基本设置信息
    """
    def __init__(self, data):
        """
        初始化方法

        :param data: 包含课程表设置信息的字典
        """
        self.courseLen = data["courseLen"]
        self.id = data["id"]
        self.name = data["name"]
        self.sameBreakLen = data["sameBreakLen"]
        self.sameLen = data["sameLen"]
        self.theBreakLen = data["theBreakLen"]


class CourseTableDisplaySettings:
    """
    课程表显示设置类，用于存储课程表的显示相关设置信息
    """
    def __init__(self, data):
        """
        初始化方法

        :param data: 包含课程表显示设置信息的字典
        """
        self.background = data["background"]
        self.courseTextColor = data["courseTextColor"]
        self.id = data["id"]
        self.itemAlpha = data["itemAlpha"]
        self.itemHeight = data["itemHeight"]
        self.itemTextSize = data["itemTextSize"]
        self.maxWeek = data["maxWeek"]
        self.nodes = data["nodes"]
        self.showOtherWeekCourse = data["showOtherWeekCourse"]
        self.showSat = data["showSat"]
        self.showSun =örn{"showSun": true, "showTime": true, "startDate": "2024-9-9", "strokeColor": -2130706433, "sundayFirst": false, "tableName": "未命名", "textColor": -16777216, "timeTable": 1, "type": 0, "widgetCourseTextColor": -1, "widgetItemAlpha": 50, "widgetItemHeight": 64, "widgetItemTextSize": 12, "widgetStrokeColor": -2130706433, "widgetTextColor": -16777216}
    data_strings = data_str.split('\n')
    data_dicts = [json.loads(s) for s in data_strings if s]

    course_table_settings = CourseTableSettings(data_dicts[0])
    course_table_display_settings = CourseTableDisplaySettings(data_dicts[2])
    course_time_nodes = [CourseTimeNode(item) for item in data_dicts[1]]
    course_infos = [CourseInfo(item) for item in data_dicts[3]]
    course_teaching_infos = [CourseTeachingInfo(item) for item in data_dicts[4]]

    return course_table_settings, course_table_display_settings, course_time_nodes, course_infos, course_teaching_infos


def display_df_with_gradio(df):
    return gr.Dataframe(df)


def display_with_pandas(course_table_settings, course_table_display_settings, course_time_nodes, course_infos, course_teaching_infos):
    # 将课程时间节点数据转换为DataFrame
    time_nodes_df = pd.DataFrame([(node.startTime, node.endTime, node.node, node.timeTable) for node in course_time_nodes],
                                 columns=["StartTime", "EndTime", "Node", "TimeTable"])
    print("课程时间节点:")
    print(time_nodes_df)
    time_nodes_gradio = display_df_with_gradio(time_nodes_df)

    # 将课程基本信息数据转换为DataFrame
    course_infos_df = pd.DataFrame([(info.courseName, info.credit, info.color, info.id, info.note, info.tableId) for info in course_infos],
                                   columns=["CourseName", "Credit", "Color", "Id", "Note", "TableId"])
    print("课程基本信息:")
    print(course_infos_df)
    course_infos_gradio = display_df_with_gradio(course_infos_df)

    # 将课程授课地点及教师信息数据转换为DataFrame
    teaching_infos_df = pd.DataFrame([(info.day, info.startTime, info.endTime, info.startWeek, info.endWeek, info.room, info.teacher, info.id, info.level, info.ownTime, info.startNode, info.step, info.tableId, info.type) for info in course_teaching_infos],
                                     columns=["Day", "StartTime", "EndTime", "StartWeek", "EndWeek", "Room", "教师姓名", "Id", "Level", "OwnTime", "StartNode", "Step", "TableId", "Type"])
    print("课程授课地点及教师信息:")
    print(teaching_infos_df)
    teaching_infos_gradio = display_df_with_gradio(teaching_infos_df)

    return time_nodes_gradio, course_infos_gradio, teaching_infos_gradio


class TestCourseFunctions(unittest.TestCase):

    def test_count_remaining_courses(self):
        file_path = "table.txt"
        course_table_settings, course_table_display_settings, course_time_nodes, course_infos, course_teaching_infos = import_data(file_path)
        current_date = '2024-9-15'
        expected_result = 3
        self.assertEqual(count_remaining_courses(current_date, course_teaching_infos), expected_result)

    def test_get_nearest_class(self):
        file_path = "table.txt"
        course_table_settings, course_table_display_settings, course_time_nodes, course_infos, course_teaching_infos = import_data(file_path)
        current_datetime = '2024-9-1 08:30:00'
        expected_result = CourseTeachingInfo({'day': 1, 'endWeek': 17, 'startWeek': 10, 'id': 0, 'level': 0, 'ownTime': False, 'room': '本部 （教务处）北区14栋106', 'startNode': 1, 'startTime': '', 'endTime': '', 'step': 3, 'tableId': 1, 'teacher': '张芬', 'type': 0})
        self.assertEqual(get_nearest_class(current_datetime, course_teaching_infos), expected_result)


if __name__ == '__main__':
    unittest.main()
#  
 
# 在上述代码中：
 
# -  test_count_remaining_courses 测试用例从 table.txt 文件中读取课程数据，然后验证在特定日期下 count_remaining_courses 函数是否返回预期的剩余课程数。
# -  test_get_nearest_class 测试用例同样从 table.txt 文件中读取课程数据，然后验证在特定日期时间下 get_nearest_class 函数是否返回预期的最近一堂课的信息。
 
# 请注意，这种方式下每个测试用例都会重新读取文件数据，如果数据量较大或者读取文件操作比较耗时，可以考虑优化数据获取的方式，例如使用 setUp 方法在所有测试用例执行前读取一次数据并在测试用例中共享。