import re
import xml.etree.ElementTree as ET
from datetime import datetime
from danmaku_array import DanmakuArray

def format_time(seconds):
    """Convert seconds to ASS time format (H:MM:SS.cc)"""
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    centiseconds = int((seconds % 1) * 100)
    seconds = int(seconds)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

def is_utf8(s):
    try:
        s.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

def getStrLen(s, fontSizeSet):
    if s is None:
        return -1

    if isinstance(s, bytes):
        str_bytes = s
    else:
        str_bytes = s.encode('utf-8')

    if is_utf8(str_bytes):
        cnt = 0
        index = 0
        while index < len(str_bytes):
            byte = str_bytes[index]
            if byte >= 0xC0:
                cnt += 1
            elif byte < 0x80:
                cnt += 1
            index += 1
    else:
        cnt = len(str_bytes)

    len_result = cnt * int((fontSizeSet) / 1.2)
    return len_result

def get_position_y(font_size, appear_time, text_length, resolution_x, roll_time, array):
    velocity = (text_length + resolution_x) / roll_time
    best_row = 0
    best_bias = float('-inf')
    for i in range(array.rows):
        previous_appear_time = array.get_time(i)
        if previous_appear_time == 0:
            array.set_time_length(i, appear_time, text_length)
            return 1 + i * font_size
        previous_length = array.get_length(i)
        previous_velocity = (previous_length + resolution_x) / roll_time
        delta_velocity = velocity - previous_velocity
        # abs_velocity = abs(delta_velocity)
        # The initial difference length
        delta_x = (appear_time - previous_appear_time) * previous_velocity - (previous_length + text_length) / 2
        # If the initial difference length is negative, which means overlapped. Skip.
        if delta_x < 0:
            continue
        if delta_velocity <= 0:
            array.set_time_length(i, appear_time, text_length)
            return 1 + i * font_size
        delta_time = delta_x / delta_velocity
        bias = appear_time - previous_appear_time - delta_time
        if bias > 0:
            array.set_time_length(i, appear_time, text_length)
            return 1 + i * font_size
        else:
            if bias > best_bias:
                best_bias = bias
                best_row = i
    return 1 + best_row * font_size
            


def convert_xml_to_ass(font_size, resolution_x, resolution_y, xml_file, ass_file, array):
    # Parse XML
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Write ASS header
    ass_header = f"""[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayResX: {resolution_x}
PlayResY: {resolution_y}
Timer: 100.0000
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding

Style: R2L,Microsoft YaHei,{font_size},&H4BFFFFFF,&H00FFFFFF,&H00000000,&H1E6A5149,0,0,0,0,100.00,100.00,0.00,0.00,1,0.0,1.0,8,0,0,0,1
Style: L2R,Microsoft YaHei,{font_size},&H4BFFFFFF,&H00FFFFFF,&H00000000,&H1E6A5149,0,0,0,0,100.00,100.00,0.00,0.00,1,0.0,1.0,8,0,0,0,1
Style: TOP,Microsoft YaHei,{font_size},&H4BFFFFFF,&H00FFFFFF,&H00000000,&H1E6A5149,0,0,0,0,100.00,100.00,0.00,0.00,1,0.0,1.0,8,0,0,0,1
Style: BTM,Microsoft YaHei,{font_size},&H4BFFFFFF,&H00FFFFFF,&H00000000,&H1E6A5149,0,0,0,0,100.00,100.00,0.00,0.00,1,0.0,1.0,8,0,0,0,1
Style: SP,Microsoft YaHei,{font_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H1E6A5149,0,0,0,0,100.00,100.00,0.00,0.00,1,0.0,1.0,7,0,0,0,1
Style: message_box,Microsoft YaHei,{font_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H1E6A5149,0,0,0,0,100.00,100.00,0.00,0.00,1,0.0,0.7,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    with open(ass_file, 'w', encoding='utf-8') as f:
        f.write(ass_header)
        
        # Convert each danmaku
        for d in root.findall('.//d'):
            # Parse attributes
            p_attrs = d.get('p').split(',')
            appear_time = float(p_attrs[0])
            danmaku_type = int(p_attrs[1])

            # Convert color from decimal to hex
            color = int(p_attrs[3])
            color_hex = hex(color)
            color_reverse = ''.join(reversed([color_hex[i:i+2] for i in range(0, len(color_hex), 2)]))
            # Remove 0x
            color_hex = color_reverse[:-2].ljust(6, '0').upper()
            color_text = f"\\c&H{color_hex}"
            
            roll_time = 12

            # Format times
            start_time = format_time(appear_time)
            end_time = format_time(appear_time + roll_time) # Display for 12 seconds
            
            # Format text
            text = d.text
            
            # For rolling danmakus (most common type)
            if danmaku_type == 1:
                text_length = getStrLen(text, 38) # Estimate the length of the text
                x1 = resolution_x + int(text_length / 2)  # Start from right edge
                x2 = -int(text_length / 2)      # End at left edge
                y = get_position_y(font_size, appear_time, text_length, resolution_x, roll_time, array)
                
                line = f"Dialogue: 0,{start_time},{end_time},R2L,,0000,0000,0000,,{{\\move({x1},{y},{x2},{y})}}{{{color_text}}}{text}\n"
                f.write(line)
            elif danmaku_type == 4:
                pass

def main():
    xml_file = "sample.xml"
    ass_file = "converted.ass"
    array = DanmakuArray(720, 1280)
    convert_xml_to_ass(38, 720, 1280, xml_file, ass_file, array)

if __name__ == "__main__":
    main()