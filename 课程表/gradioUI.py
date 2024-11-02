from Models import import_data
import gradio as gr
import pandas as pd


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

if __name__ == "__main__":
    file_path = "table.txt"
    course_table_settings, course_table_display_settings, course_time_nodes, course_infos, course_teaching_infos = import_data(file_path)
    time_nodes_gradio, course_infos_gradio, teaching_infos_gradio = display_with_pandas(course_table_settings, course_table_display_settings, course_time_nodes, course_infos, course_teaching_infos)
    gr.Interface(
        lambda: (time_nodes_gradio, course_infos_gradio, teaching_infos_gradio),
        inputs=[],
        outputs=[gr.Dataframe() for _ in range(3)]
    ).launch()