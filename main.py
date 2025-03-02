#--coding:utf-8--
#kivy使用zipfile压缩文件并删除源文件CompressZipFile2.py
#有开始确认和退出确认，开始后标签上增加显示进行中...
#显示任务完成后进度条只完成90%
#在pydroid中小部件尺寸异常，按钮中文正常，文件名中文乱码
#改名后的文件夹里的子文件夹下的文件没能压缩
import kivy
import os
import threading
import logging
import zipfile
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.core.text import LabelBase
from datetime import datetime
from kivy import utils

# 注册中文字体（使用相对路径）
LabelBase.register(name='SimHei', fn_regular='data/fonts/SimHei.ttf')

# 配置日志记录
project_root = os.path.dirname(os.path.abspath(__file__))
# 动态获取用户数据目录
if utils.platform == 'android':
    # Android平台使用内部存储
    log_file_path = os.path.join(utils.app_user_dir(), "file_processing.log")
else:
    # 其他平台使用标准用户目录
    log_file_path = os.path.join(os.path.expanduser('~'), ".kivy", "file_processing.log")

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class CompressApp(App):
    status_label = ObjectProperty(None)
    progress_bar = ObjectProperty(None)
    progress_label = ObjectProperty(None)
    total_files = 0
    processed_files = 0

    def build(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        try:
            self.file_chooser = FileChooserIconView(font_name='SimHei.ttf')
            self.file_chooser.path = os.getcwd()
            self.layout.add_widget(self.file_chooser)

        except Exception as e:
            self.update_status(f"处理文件 {self.file_chooser.path} 时发生错误: {e}")
            logging.error(f"处理文件 {self.file_chooser.path} 时发生错误: {e}")
        
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        self.compress_button = Button(text="选择并压缩", font_name='SimHei.ttf',size_hint_y=None,
                              height=150)#"./simhei.ttf")
        self.quit_button = Button(text="退出", font_name='simhei.ttf',size_hint_y=None,
                              height=150)#"./simhei.ttf")

        button_layout.add_widget(self.compress_button)
        button_layout.add_widget(self.quit_button)
        self.layout.add_widget(button_layout)

        self.compress_button.bind(on_press=self.confirm_compress)
        self.quit_button.bind(on_press=self.show_quit_confirmation_popup)

        self.status_label = Label(
            text="这是一个很长的文本，用于测试 Kivy 的 Label 控件的自动换行功能。",
            size_hint=(1, None),  # 宽度占满父布局，高度由内容决定
            height=200,  # 设置 Label 的高度
            text_size=(None, None),  # 初始设置为 None，稍后绑定
            halign='left',  # 水平左对齐
            valign='top',  # 垂直顶部对齐
            padding=(10, 10),  # 设置内边距
            font_name="simhei.ttf"
        )
        # 动态绑定 text_size 到 Label 的宽度
        self.status_label.bind(
            width=lambda *x: self.status_label.setter('text_size')(self.status_label, (self.status_label.width, None))
        )
        self.layout.add_widget(self.status_label)

        self.progress_label = Label(text="0%", font_name='simhei.ttf', size_hint_y=None, height=20)
        self.layout.add_widget(self.progress_label)
        
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=20)
        self.layout.add_widget(self.progress_bar)


        return self.layout

    def on_start(self):
        """平台适配的权限请求"""
        if kivy.utils.platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])



    def show_quit_confirmation_popup(self, instance):
        content = BoxLayout(orientation='vertical')
        message = Label(text="确定要退出吗？", font_name='simhei.ttf')
        yes_button = Button(text="退出", font_name='simhei.ttf', size_hint_y=None, height=120)
        no_button = Button(text="取消", font_name='simhei.ttf', size_hint_y=None, height=120, on_press=lambda *args: self.quit_confirmation_popup.dismiss())

        yes_button.bind(on_release=self.quit_app)
        content.add_widget(message)
        button_layout = BoxLayout(orientation='horizontal', spacing=10)
        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)
        content.add_widget(button_layout)

        self.quit_confirmation_popup = Popup(title="确认退出", title_font='simhei.ttf', content=content, size_hint=(None, None), size=(800, 600))
        self.quit_confirmation_popup.open()

    def quit_app(self, instance):
        self.quit_confirmation_popup.dismiss()
        App.get_running_app().stop()

    def confirm_compress(self, instance):
        content = BoxLayout(orientation='vertical')
        message = Label(text="确定要开始压缩吗？", font_name='simhei.ttf')
        confirm_button = Button(text="开始", font_name='simhei.ttf', size_hint_y=None, height=120)
        cancel_button = Button(text="取消", font_name='simhei.ttf', size_hint_y=None, height=120)

        content.add_widget(message)
        button_layout = BoxLayout(orientation='horizontal', spacing=10)
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)

        popup = Popup(title="确认压缩", title_font='simhei.ttf', content=content, size_hint=(None, None), size=(800, 600))
        confirm_button.bind(on_release=lambda x: (self.start_compress_thread(), popup.dismiss()))
        cancel_button.bind(on_release=popup.dismiss)
        popup.open()

    def start_compress_thread(self):
        self.status_label.text = "进行中..."
        self.total_files = sum([len(files) for root, dirs, files in os.walk(self.file_chooser.path)])
        self.processed_files = 0
        threading.Thread(target=self.compress_and_delete_files, daemon=True).start()

    #######################

    
    def log_info(self, message):
        """记录 INFO 级别的日志，并更新界面状态"""
        logging.info(message)
        self.update_status(message)  # 将信息输出到界面
        print(f"[INFO] {message}")
    
    def log_warning(self, message):
        """记录 WARNING 级别的日志，并更新界面状态"""
        logging.warning(message)
        self.update_status(message)  # 将信息输出到界面
        print(f"[WARNING] {message}")
    
    def log_error(self, message):
        """记录 ERROR 级别的日志，并更新界面状态"""
        logging.error(message)
        self.update_status(message)  # 将信息输出到界面
        print(f"[ERROR] {message}")

    def compress_and_delete_files(self):
        directory_path = self.file_chooser.path
        if not os.path.isdir(directory_path):
            self.log_error("无效的目录路径")
            return

        # 定义需要删除的文字
        text_to_remove_in_dir = "（含视频讲解）"  # 目录中需要删除的文字
        text_to_remove_in_file = "【公众号：微课资料站】"  # 文件名中需要删除的文字

        try:
            for root, dirs, files in os.walk(directory_path, topdown=True):
                # 修改当前目录名
                new_root = root.replace(text_to_remove_in_dir, "")
                if new_root != root:
                    try:
                        os.rename(root, new_root)
                        root = new_root
                        self.log_info(f"修改目录名: {root} -> {new_root}")
                        print(f"修改目录名: {root} -> {new_root}")
                        # 更新 dirs 列表中的目录名
                        dirs[:] = [d.replace(text_to_remove_in_dir, "") for d in dirs]
                    except Exception as e:
                        self.log_error(f"修改目录名失败: {root} -> {new_root}, 错误: {e}")

                for file in files:
                    file_path = os.path.join(root, file)
                    file_path = os.path.normpath(file_path)  # 规范化路径
                    print("规范化路径: ", file_path)

                    # 修改文件名
                    new_file = file.replace(text_to_remove_in_file, "")
                    new_file_path = os.path.join(root, new_file)
                    print("新文件名和路径: ", new_file_path)
                    if new_file != file:
                        try:
                            os.rename(file_path, new_file_path)
                            file_path = new_file_path

                            self.log_info(f"修改文件名: {file} -> {new_file}")
                            print(f"修改文件名: {file} -> {new_file}")

                        except Exception as e:
                            self.log_error(f"修改文件名失败: {file} -> {new_file}, 错误: {e}")
                            continue
                    else:
                        pass  # 新旧文件名相同，无需处理

                    # 添加日志和存在性检查
                    self.log_info(f"正在处理文件: {file_path}")
                    if not os.path.exists(file_path):
                        self.log_error(f"文件不存在: {file_path}")
                        continue

                    # 检查文件权限
                    if not os.access(file_path, os.R_OK):
                        self.log_error(f"无读取权限: {file_path}")
                        continue

                    if is_archive_file(file_path):
                        self.log_info(f"跳过压缩文件: {file_path}")
                        continue

                    # 压缩文件
                    output_zip = os.path.join(root, f"{os.path.splitext(new_file)[0]}.zip")
                    try:
                        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                            # 仅压缩文件本身，不包含目录结构
                            zipf.write(file_path, arcname=new_file)
                            self.log_info(f"{file_path} 已压缩至 {output_zip}")

                        # 检查删除权限
                        if not os.access(file_path, os.W_OK):
                            self.log_error(f"无删除权限: {file_path}")
                            continue

                        # 删除源文件
                        os.remove(file_path)
                        self.log_info(f"已删除 {file_path}")

                    except PermissionError:
                        self.log_error(f"权限不足，无法压缩或删除 {file_path}")
                    except Exception as e:
                        self.log_error(f"处理文件 {file_path} 时发生错误: {e}")
                    finally:
                        self.processed_files += 1
                        # 重新计算 total_files
                        self.total_files = sum([len(files) for r, d, files in os.walk(directory_path)])
                        self.update_progress()

            self.log_info("所有文件已成功逐个压缩并删除源文件")
            self.update_progress()

        except Exception as e:
            self.log_error(f"发生全局错误: {e}")

    def update_status(self, text):
        self.status_label.text = text
        self.log_info(text)  # 同步记录日志

    def update_progress(self):
        if self.total_files > 0:
            print("total_files is: ",self.total_files)
            progress = (self.processed_files / self.total_files) * 100
            self.progress_bar.value = progress
            self.progress_label.text = f"{int(progress)}%"
        else:
            self.progress_bar.value = 0
            self.progress_label.text = "0%"

    def log_info(self, message):
        logging.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
        self.update_status(message)

    def log_warning(self, message):
        logging.warning(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
        self.update_status(f"警告: {message}")

    def log_error(self, message):
        logging.error(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
        self.update_status(f"错误: {message}")

def is_archive_file(file_path):
    archive_extensions = ('.zip', '.rar', '.7z', '.tar', '.gz', '.bz2')#, '.jpg', '.mp3','mp4','flv','avi','.wmv','.ts')
    return any(file_path.lower().endswith(ext) for ext in archive_extensions)

if __name__ == '__main__':
    CompressApp().run()