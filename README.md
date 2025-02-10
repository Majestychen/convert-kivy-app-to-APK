# convert-kivy-app-to-APK
Converts your kivy app into an APK to install in android.
将您的kivy应用程序复制到APK中以安装在Android中。

1. fork my repo (click the fork button)
1. 分叉我的仓库（单击分叉按钮）   
2. upload your main.py to the forked repo (python file MUST BE NAMED "main.py") otherwise, you will get an error
2. 将您的main.py上传到forked repo（Python文件必须命名为“main.py”），否则您将收到错误
3. Cancel, and delete the first workflow run under the actions tab
3. 取消并删除在操作(actions)选项卡下运行的第一个工作流
4. remember to modify/change lines 4, 7, 10, 16, 40, 47, 50, 54, 77, 98, 104(IF NEEDED), and 286 
4. 请记住修改/更改第4、7、10、16、40、47、50、54、77、98、104（如果需要）和286行
5. go to the actions tab
5. 转到操作(actions)选项卡
6. click on the only action (there should be only 1)
6. 单击唯一操作(action)（应该只有1个）
7. click on "Build"
7. 点击“构建”("Build")
8. wait untill the green check comes near the word "build"
8. 等到绿色检查接近“构建”一词
9. click on "summary"
9. 点击“摘要”("summary")
10. click on "package"
10. 点击“包裹”("package")
11. download the zip file
11. 下载zip文件
12. extract the zip file
12. 解压缩zip文件
13. you should get your apk!!!!!!!!
13. 你应该得到你的apk！
14. (If you would also like an .aab file, UNCOMMENT line 308, in the buildozer.spec file)
14. (如果您还需要buildozer.spec文件中的.aab文件，取消第308行的注释）
15. (IF YOU GET AN ERROR DURING THE ACTION, DONT HESATATE TO POST AN ISSUE!!!!!!!!)
15. (如果您在操作过程中出错，不要犹豫，去‘https://github.com/snuq/Snu-Photo-Manager/issues’提交问题！！）

 **THANK YOU TO NOVFENSEC FOR THE BUILD.YML FILE**
感谢您为NovFenSEC提供Build.YML文件
