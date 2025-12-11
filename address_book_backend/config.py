# backend/config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:jxs20051005@localhost:3306/contact_book'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')  # 导入Excel的临时目录
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}  # 允许的Excel格式

# 创建上传目录
if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)