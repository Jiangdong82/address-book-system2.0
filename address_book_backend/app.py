# backend/app.py
from flask import Flask, request, jsonify, send_file , make_response
from flask_cors import CORS
from models import db, Group, Contact, ContactInfo
from config import Config
from utils import allowed_file, parse_excel, generate_excel
import os
import urllib

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

# --------------------- 原有接口修改 ---------------------
# 1. 创建联系人（支持多联系方式）
@app.route('/api/contacts', methods=['POST'])
def create_contact():
    data = request.json
    if not data.get('name'):
        return jsonify({'error': '姓名不能为空'}), 400

    # 创建联系人主记录
    contact = Contact(
        name=data.get('name'),
        group_id=data.get('group_id'),
        is_favorite=data.get('is_favorite', False)
    )
    db.session.add(contact)
    db.session.flush()  # 获取contact.id

    # 添加联系方式
    infos = data.get('contact_infos', [])
    for info in infos:
        if info.get('info_type') and info.get('info_value'):
            contact_info = ContactInfo(
                contact_id=contact.id,
                info_type=info['info_type'],
                info_value=info['info_value']
            )
            db.session.add(contact_info)

    db.session.commit()
    return jsonify({'message': '联系人创建成功', 'contact': contact.id}), 201

# 2. 获取单个联系人（包含联系方式）
@app.route('/api/contacts/<int:id>', methods=['GET'])
def get_contact(id):
    contact = Contact.query.get_or_404(id)
    # 序列化联系人数据（包含联系方式）
    contact_data = {
        'id': contact.id,
        'name': contact.name,
        'group_id': contact.group_id,
        'is_favorite': contact.is_favorite,
        'created_at': contact.created_at,
        'group': {
            'id': contact.group.id,
            'name': contact.group.name
        } if contact.group else None,
        'contact_infos': [
            {
                'id': info.id,
                'info_type': info.info_type,
                'info_value': info.info_value
            } for info in contact.contact_infos
        ]
    }
    return jsonify(contact_data)

# 3. 更新联系人（支持多联系方式）
@app.route('/api/contacts/<int:id>', methods=['PUT'])
def update_contact(id):
    contact = Contact.query.get_or_404(id)
    data = request.json

    # 更新主信息
    contact.name = data.get('name', contact.name)
    contact.group_id = data.get('group_id', contact.group_id)
    contact.is_favorite = data.get('is_favorite', contact.is_favorite)

    # 清空原有联系方式（级联删除，也可按需更新）
    ContactInfo.query.filter_by(contact_id=id).delete()
    # 添加新的联系方式
    infos = data.get('contact_infos', [])
    for info in infos:
        if info.get('info_type') and info.get('info_value'):
            contact_info = ContactInfo(
                contact_id=contact.id,
                info_type=info['info_type'],
                info_value=info['info_value']
            )
            db.session.add(contact_info)

    db.session.commit()
    return jsonify({'message': '联系人更新成功'})

# 4. 获取所有联系人（包含联系方式，支持分组筛选和收藏筛选）
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    group_id = request.args.get('group_id')
    is_favorite = request.args.get('is_favorite')  # 'true'/'false' or None

    query = Contact.query.join(Contact.contact_infos).outerjoin(Group)
    if group_id:
        query = query.filter(Contact.group_id == group_id)
    if is_favorite is not None:
        query = query.filter(Contact.is_favorite == (is_favorite == 'true'))

    contacts = query.all()
    # 序列化
    contacts_data = []
    for contact in contacts:
        contacts_data.append({
            'id': contact.id,
            'name': contact.name,
            'group_id': contact.group_id,
            'is_favorite': contact.is_favorite,
            'group': {
                'id': contact.group.id,
                'name': contact.group.name
            } if contact.group else None,
            'contact_infos': [
                {
                    'id': info.id,
                    'info_type': info.info_type,
                    'info_value': info.info_value
                } for info in contact.contact_infos
            ]
        })
    return jsonify(contacts_data)

# --------------------- 新增接口 ---------------------
# 1. 切换联系人收藏状态
@app.route('/api/contacts/<int:id>/favorite', methods=['PATCH'])
def toggle_favorite(id):
    contact = Contact.query.get_or_404(id)
    contact.is_favorite = not contact.is_favorite
    db.session.commit()
    return jsonify({'is_favorite': contact.is_favorite})

# 2. 导出通讯录为Excel
@app.route('/api/contacts/export', methods=['GET'])
def export_contacts():
    contacts = Contact.query.outerjoin(Group).all()
    # 序列化联系人数据（包含分组和联系方式）
    contacts_data = []
    for contact in contacts:
        contacts_data.append({
            'id': contact.id,
            'name': contact.name,
            'group': {
                'id': contact.group.id,
                'name': contact.group.name
            } if contact.group else None,
            'is_favorite': contact.is_favorite,
            'contact_infos': [
                {
                    'info_type': info.info_type,
                    'info_value': info.info_value
                } for info in contact.contact_infos
            ]
        })
    # 生成Excel文件（接收文件路径和文件名）
    file_path, file_name = generate_excel(contacts_data)
    
    # 修复：处理中文文件名下载，使用make_response包装
    response = make_response(send_file(file_path, as_attachment=True))
    # 编码文件名，避免中文乱码
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{urllib.parse.quote(file_name)}"
    return response

# 3. 导入通讯录从Excel
@app.route('/api/contacts/import', methods=['POST'])
def import_contacts():
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名不能为空'}), 400
    if file and allowed_file(file.filename):
        # 保存文件
        filename = os.path.join(Config.UPLOAD_FOLDER, file.filename)
        file.save(filename)
        # 解析Excel
        contacts_data, error = parse_excel(filename)
        if error:
            return jsonify({'error': f'解析Excel失败：{error}'}), 400
        # 批量添加联系人
        for contact_data in contacts_data:
            # 检查分组是否存在（这里简化处理，若分组名称不存在则设为None，可扩展为自动创建分组）
            group_id = contact_data.get('group_id')
            # 若Excel中是分组名称，可添加逻辑：Group.query.filter_by(name=group_name).first()?.id
            contact = Contact(
                name=contact_data['name'],
                group_id=group_id,
                is_favorite=contact_data['is_favorite']
            )
            db.session.add(contact)
            db.session.flush()
            # 添加联系方式
            for info in contact_data['infos']:
                contact_info = ContactInfo(
                    contact_id=contact.id,
                    info_type=info['info_type'],
                    info_value=info['info_value']
                )
                db.session.add(contact_info)
        db.session.commit()
        return jsonify({'message': f'成功导入{len(contacts_data)}个联系人'}), 201
    else:
        return jsonify({'error': '仅支持xlsx和xls格式'}), 400

# 原有分组接口（无修改，保留）
@app.route('/api/groups', methods=['GET'])
def get_groups():
    groups = Group.query.all()
    return jsonify([{'id': g.id, 'name': g.name} for g in groups])

@app.route('/api/groups', methods=['POST'])
def create_group():
    data = request.json
    if not data.get('name'):
        return jsonify({'error': '分组名称不能为空'}), 400
    if Group.query.filter_by(name=data['name']).first():
        return jsonify({'error': '分组已存在'}), 400
    group = Group(name=data['name'])
    db.session.add(group)
    db.session.commit()
    return jsonify({'message': '分组创建成功', 'group': group.id}), 201

# 补充分组更新接口
@app.route('/api/groups/<int:id>', methods=['PUT'])
def update_group(id):
    group = Group.query.get_or_404(id)
    data = request.json
    if not data.get('name'):
        return jsonify({'error': '分组名称不能为空'}), 400
    if Group.query.filter_by(name=data['name']).filter(Group.id != id).first():
        return jsonify({'error': '分组已存在'}), 400
    group.name = data['name']
    db.session.commit()
    return jsonify({'message': '分组更新成功'})

# 补充分组删除接口
@app.route('/api/groups/<int:id>', methods=['DELETE'])
def delete_group(id):
    group = Group.query.get_or_404(id)
    db.session.delete(group)
    db.session.commit()
    return jsonify({'message': '分组删除成功'})

#删除联系人接口（包含级联删除关联的contact_infos）
@app.route('/api/contacts/<int:id>', methods=['DELETE'])
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    # 由于模型中配置了cascade='all, delete-orphan'，删除联系人会自动删除关联的contact_infos
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'message': '联系人删除成功'}), 200

# 运行应用
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建表（首次运行时）
    app.run(debug=True)