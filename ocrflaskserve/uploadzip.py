import os
import uuid
import shutil
import zipfile
from flask import Flask, render_template, request

# from werkzeug.datastructures import FileStorage

app = Flask(__name__)

UploadZip_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def unzip_file(zip_src, dst_dir):
    """
    解压zip文件
    :param zip_src: zip文件的全路径
    :param dst_dir: 要解压到的目的文件夹
    :return:
    """
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, "r")
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        return "请上传zip类型压缩文件"


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    obj = request.files.get("file")
    print(obj)  # <FileStorage: "test.zip" ("application/x-zip-compressed")>
    print(obj.filename)  # test.zip
    print(obj.stream)  # <tempfile.SpooledTemporaryFile object at 0x0000000004135160>
    # 检查上传文件的后缀名是否为zip
    ret_list = obj.filename.rsplit(".", maxsplit=1)
    if len(ret_list) != 2:
        return "请上传zip类型压缩文件"
    if ret_list[1] != "zip":
        return "请上传zip类型压缩文件"

    # 方式一：直接保存文件
    obj.save(os.path.join(UploadZip_BASE_DIR, "files", obj.filename))

    # 方式二：保存解压后的文件（原压缩文件不保存）
    target_path = os.path.join(UploadZip_BASE_DIR, "files", str(uuid.uuid4()))
    shutil._unpack_zipfile(obj.stream, target_path)

    # 方式三：先保存压缩文件到本地，再对其进行解压，然后删除压缩文件
    file_path = os.path.join(UploadZip_BASE_DIR, "files", obj.filename)  # 上传的文件保存到的路径
    obj.save(file_path)
    target_path = os.path.join(UploadZip_BASE_DIR, "files", str(uuid.uuid4()))  # 解压后的文件保存到的路径
    ret = unzip_file(file_path, target_path)
    os.remove(file_path)  # 删除文件
    if ret:
        return ret

    return "上传成功"


if __name__ == "__main__":
    app.run()