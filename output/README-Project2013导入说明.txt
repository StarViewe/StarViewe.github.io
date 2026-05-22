文件说明

1. project_plan_for_project2013.xml
用于“4.1 编制项目开发计划表（甘特图）”

2. project_progress_for_project2013.xml
用于“4.2 开发进度跟踪结果（甘特图）”
已预填一组模拟进度百分比，可直接在 Microsoft Project Professional 2013 中打开后截图。

导入方式

1. 打开 Microsoft Project Professional 2013
2. 选择“文件” -> “打开”
3. 文件类型选择 XML
4. 打开上述任一 xml 文件
5. 若弹出导入向导，按默认映射导入即可

本文件特点

1. 基于实验第三部分任务表生成
2. 已包含 4 个功能模块、19 个叶子任务、5 个资源
3. 已体现第四部分要求的多种前置关系：
   FS 结束->开始
   SS 开始->开始
   FF 结束->结束
   SF 开始->结束
4. 已包含正 Lag 与负 Lag（Lead）示例

如需调整项目开始日期、任务进度或任务名称，可修改同目录上级的：
/Users/bytedance/Desktop/Projects/myBlog/tools/generate_project_xml.py
然后重新运行脚本生成。
