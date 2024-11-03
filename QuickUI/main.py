# main.py
import gradio as gr
from config.repo_config import configure_repo, create_symlink
from git_functions.git_utils import clone_repo, commit_and_push, pull_latest
from file_operations.file_utils import open_or_create_file, backup_file, restore_backup

def setup_repo_ui(remote_repo_url):
    # 配置仓库
    remote_url, local_dir, repo_name = configure_repo(remote_repo_url)
    create_symlink(local_dir, f"/content/{repo_name}")
    return f"Configured repo at {local_dir}"

def git_commit_and_push(commit_message):
    # Git 提交并推送
    try:
        commit_and_push(local_dir, commit_message)
        return "Pushed changes successfully."
    except Exception as e:
        return str(e)

def file_backup(filepath):
    # 文件备份操作
    backup_file(filepath)
    return f"Backup created for {filepath}"

def file_restore(filepath):
    # 文件还原操作
    restore_backup(filepath)
    return f"Restored backup for {filepath}"

# 定义Gradio界面
with gr.Blocks() as demo:
    with gr.Row():
        # 左侧按钮区
        with gr.Column(scale=1):
            gr.Markdown("### 功能分类")
            gr.Button("基础配置").click(setup_repo_ui, inputs="text", outputs="text")
            gr.Button("Git 提交推送").click(git_commit_and_push, inputs="text", outputs="text")
            gr.Button("备份文件").click(file_backup, inputs="text", outputs="text")
            gr.Button("恢复文件").click(file_restore, inputs="text", outputs="text")

        # 右侧参数输入和输出区
        with gr.Column(scale=2):
            gr.Markdown("### 输入参数")
            remote_repo_url = gr.Textbox(label="远程仓库URL")
            commit_message = gr.Textbox(label="提交信息")
            filepath = gr.Textbox(label="文件路径")
            
            gr.Markdown("### 操作输出")
            output_text = gr.Textbox(label="输出结果", interactive=False)

    # 绑定按钮动作
    gr.Button("配置仓库").click(setup_repo_ui, inputs=remote_repo_url, outputs=output_text)
    gr.Button("提交并推送").click(git_commit_and_push, inputs=commit_message, outputs=output_text)
    gr.Button("备份文件").click(file_backup, inputs=filepath, outputs=output_text)
    gr.Button("恢复文件").click(file_restore, inputs=filepath, outputs=output_text)

demo.launch()