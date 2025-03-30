# Copyright (c) 2025 DanmakuConvert

# from .danmaku_array import DanmakuArray
# from ..utils import format_time, get_str_len, remove_emojis
def draw_ass_header(ass_file, resolution_x, resolution_y, font_size, sc_font_size):
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
Style: message_box,Microsoft YaHei,{sc_font_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H1E6A5149,0,0,0,0,100.00,100.00,0.00,0.00,1,0.0,0.7,7,0,0,0,1
Style: price,Microsoft YaHei,{int(sc_font_size * 0.7)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H1E6A5149,0,0,0,0,100.00,100.00,0.00,0.00,1,0.0,0.7,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(ass_file, "w", encoding="utf-8") as f:
        f.write(ass_header)

def format_time(seconds):
    """Convert seconds to ASS time format (H:MM:SS.cc)"""
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    centiseconds = int((seconds % 1) * 100)
    seconds = int(seconds)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

max_rows = 7
video_end_time = 100

class Danmaku:
    text: str
    appear_time: float   # 出现时间（秒）
    current_row: int = 0 # 最下是1，逐渐上升
    user : str
    disappear_time: float = None
    
    def __init__(self, text, appear_time):
        self.text = text
        self.appear_time = appear_time
class Move:
    text: str
    start_time: float
    end_time: float
    row: int


def record_move(dm,start_time,end_time,row):
    move = Move()
    move.text = dm.text
    move.start_time = start_time
    move.end_time = end_time
    move.row = row
    return move

dm_list = []
dm_list.append(Danmaku("hello", 10.0))
dm_list.append(Danmaku("world", 11.0))
dm_list.append(Danmaku("!!!!!", 12.0))
dm_list.append(Danmaku("123", 13.0))
dm_list.append(Danmaku("456", 14.0))
dm_list.append(Danmaku("123", 25.0))
dm_list.append(Danmaku("456", 30.0))
dm_list.append(Danmaku("789", 35.0))
dm_list.append(Danmaku("abc", 40.0))
dm_list.append(Danmaku("def", 45.0))
dm_list.append(Danmaku("ghi", 50.0))
dm_list.append(Danmaku("jkl", 55.0))
dm_list.append(Danmaku("mno", 60.0))
dm_list.append(Danmaku("pqr", 65.0))
dm_list.append(Danmaku("stu", 70.0))
dm_list.append(Danmaku("vwx", 75.0))
dm_list.append(Danmaku("yzz", 80.0))


def cal_move(dm_list): 
    # dm_list = sorted(raw)

    #for d in dm_list:
    #     print(d.text, d.appear_time)

    recorded_move = []
    active_danmaku = []


    # 第一次到达顶格的弹幕出错了，需要处理
    last_time = 0
    for dm in dm_list:
        # 处理在屏幕上停留的弹幕的移动
        for i in range(len(active_danmaku)-1,-1,-1) : # 倒序遍历，避免remove操作影响遍历
            """
            这里的remove操作会导致索引变化，进而影响for循环的遍历，会跳过当前元素
            AI说逆序可以解决这个问题
            反正我是不懂
            """
            d = active_danmaku[i]
            if d.current_row == max_rows: # 这个地方没想好用行高判断还是list长度判断
                active_danmaku.remove(d)
                # move = record_move(d,last_time,dm.appear_time,d.current_row)
                # recorded_move.append(move)
                # last_time = dm.appear_time
            else :
                d.current_row += 1
                move = record_move(d,last_time,dm.appear_time,d.current_row)
                recorded_move.append(move)
                # last_time = dm.appear_time
        last_time = dm.appear_time
        active_danmaku.append(Danmaku(dm.text,dm.appear_time))
        for d in active_danmaku:
            print(d.text, d.appear_time, d.current_row)
        print("------------------------")

    #for d in active_danmaku:
        # recorded_move.append(record_move(d,d.appear_time,video_end_time,d.current_row))

    # 排序,好观察结果
    sorted_move = sorted(recorded_move, key=lambda x: x.text)

    for m in sorted_move:
        print(m.text, m.start_time, m.end_time, m.row)
    return sorted_move

def draw_move(move, video_width, video_height, font_size):
    lines = ""
    for m in move:
        text = m.text
        start_time = m.start_time
        end_time = m.end_time
        row = m.row
        effect = f"\\pos({0},{video_height-(row)*font_size})"
        start_time = format_time(start_time)
        end_time = format_time(end_time)

        lines += f"Dialogue: {0},{start_time},{end_time},message_box,,0000,0000,0000,,{{{effect}}}{text}\n"
    return lines

def main():
    video_width = 720
    video_height = 1280
    font_size = 38
    

    move = cal_move(dm_list)
    lines = draw_move(move, video_width, video_height, font_size)
    draw_ass_header("dytest.ass", 720, 1280, font_size, font_size)
    with open("dytest.ass", "a", encoding="utf-8") as f:
        f.write(lines)

if __name__ == '__main__':
    main()



