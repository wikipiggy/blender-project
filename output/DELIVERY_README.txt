交付文件 / Delivery files

.blend 模型：japanese_contemporary_villa.blend
bpy 脚本：create_villa.py
最终渲染：final_front.png、final_garden.png、final_courtyard.png
过程渲染：progress_front.png、progress_refined.png
参考图：japanese villa.jpg

将整个压缩包解压后，在解压目录运行：
blender -b -t 5 --python-exit-code 1 --python create_villa.py -- --stage final

脚本在名为 output 的文件夹内运行时，将结果写入当前文件夹；否则写入其 output 子文件夹。
