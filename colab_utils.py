import logging
import traceback
import re
from IPython.display import HTML, display

class HTMLFormatter(logging.Handler):
    """A logging handler that formats error messages as HTML links."""

    def emit(self, record):
        # 处理异常信息
        if record.exc_info:
            tb_str = ''.join(traceback.format_exception(*record.exc_info))
            tb_str = replace_links(tb_str)  # 替换 URL 和文件路径为超链接
            display(HTML(f"<pre>{tb_str}</pre>"))
        else:
            # 对于没有异常信息的情况，直接格式化消息文本
            formatted_message = replace_links(record.getMessage())
            display(HTML(f"<pre>{formatted_message}</pre>"))

def configure_logger():
    """配置 logger 以使用自定义的 HTMLFormatter handler"""
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(HTMLFormatter())
    return logger

def create_hyperlink(file_path, text=None, target_line=0):
    """创建一个指向文件的超链接。"""
    if text is None:
        text = file_path
    return f'<a href="#" onclick="event.preventDefault(); google.colab.files.view(\'{file_path}\', {target_line});">{text}</a>'

def create_button(file_path, text=None, target_line=0):
    """创建一个指向文件的按钮超链接。"""
    if text is None:
        text = file_path
    return f'<button onclick="event.preventDefault(); google.colab.files.view(\'{file_path}\', {target_line});">{text}</button>'

def replace_links(text):
    """替换文本中的 URL 和文件路径为超链接。

    Args:
        text (str): 需要处理的文本

    Returns:
        str: 包含超链接的 HTML 格式文本
    """
    # 匹配 URL 的正则表达式
    url_pattern = r'(https?://[^\s]+)'
    # 匹配文件路径的正则表达式（假设以 /content/ 开头）
    file_path_pattern = r'(/content/[^\s]+)'

    # 替换 URL 为超链接
    text = re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)

    # 替换文件路径为超链接，默认跳转到第 0 行
    text = re.sub(file_path_pattern, lambda match: create_hyperlink(match.group(0)), text)

    return text

if __name__ == "__main__":
    # 配置 logger
    logger = configure_logger()

    # 示例使用 create_hyperlink 函数
    hyperlink = create_hyperlink('/content/example.txt', 'Open Example.txt', 10)
    display(HTML(f"Click here to {hyperlink}"))

    # 示例使用 create_button 函数
    button_html = create_button('/content/example.txt', 'Open Example.txt', 10)
    display(HTML(button_html))

    # 测试 replace_links 函数
    sample_text = """
    Here is a URL: https://example.com and here is a file path: /content/example.txt
    """
    display(HTML(f"<pre>{replace_links(sample_text)}</pre>"))

    # 测试函数，故意引发异常
    try:
        undefined_function_call()  # 故意引发错误
    except Exception:
        logger.error("An error occurred", exc_info=True)
