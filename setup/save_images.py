import os
import subprocess
import base64
import argparse


class ImageInfoItem:
    def __init__(self, repo, tag, image_id, filepath=None):
        self.repo = repo
        self.tag = tag
        self.image_id = image_id
        self.filepath = filepath

    @classmethod
    def from_docker(cls):
        result = subprocess.run(['docker', 'images'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        images_info = output.splitlines()

        image_items = []
        for line in images_info:
            if line.startswith("REPOSITORY"):
                continue
            parts = line.split()
            repo = parts[0]
            tag = parts[1]
            image_id = parts[2]
            image_items.append(cls(repo, tag, image_id))

        return image_items

    @classmethod
    def from_dir(cls, dir_path):
        image_items = []
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".tar"):
                    file_path = os.path.join(root, file)
                    parts = file[:-4].split("_")
                    encoded_repository = parts[0]
                    tag = parts[1]
                    image_id = parts[2]
                    repo = base64.b64decode(encoded_repository).decode('utf-8')
                    image_items.append(cls(repo, tag, image_id, file_path))

        return image_items

    def get_save_file_name(self, save_dir):
        """
        根据镜像的仓库名、标签和镜像ID生成保存镜像的文件名，并将仓库名进行Base64编码，
        然后拼接成完整的文件名路径并返回。
        """
        encoded_repository = base64.b64encode(self.repo.encode('utf-8')).decode('utf-8')
        return os.path.join(save_dir, f"{encoded_repository}_{self.tag}_{self.image_id}.tar")

    def to_file(self, save_dir):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        save_file = self.get_save_file_name(save_dir)

        if os.path.exists(save_file):
            choice = input(f"文件 {save_file} 已存在，是否覆盖？(y/n) ")
            if choice!= "y":
                print(f"跳过保存镜像 {self.repo}:{self.tag}")
                return
        save_command = ['docker','save', '-o', save_file, self.image_id]
        result = subprocess.run(save_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        if result.returncode == 0:
            print(f"镜像 {self.repo}:{self.tag} 已成功保存到 {save_file}")
        else:
            print(f"保存镜像 {self.repo}:{self.tag} 失败，请检查原因。")

    def to_docker(self):
        load_command = ['docker', 'load', '-i', self.filepath]
        subprocess.run(load_command)

        tag_command = ['docker', 'tag', self.image_id, f"{self.repo}:{self.tag}"]
        subprocess.run(tag_command)


def main():
    parser = argparse.ArgumentParser(description="Docker镜像保存和加载工具")
    parser.add_argument("--save", help="保存镜像的目录")
    parser.add_argument("--loads", help="加载镜像的目录")
    args = parser.parse_args()

    if args.save:
        image_items = ImageInfoItem.from_docker()
        for item in image_items:
            item.to_file(args.save)
    if args.loads:
        image_items = ImageInfoItem.from_dir(args.loads)

        loaded_image_ids = [item.image_id for item in ImageInfoItem.from_docker()]
        image_items = [item for item in image_items if item.image_id not in loaded_image_ids]

        [item.to_docker() for item in image_items]


if __name__ == "__main__":
    main()
