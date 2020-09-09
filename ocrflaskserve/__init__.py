import os
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    # 创建一个flask实例，__name__是当前python模块的名称，应用需要知道在哪里设置路径，__name__是个方便的方法
    # instance_relative_config=True告诉应用配置文件是相对于instance_folder的相对路径
    app = Flask(__name__, instance_relative_config=True)
    # 设置一个应用的缺省配置
    # 秘钥用来保证数据安全
    # DATABASE sqlite数据库文件存放路径
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flasker.sqlite'),
    # )
    if test_config is None:
        # load the instance config,if it exits,when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # add the test config if passedd in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    # 创建一个简单的路由
    @app.route('/hello')
    def hello():
        return 'hello world'


    from . import upload_pictures
    app.register_blueprint(upload_pictures.bp)
    # from . import blog
    # app.register_blueprint(blog.bp)
    # app.add_url_rule('/', endpoint='index')

    return app




