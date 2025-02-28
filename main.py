#kivy使用py7zr压缩文件并删除源文件5.py
#有开始确认和退出确认，开始后标签上增加显示进行中...
#显示任务完成后进度条只完成90%

import os
import threading
import py7zr
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar

class CompressApp(App):
    status_label = ObjectProperty(None)
    progress_bar = ObjectProperty(None)
    progress_label = ObjectProperty(None)  # 新增进度标签
    total_files = 0
    processed_files = 0

    def build(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.file_chooser = FileChooserIconView()
        self.file_chooser.path = os.getcwd()
        self.layout.add_widget(self.file_chooser)

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        self.compress_button = Button(text="选择并压缩", font_name="simhei.ttf")
        self.quit_button = Button(text="退出", font_name="simhei.ttf")

        button_layout.add_widget(self.compress_button)
        button_layout.add_widget(self.quit_button)
        self.layout.add_widget(button_layout)

        self.compress_button.bind(on_press=self.confirm_compress)
        self.quit_button.bind(on_press=self.show_quit_confirmation_popup)

        self.status_label = Label(text="请选择一个目录以开始", font_name="simhei.ttf", size_hint_y=None, height=40)
        self.layout.add_widget(self.status_label)

        self.progress_label = Label(text="0%", font_name="simhei.ttf", size_hint_y=None, height=20)
        self.layout.add_widget(self.progress_label)
        
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=20)
        self.layout.add_widget(self.progress_bar)


        return self.layout

    def show_quit_confirmation_popup(self, instance):
        content = BoxLayout(orientation='vertical')
        message = Label(text="确定要退出吗？", font_name="simhei.ttf")
        yes_button = Button(text="退出", font_name="simhei.ttf", size_hint_y=None, height=40)
        no_button = Button(text="取消", font_name="simhei.ttf", size_hint_y=None, height=40, on_press=lambda *args: self.quit_confirmation_popup.dismiss())

        yes_button.bind(on_release=self.quit_app)
        content.add_widget(message)
        button_layout = BoxLayout(orientation='horizontal', spacing=10)
        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)
        content.add_widget(button_layout)

        self.quit_confirmation_popup = Popup(title="确认退出", title_font="simhei.ttf", content=content, size_hint=(None, None), size=(300, 150))
        self.quit_confirmation_popup.open()

    def quit_app(self, instance):
        self.quit_confirmation_popup.dismiss()
        App.get_running_app().stop()

    def confirm_compress(self, instance):
        content = BoxLayout(orientation='vertical')
        message = Label(text="确定要开始压缩吗？", font_name="simhei.ttf")
        confirm_button = Button(text="开始", font_name="simhei.ttf", size_hint_y=None, height=40)
        cancel_button = Button(text="取消", font_name="simhei.ttf", size_hint_y=None, height=40)

        content.add_widget(message)
        button_layout = BoxLayout(orientation='horizontal', spacing=10)
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)

        popup = Popup(title="确认压缩", title_font="simhei.ttf", content=content, size_hint=(None, None), size=(300, 150))
        confirm_button.bind(on_release=lambda x: (self.start_compress_thread(), popup.dismiss()))
        cancel_button.bind(on_release=popup.dismiss)
        popup.open()

    def start_compress_thread(self):
        self.status_label.text = "进行中..."
        self.total_files = sum([len(files) for root, dirs, files in os.walk(self.file_chooser.path)])
        self.processed_files = 0
        threading.Thread(target=self.compress_and_delete_files, daemon=True).start()

    def compress_and_delete_files(self):
        directory_path = self.file_chooser.path
        if not os.path.isdir(directory_path):
            self.update_status("无效的目录路径")
            return

        try:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)

                    if is_archive_file(file_path):
                        print(f"检测到 {file_path} 是压缩文件，跳过该文件。")
                        continue

                    output_7z = os.path.join(root, f"{os.path.splitext(file)[0]}.7z")

                    try:
                        with py7zr.SevenZipFile(output_7z, 'w', filters=[{'id': py7zr.FILTER_LZMA2, 'preset': 9}]) as archive:
                            arcname = os.path.relpath(file_path, directory_path)
                            write_name = arcname.split("\\")[-1]
                            archive.write(file_path, write_name)
                            print(f"{file_path} 已压缩至 {output_7z}")

                        os.remove(file_path)
                        print(f"已删除 {file_path}")

                    except PermissionError:
                        self.update_status(f"权限不足，无法压缩或删除 {file_path}")
                        return
                    except Exception as e:
                        self.update_status(f"处理文件 {file_path} 时发生错误: {e}")
                        return
                    finally:
                        self.processed_files += 1
                        self.update_progress()

            self.update_status("所有文件已成功逐个压缩并删除源文件")
            self.update_progress()  # 确保最后再更新一次进度

        except Exception as e:
            self.update_status(f"发生错误: {e}")

    def update_status(self, text):
        self.status_label.text = text

    def update_progress(self):
        if self.total_files > 0:
            print("total_files is: ",self.total_files)
            progress = (self.processed_files / self.total_files) * 100
            self.progress_bar.value = progress
            self.progress_label.text = f"{int(progress)}%"
        else:
            self.progress_bar.value = 0
            self.progress_label.text = "0%"

def is_archive_file(file_path):
    archive_extensions = ('.zip', '.rar', '.7z', '.tar', '.gz', '.bz2')
    return any(file_path.lower().endswith(ext) for ext in archive_extensions)

if __name__ == '__main__':
    CompressApp().run()
