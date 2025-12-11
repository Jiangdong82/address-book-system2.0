# backend/utils.py
import os
from config import Config
from openpyxl import Workbook
import pandas as pd
from datetime import datetime

# 检查文件是否为允许的Excel格式
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# 解析Excel文件为联系人数据
def parse_excel(file_path):
    try:
        # 支持xlsx和xls格式
        if file_path.endswith('.xls'):
            df = pd.read_excel(file_path, engine='xlrd')
        else:
            df = pd.read_excel(file_path, engine='openpyxl')
        
        contacts_data = []
        # 遍历每一行（Excel的列名需包含：姓名、分组、是否收藏、以及各类联系方式）
        for index, row in df.iterrows():
            contact = {
                'name': row.get('姓名', ''),
                'group_id': row.get('分组ID', None),
                'is_favorite': row.get('是否收藏', False) in [True, '是', 'Y', 1],
                'infos': []
            }
            # 提取所有联系方式（排除固定列后的所有列）
            for col in df.columns:
                if col not in ['姓名', '分组ID', '是否收藏'] and pd.notna(row[col]):
                    contact['infos'].append({
                        'info_type': col,
                        'info_value': row[col]
                    })
            if contact['name']:  # 姓名不能为空
                contacts_data.append(contact)
        return contacts_data, None
    except Exception as e:
        return None, str(e)

# 生成Excel文件（导出联系人）
def generate_excel(contacts):
    # 修复：直接创建新的工作簿，不再依赖模板文件
    wb = Workbook()
    ws = wb.active
    ws.title = '通讯录'

    # 第一步：收集所有可能的联系方式类型（用于列名）
    info_types = set()
    for contact in contacts:
        for info in contact['contact_infos']:
            info_types.add(info['info_type'])
    info_types = list(info_types)

    # 写入表头：姓名、分组、是否收藏、[各类联系方式]
    headers = ['姓名', '分组名称', '是否收藏'] + info_types
    ws.append(headers)

    # 写入每一行数据
    for contact in contacts:
        # 初始化行数据
        row_data = {
            '姓名': contact['name'],
            '分组名称': contact['group']['name'] if contact['group'] else '',
            '是否收藏': '是' if contact['is_favorite'] else '否'
        }
        # 填充联系方式
        for info_type in info_types:
            row_data[info_type] = ''
            for info in contact['contact_infos']:
                if info['info_type'] == info_type:
                    row_data[info_type] = info['info_value']
                    break
        # 写入行
        ws.append([row_data[h] for h in headers])

    # 修复：使用时间戳命名，避免中文/特殊字符问题，同时确保路径正确
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f'contact_export_{timestamp}.xlsx'
    file_path = os.path.join(Config.UPLOAD_FOLDER, file_name)
    
    # 保存文件
    wb.save(file_path)
    return file_path, file_name  # 新增返回文件名，用于前端下载时的命名