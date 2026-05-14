#!/usr/bin/env python3
"""
MasterGo Layout Processor
把 absoluteBoundingBox JSON 数据转换为 per-frame 局部坐标
用法: python3 process_mastergo.py input.json output.json
"""
import json, sys, re

def process(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 识别顶层 Frame：1024x600，id不含"/"，name含数字编号
    frames = []
    skip_keywords = ['切图', '设计用', '互联切图']
    for node in data:
        bbox = node['bbox']
        if bbox['width'] == 1024 and bbox['height'] == 600 and '/' not in node['id']:
            if any(kw in node['name'] for kw in skip_keywords):
                continue
            frames.append(node)
    
    result = {}
    for frame in frames:
        fx = frame['bbox']['x']
        fy = frame['bbox']['y']
        fw = frame['bbox']['width']
        fh = frame['bbox']['height']
        
        elements = []
        for node in data:
            if node['id'] == frame['id']:
                continue
            nx, ny = node['bbox']['x'], node['bbox']['y']
            nw, nh = node['bbox']['width'], node['bbox']['height']
            
            # 元素中心在Frame范围内
            cx, cy = nx + nw/2, ny + nh/2
            if fx <= cx <= fx + fw and fy <= cy <= fy + fh:
                elements.append({
                    'id': node['id'],
                    'name': node['name'],
                    'left': round(nx - fx, 2),
                    'top': round(ny - fy, 2),
                    'width': round(nw, 2),
                    'height': round(nh, 2)
                })
        
        result[frame['name']] = {
            'frame_id': frame['id'],
            'frame_origin': {'x': fx, 'y': fy},
            'frame_size': {'width': fw, 'height': fh},
            'element_count': len(elements),
            'elements': elements
        }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    total = 0
    for name, info in result.items():
        count = info['element_count']
        total += count
        print(f"  {name}: {count} 个元素")
    print(f"\n共 {len(result)} 个页面, {total} 个元素")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python3 process_mastergo.py input.json output.json")
        sys.exit(1)
    process(sys.argv[1], sys.argv[2])
