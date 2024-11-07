# !pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
# path/to/your/google_drive_manager.py
"""
简要说明：此脚本演示如何使用Google Drive API进行类OS操作，并优化API调用以减少配额的占用。
使用方法：
1. 确保已安装所需库。
2. 修改凭据路径。
3. 调用GoogleDriveManager类中的方法进行操作。

工作流：
1. 设置Google Drive API凭据。
2. 列出文件。
3. 创建文件夹。
4. 上传文件。
5. 下载文件。
6. 删除文件。
7. 通过路径获取文件ID。
8. 从Colab路径获取文件ID。
9. 遍历文件夹（类似于os.walk），优化API调用。

流编号：
1. 设置凭据
2. 列出文件
3. 创建文件夹
4. 上传文件
5. 下载文件
6. 删除文件
7. 通过路径获取文件ID
8. 从Colab路径获取文件ID
9. 遍历文件夹
"""

import os
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

class GoogleDriveManager:
    def __init__(self, creds_path):
        """初始化GoogleDriveManager
        :param creds_path: 服务账户凭据文件路径
        """
        self.creds = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.service = build('drive', 'v3', credentials=self.creds)

    def _pause(self):
        """控制API请求频率"""
        time.sleep(1)  # 设置延迟，单位为秒

    def list_files(self, page_size=10):
        """列出Google Drive中的文件
        :param page_size: 每页显示的文件数量
        """
        results = []
        page_token = None

        while True:
            self._pause()
            response = self.service.files().list(
                pageSize=page_size,
                pageToken=page_token,
                fields="nextPageToken, files(id, name)"
            ).execute()
            results.extend(response.get('files', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break

        if not results:
            print('没有找到文件。')
        else:
            print('文件列表:')
            for item in results:
                print(f'{item["name"]} ({item["id"]})')

    def create_folder(self, folder_name):
        """创建文件夹
        :param folder_name: 文件夹名称
        """
        self._pause()
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')
        print(f'创建的文件夹ID: {folder_id}')
        return folder_id

    def upload_file(self, file_path, mime_type, folder_id='root'):
        """上传文件到指定的Google Drive文件夹
        :param file_path: 要上传的文件路径
        :param mime_type: 文件的MIME类型
        :param folder_id: 目标文件夹的ID，默认为根目录
        """
        self._pause()
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]  # 指定上传的文件夹ID
        }
        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f'文件上传成功，ID为: {file.get("id")}')


    def download_file(self, file_id, destination):
        """从Google Drive下载文件
        :param file_id: 文件ID
        :param destination: 保存到本地的路径
        """
        self._pause()
        request = self.service.files().get_media(fileId=file_id)
        with open(destination, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f'下载 {int(status.progress() * 100)}%.')

    def delete_file(self, file_id):
        """删除Google Drive中的文件
        :param file_id: 文件ID
        """
        self._pause()
        self.service.files().delete(fileId=file_id).execute()
        print(f'文件ID {file_id} 已被删除。')

    def get_file_id_by_path(self, path):
        """通过路径获取文件的ID
        :param path: 文件或文件夹的路径
        :return: 文件ID，如果未找到则返回None
        """
        parts = path.split('/')  # 假设路径用'/'分隔
        folder_id = 'root'  # 从根目录开始

        for part in parts:
            self._pause()
            query = f"'{folder_id}' in parents and name='{part}'"
            response = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType)",
                pageSize=1  # 只需要获取第一个结果
            ).execute()

            items = response.get('files', [])
            if not items:
                print(f'未找到文件或文件夹: {part}')
                return None
            folder_id = items[0]['id']  # 更新folder_id为当前文件夹的ID

        return folder_id  # 返回最后找到的ID

    def get_file_id_from_colab_path(self, colab_path):
        """从Colab路径获取文件的ID
        :param colab_path: Colab中的文件路径，例如'/content/drive/My Drive/your_folder/your_file'
        :return: 文件ID，如果未找到则返回None
        """
        # 从Colab路径中提取文件的相对路径
        relative_path = colab_path.replace('/content/drive/My Drive/', '')  # 去掉Colab的根路径
        return self.get_file_id_by_path(relative_path)  # 调用已定义的方法获取文件ID

    def walk(self, folder_id='root'):
        """遍历Google Drive中的文件和文件夹，类似于os.walk
        :param folder_id: 起始文件夹的ID，默认为根目录
        """
        results = []
        page_token = None

        while True:
            self._pause()
            query = f"'{folder_id}' in parents"
            response = self.service.files().list(
                q=query,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType)"
            ).execute()
            results.extend(response.get('files', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break

        for item in results:
            print(f'文件: {item["name"]} (ID: {item["id"]})')
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                self.walk(item['id'])  # 如果是文件夹，递归调用

if __name__ == '__main__':
    # 创建Google Drive管理对象
    gdrive_manager = GoogleDriveManager('credentials.json')

    # # 列出文件
    # gdrive_manager.list_files(page_size=10)

    # # 创建文件夹
    # folder_id = gdrive_manager.create_folder('新文件夹')

    # # 上传文件
    # gdrive_manager.upload_file('temp.txt', 'text/plain', folder_id=folder_id)

    # 下载文件
    colab_file_path = '/content/drive/MyDrive/audios/2022 最新 Android 基础教程，从开发入门到项目实战，看它就够了，更新中/01-课程前面的话.aac'  # Colab中的文件路径
    file_id = gdrive_manager.get_file_id_from_colab_path(colab_file_path)  # 从Colab路径获取ID
    if file_id:
        gdrive_manager.download_file(file_id, 'temp2.txt')

    # # 删除文件
    # file_id_to_delete = gdrive_manager.get_file_id_from_colab_path(colab_file_path)  # 从Colab路径获取ID
    # if file_id_to_delete:
    #     gdrive_manager.delete_file(file_id_to_delete)

    # 遍历文件夹
    print("遍历Google Drive中的文件和文件夹:")
    gdrive_manager.walk()
