#!/usr/bin/env python3

import os
import json
import platform
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

def get_vscode_user_snippets_path():
    """获取不同平台的VSCode用户snippets目录"""
    if platform.system() == 'Windows':
        return Path(os.environ['APPDATA']) / 'Code' / 'User' / 'snippets'
    elif platform.system() == 'Darwin':  # macOS
        return Path.home() / 'Library' / 'Application Support' / 'Code' / 'User' / 'snippets'
    else:  # Linux
        return Path.home() / '.config' / 'Code' / 'User' / 'snippets'

def get_idea_templates_path():
    """获取不同平台的IDEA模板目录"""
    # 注意：这里需要替换<product><version>为实际的产品和版本
    # 例如：IntelliJIdea2023.1
    product_version = "IntelliJIdea2023.1"  # 可以通过配置修改
    
    if platform.system() == 'Windows':
        return Path(os.environ['APPDATA']) / 'JetBrains' / product_version / 'templates'
    elif platform.system() == 'Darwin':
        return Path.home() / 'Library' / 'Application Support' / 'JetBrains' / product_version / 'templates'
    else:  # Linux
        return Path.home() / '.config' / 'JetBrains' / product_version / 'templates'

class Config:
    """配置选项"""
    # IDE类型: 'vscode' | 'idea' | 'both'
    ide_type = 'both'
    # VSCode配置
    vscode = {
        # 选择存放位置: 'workspace' | 'user' | 'project'
        'location': 'project',
        # 文件名
        'filename': 'yaml.code-snippets'
    }
    # IDEA配置
    idea = {
        # 产品版本
        'product_version': 'IntelliJIdea2023.1',
        # 模板组名
        'group_name': 'AutoCoder',
        # 文件名
        'filename': 'AutoCoder.xml'
    }

def get_vscode_snippets_path():
    """获取VSCode snippets文件的完整路径"""
    if Config.vscode['location'] == 'user':
        return get_vscode_user_snippets_path() / Config.vscode['filename']
    elif Config.vscode['location'] == 'workspace':
        return Path('.vscode') / Config.vscode['filename']
    elif Config.vscode['location'] == 'project':
        snippets_dir = Path('.vscodesnippets')
        snippets_dir.mkdir(exist_ok=True)
        return snippets_dir / Config.vscode['filename']
    else:
        raise ValueError('Invalid location specified for VSCode')

def create_vscode_snippets(single_at_symbols, double_at_symbols):
    """创建VSCode snippets配置"""
    return {
        "@Reference": {
            "scope": "yaml",
            "prefix": "@",
            "body": [
                "${1|" + ','.join(item['const'] for item in single_at_symbols['oneOf']) + "|}"
            ],
            "description": "Insert a single @ reference",
            "isFileTemplate": True,
            "includeIf": "autocoder_input.yaml"
        },
        "@@Reference": {
            "scope": "yaml",
            "prefix": "@@",
            "body": [
                "${1|" + ','.join(item['const'] for item in double_at_symbols['oneOf']) + "|}"
            ],
            "description": "Insert a double @@ reference",
            "isFileTemplate": True,
            "includeIf": "autocoder_input.yaml"
        }
    }

def create_idea_template_xml(single_at_symbols, double_at_symbols):
    """创建IDEA Live Templates XML配置"""
    root = ET.Element('templateSet')
    root.set('group', Config.idea['group_name'])

    # 创建单@模板
    template = ET.SubElement(root, 'template')
    template.set('name', 'single_at_ref')
    template.set('value', '@$symbol$')
    template.set('description', 'Insert a single @ reference')
    template.set('toReformat', 'false')
    template.set('toShortenFQNames', 'true')

    variable = ET.SubElement(template, 'variable')
    variable.set('name', 'symbol')
    # 使用enum变量类型来提供选项
    options = [item['const'].replace('@', '') for item in single_at_symbols['oneOf']]
    variable.set('expression', '"' + '||'.join(options) + '"')
    variable.set('defaultValue', options[0] if options else '')

    context = ET.SubElement(template, 'context')
    option = ET.SubElement(context, 'option')
    option.set('name', 'YAML')
    option.set('value', 'true')

    # 创建双@@模板
    template = ET.SubElement(root, 'template')
    template.set('name', 'double_at_ref')
    template.set('value', '@@$symbol$')
    template.set('description', 'Insert a double @@ reference')
    template.set('toReformat', 'false')
    template.set('toShortenFQNames', 'true')

    variable = ET.SubElement(template, 'variable')
    variable.set('name', 'symbol')
    # 使用enum变量类型来提供选项
    options = [item['const'].replace('@@', '') for item in double_at_symbols['oneOf']]
    variable.set('expression', '"' + '||'.join(options) + '"')
    variable.set('defaultValue', options[0] if options else '')

    context = ET.SubElement(template, 'context')
    option = ET.SubElement(context, 'option')
    option.set('name', 'YAML')
    option.set('value', 'true')

    # 格式化XML
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    return xml_str

def update_vscode_snippets(single_at_symbols, double_at_symbols):
    """更新VSCode snippets"""
    snippets = create_vscode_snippets(single_at_symbols, double_at_symbols)
    target_path = get_vscode_snippets_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(snippets, f, indent=4)
    
    print(f"VSCode snippets updated at: {target_path}")

def update_idea_templates(single_at_symbols, double_at_symbols):
    """更新IDEA templates"""
    xml_content = create_idea_template_xml(single_at_symbols, double_at_symbols)
    target_path = get_idea_templates_path() / Config.idea['filename']
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"IDEA templates updated at: {target_path}")

def main():
    try:
        # 读取符号文件
        with open('symbols/single-at-symbols.json', 'r', encoding='utf-8') as f:
            single_at_symbols = json.load(f)
        
        with open('symbols/double-at-symbols.json', 'r', encoding='utf-8') as f:
            double_at_symbols = json.load(f)

        # 根据配置更新不同IDE的snippets
        if Config.ide_type in ['vscode', 'both']:
            update_vscode_snippets(single_at_symbols, double_at_symbols)
            
        if Config.ide_type in ['idea', 'both']:
            update_idea_templates(single_at_symbols, double_at_symbols)

    except Exception as error:
        print(f"Error updating snippets: {error}")

if __name__ == '__main__':
    main() 