# backend/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 分组模型（原有，无修改）
class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 联系人主表（新增is_favorite字段）
class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 联系人姓名
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)  # 收藏标记
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联分组和联系方式
    group = db.relationship('Group', backref=db.backref('contacts', lazy=True))
    contact_infos = db.relationship('ContactInfo', backref='contact', lazy=True, cascade='all, delete-orphan')

# 联系人多联系方式表（新增）
class ContactInfo(db.Model):
    __tablename__ = 'contact_infos'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    info_type = db.Column(db.String(50), nullable=False)  # 类型：电话、邮箱、微信、地址等
    info_value = db.Column(db.String(255), nullable=False)  # 具体值
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 初始化数据库（新增表）
# 执行 db.create_all() 时会自动创建新表