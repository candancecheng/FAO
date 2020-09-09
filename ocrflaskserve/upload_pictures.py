# coding:utf-8
import os
import sys
import json
import numpy as np
import random
import string
__dir__ = os.path.dirname(os.path.abspath(__file__))
print("__dir__",__dir__)
sys.path.append(__dir__)
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify,Blueprint
from werkzeug.utils import secure_filename
import cv2
import time
from collections import namedtuple
from PaddleOCR.tools.infer.predict_system import Predict
import PaddleOCR.tools.infer.utility as utility
from datetime import timedelta
bp = Blueprint('pre_labeling', __name__,url_prefix="/pre_labeling")
# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)


@bp.route('/upload', methods=['POST', 'GET'])  # 添加路由
def upload():
    if request.method == 'POST':
        f = request.files['file']
        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})
        user_input = request.form.get("name")
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        root_path = os.path.join(basepath,"ImgAndFile")
        if not os.path.exists(root_path):
            os.mkdir(root_path)
        dir_name = DirName(root_path)
        dirpath = os.path.join(root_path, dir_name)
        os.mkdir(dirpath)
        upload_path = os.path.join(dirpath,f.filename)  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
        # 使用Opencv转换一下图片格式和名称
        img = cv2.imread(upload_path)
        cv2.imwrite(upload_path, img)
        # print("utility.parse_args():",utility.parse_args())
        args = {
            "use_gpu": True, "ir_optim": True, "use_tensorrt": False, "gpu_mem": 8000,
            "image": " ",
            "image_dir":"", "det_algorithm": "DB", "det_model_dir": __dir__+"/PaddleOCR/inference/ch_det_mv3_db", "det_max_side_len": 960,
            "det_db_thresh": 0.3, "det_db_box_thresh": 0.5, "det_db_unclip_ratio": 2.0, "det_east_score_thresh": 0.8, "det_east_cover_thresh": 0.1,
            "det_east_nms_thresh": 0.2, "rec_algorithm": 'CRNN', "rec_model_dir": __dir__+"/PaddleOCR/inference/ch_rec_mv3_crnn", "rec_image_shape": "3, 32, 320",
            "rec_char_type": "ch", "rec_batch_num": 30, "rec_char_dict_path": __dir__+"/PaddleOCR/ppocr/utils/ppocr_keys_v1.txt", "use_space_char": True, "enable_mkldnn": False}
        args = DottableDict(args)
        json_path = Predict(upload_path, args)
        new_json_file = ChangeJson(json_path)
        with open(new_json_file, "r") as jsonfile:
            jf = json.load(jsonfile)
        return jsonify(jf)
        # return new_json_file,200,{"ContentType":"application/json"}
    return render_template('upload.html')


class DottableDict(dict):
  def __init__(self, *args, **kwargs):
    dict.__init__(self, *args, **kwargs)
    self.__dict__ = self
  def allowDotting(self, state=True):
    if state:
      self.__dict__ = self
    else:
      self.__dict__ = dict()
class MyEncoder(json.JSONEncoder):
  def default(self, obj):
      if isinstance(obj, np.integer):
          return int(obj)
      elif isinstance(obj, np.floating):
          return float(obj)
      elif isinstance(obj, np.ndarray):
          return obj.tolist()
      else:
          return super(MyEncoder, self).default(obj)
template_dict = {
    "code": 0,
    "message": "",
    "result": {
        "annotations":[{
            "content":None,
            "shape":{
                "shape_category":"polygon",
                "points":[]
            }
        }]
    },
}
def DirName(dirpath):
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    name_list = os.listdir(dirpath)
    if ran_str in name_list:
        DirName(dirpath)
    else:
        return ran_str
def ChangeJson(json_path):
    with open(json_path, "r",encoding="utf-8") as jsonfile:
        jf = json.load(jsonfile)
    # imgs_path = jf['imagePath']
    sample_dict = dict(template_dict)
    print(sample_dict.keys())
    # print(sample_dict["result"]["annotations"][0]["shape"]["shape_category"])
    shapes = jf['shapes']
    anno = []
    for points in shapes:
        content = points['label']
        point = points['points']
        shape_category = points['shape_type']
        onedata = {"content": content, "shape":{"shape_category":shape_category,"points":point}}
        anno.append(onedata)
    sample_dict['result']["annotations"]= anno
    print("json_path",json_path)
    newname = os.path.basename(json_path).split(".")[0]+"_new"
    ext = os.path.basename(json_path).split(".")[1]
    print('newname',newname, "ext",ext)
    # new_json_path = os.path.join(os.path.dirname(json_path), newname+"."+ext)
    # if not os.path.exists(new_json_path):
    #     os.mkdir(new_json_path)
    jsonfile = os.path.join(os.path.dirname(json_path), newname+"."+ext)
    print('jsonfilename',jsonfile)
    with open(jsonfile, 'w', encoding='utf-8') as file_stream:
        json.dump(sample_dict, file_stream, ensure_ascii=False, indent=4, cls=MyEncoder)
    return jsonfile


