from datetime import datetime, timedelta
import re
import os
import json
from Models import CourseTableSettings, CourseTableDisplaySettings, CourseTimeNode, CourseInfo, CourseTeachingInfo, import_data


class InvalidDateTimeFormatError(Exception):
    pass


def calculate_remaining_courses(current_date, course_teaching_infos, start_date_str='2024-9-9'):
    """
    计算给定日期剩余的课程数量。

    :param current_date: 当前日期，格式为 '%Y-%m-%d'。
    :param course_teaching_infos: 课程授课信息列表。
    :param start_date_str: 课程开始日期字符串，默认为'2024-9-9'，格式为 '%Y-%m-%d'。
    :return: 剩余课程数量。
    """
    current_date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
    start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    remaining_courses = 0
    for info in course_teaching_infos:
        end_date_obj = start_date_obj + timedelta(days=(info.endWeek - info.startWeek) * 7)
        if start_date_obj <= current_date_obj <= end_date_obj:
            remaining_courses += 1
    return remaining_courses


def find_nearest_course_info(current_datetime, course_teaching_infos, start_date_str='2024-9-9'):
    """
    获取给定日期时间最近的一堂课的信息。

    :param current_datetime: 当前日期时间，datetime 对象。
    :param course_teaching_infos: 课程授课信息列表。
    :param start_date_str: 课程开始日期字符串，默认为'2024-9-9'，格式为 '%Y-%m-%d'。
    :return: 最近一堂课的信息，如果当前没有课程安排则返回 None。
    """
    start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    nearest_class_info = None
    min_time_diff = None
    for info in course_teaching_infos:
        if not all(hasattr(info, attr) for attr in ['startWeek', 'endWeek', 'startTime', 'endTime']):
            print(f"Invalid course teaching info: {info}")
            continue
        default_start_time = "08:00"
        default_end_time = "09:00"
        startTime = info.startTime if info.startTime else default_start_time
        endTime = info.endTime if info.endTime else default_end_time
        try:
            start_datetime_obj = datetime.combine(start_date_obj + timedelta(days=(info.startWeek - 1) * 7),
                                                 datetime.strptime(startTime, '%H:%M').time())
            end_datetime_obj = datetime.combine(start_date_obj + timedelta(days=(info.endWeek - 1) * 7),
                                               datetime.strptime(endTime, '%H:%M').time())
        except ValueError as ve:
            print(f"Error parsing time for course info: {info}. Error: {ve}")
            continue
        if start_datetime_obj <= current_datetime <= end_datetime_obj:
            return info
        elif current_datetime < start_datetime_obj:
            time_diff = start_datetime_obj - current_datetime
            if min_time_diff is None or time_diff < min_time_diff:
                min_time_diff = time_diff
                nearest_class_info = info
    return nearest_class_info


def parse_datetime(input_str):
    """
    解析输入字符串为 datetime 对象。

    :param input_str: 输入的日期时间字符串，格式为 '%Y-%m-%d'、'%Y-%m-%d %H'、'%Y-%m-%d %H:%M' 或 '%Y-%m-%d %H:%M:%S'。
    :return: datetime 对象，如果输入格式错误则抛出 InvalidDateTimeFormatError 异常。
    """
    pattern = r'(\d{4}-\d{2}-\d{2})(\s(\d{2}(:\d{2})?(:\d{2})?)?)?'
    match = re.match(pattern, input_str)
    if not match:
        raise InvalidDateTimeFormatError(f"Invalid date time format: {input_str}")
    date_part = match.group(1)
    time_part = match.group(3)
    if time_part is None:
        time_part = '00:00:00'
    elif ':' not in time_part:
        time_part += ':00:00'
    elif time_part.count(':') == 1:
        time_part += ':00'
    datetime_str = f'{date_part} {time_part}'
    try:
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise InvalidDateTimeFormatError(f"Invalid date time format: {input_str}")


def convert_to_datetime(input_str):
    """
    将输入字符串转换为 datetime 对象，进行空检查和错误检测。

    :param input_str: 输入的字符串。
    :return: datetime 对象，如果输入为空或格式错误则返回 None。
    """
    if not input_str:
        print("Input string is empty.")
        return None
    try:
        return parse_datetime(input_str)
    except InvalidDateTimeFormatError as e:
        print(f"Error converting to datetime: {e}")
        return None


def test_functions():
    file_path = os.path.join(os.path.dirname(__file__), 'table.txt')
    course_table_settings, course_table_display_settings, course_time_nodes, course_infos, course_teaching_infos = import_data(file_path)

    # 直接提供参数测试
    test_date_str = "2024-11-02"
    test_datetime_str = "2024-11-02 15:30:00"

    test_date = convert_to_datetime(test_date_str)
    if test_date is None:
        print("日期格式错误。")
    else:
        print(f"转换后的日期：{test_date}")
        remaining_courses = calculate_remaining_courses(test_date.strftime('%Y-%m-%d'), course_teaching_infos)
        print(f"剩余课程数: {remaining_courses}")

    test_datetime = convert_to_datetime(test_datetime_str)
    if test_datetime is None:
        print("日期时间格式错误。")
    else:
        print(f"转换后的日期时间：{test_datetime}")
        nearest_class_info = find_nearest_course_info(test_datetime, course_teaching_infos)
        if nearest_class_info:
            # 处理空值并格式化输出
            formatted_info = {
                "id": nearest_class_info.id if hasattr(nearest_class_info, 'id') else None,
                "courseId": nearest_class_info.courseId if hasattr(nearest_class_info, 'courseId') else None,
                "teacherId": nearest_class_info.teacherId if hasattr(nearest_class_info, 'teacherId') else None,
                "startWeek": nearest_class_info.startWeek if hasattr(nearest_class_info, 'startWeek') else None,
                "endWeek": nearest_class_info.endWeek if hasattr(nearest_class_info, 'endWeek') else None,
                "startTime": nearest_class_info.startTime if nearest_class_info.startTime else "未设置",
                "endTime": nearest_class_info.endTime if nearest_class_info.endTime else "未设置",
                "room": nearest_class_info.room if nearest_class_info.room else "未设置",
                "startNode": nearest_class_info.startNode if hasattr(nearest_class_info, 'startNode') else None,
                "ownTime": nearest_class_info.ownTime if hasattr(nearest_class_info, 'ownTime') else None,
                "level": nearest_class_info.level if hasattr(nearest_class_info, 'level') else None
            }
            pretty_nearest_info = json.dumps(formatted_info, ensure_ascii=False,indent=4)
            print(f"最近一堂课信息: {pretty_nearest_info}")
        else:
            print("当前没有课程安排")


if __name__ == "__main__":
    test_functions()

