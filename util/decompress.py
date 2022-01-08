import os
import shutil
import subprocess
from util.zipfile import ZipFile

# 文件类型选择
file_flag = ".zip"


# 删除已解压过的文件
# 一定要先测试，不然很麻烦
def del_old_zip(file_path):
    os.remove(file_path)

_7ZIP = "util/7zip/7z.exe"
def unzip_with_7zip(file_path, destiny):
    if os.path.exists(_7ZIP):
        print("= USANDO 7ZIP =")
        #t = threading.Thread(target=subprocess.run, args=("%s x %s -y -o%s" % (_7ZIP, file_path, destiny),))
        #t.start()
        try:
            subprocess.run("%s x %s -y -o%s" % (_7ZIP, file_path, destiny), shell=False)
        except:
            return False, ""
        else:
            with ZipFile(f'{file_path}', 'r') as z:
                for names in z.namelist():
                    if names.endswith(".html"):
                        # os.rename(os.path.join(file_path, names), os.path.join(file_path, "webpage.html"))
                        return True, names
                #
    else:
        print("= USANDO LIB NATIVA =")
        zip_decompress(file_path, destiny)

# 解压
def zip_decompress(file_path, root="delete/"):
    # 开始
    # zipfile打开zip文件
    try:
        with ZipFile(f'{file_path}', 'r') as z:

            # 解压
            z.extractall(path=f"{root}")  # path为解压路径，解包后位于该路径下

            for names in z.namelist():
                if names.endswith(".html"):
                    #os.rename(os.path.join(file_path, names), os.path.join(file_path, "webpage.html"))
                    return True, "webmail.html"
    except:
        return False, ""

#zip_decompress("C:\\Users\\Javier\\AppData\\Local\\yoogle\\cache\\5a11a975516bdd5319f3c2fb713ee4b4\\webpage.zip")

def start_dir_make(root, dirname):
    os.chdir(root)
    os.mkdir(dirname)
    return os.path.join(root, dirname)


# 去除多余文件夹
def rem_dir_extra(root, father_dir_name):
    # 递归要注意信息的正常处理  搞不好上一个调用已经改变了东西  而下面的调用还是使用之前的数据

    try:

        # 判断文件夹重名  开始
        for item in os.listdir(os.path.join(root, father_dir_name)):

            # 第一步判断是不是一个文件夹，如果不是则跳过本次循环
            if not os.path.isdir(os.path.join(root, father_dir_name, item)):
                continue

            # 判断是否要脱掉一层目录结构
            # 文件夹名字要相同，且子目录中只有单独的一个文件夹
            if item == father_dir_name and len(
                    os.listdir(os.path.join(root, father_dir_name))) == 1:

                # 改变工作目录
                os.chdir(root)

                # 将无用文件夹重命名，因为直接移动会有重名错误
                os.rename(father_dir_name, father_dir_name + '-old')

                # 移动文件后删除空文件夹
                shutil.move(os.path.join(root, father_dir_name + '-old', item), os.path.join(root))
                os.rmdir(os.path.join(root, father_dir_name + '-old'))

                # 将去掉一层目录结构后的文件夹继续作为父本递归处理下去
                # 这里要注意，上面已经发生过数据的改动，所以下面递归传参一定要正确！
                rem_dir_extra(root, item)

            else:

                # 处理那些不满足上面条件的文件夹
                rem_dir_extra(os.path.join(root, father_dir_name), item)

    except Exception as e:

        # 打印错误信息
        print("清除文件夹出错" + str(e))
