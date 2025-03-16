from utils import format_time, get_color

def extract_gift_data(element):
    """extract the common attributes of gifts and guards"""
    fixed_time = 2 # the time of gift danmaku
    data = {
        'appear_time': float(element.get('ts')),
        'over_time': float(element.get('ts')) + fixed_time,  
        'user': element.get('user'),
        'name': element.get('giftname'),
        'count': int(element.get('giftcount' if element.tag=='gift' else 'count')), 
        'price': element.get('price'),
        'move': 0,
        'height': 0,
        'move_time': -1,
        'disappear_time': -2
    }
    return data

def merge_gifts(giftlist, merge_interval=5):
    """merge the same user, same gift and the time interval is less than 5 seconds"""
    if not giftlist:
        return []

    # sort by the appear time
    giftlist.sort(key=lambda x: (x['appear_time']))
    
    merged = []
    current = giftlist[0].copy()
    
    for gift in giftlist[1:]:
        if (gift['user'] == current['user'] and
            gift['name'] == current['name'] and
            gift['appear_time'] - current['appear_time'] < merge_interval):
            current['count'] += gift['count']
            current['over_time'] = gift['over_time']  # keep the last time
        else:
            merged.append(current)
            current = gift.copy()
    merged.append(current)
    return merged

def adjust_time_conflicts(gifts, max_overlap=5, interval=0.2):
    """
        handle the gift danmaku with the same time, avoid overlapping by interval
    
    Args:
        max_overlap: the max number of the same time gift danmaku
        interval: the interval time
    """
    processed = []
    last_time = -float('inf')
    overlap_count = 0
    
    for gift in sorted(gifts, key=lambda x: x['appear_time']):
        if gift['appear_time'] == last_time:
            overlap_count += 1
            if overlap_count >= max_overlap:
                continue  # discard the gift danmaku with more than 5 conflicts
            delta = interval * overlap_count
        else:
            overlap_count = 0
            delta = 0
            
        adjusted = gift.copy()
        adjusted['appear_time'] += delta
        adjusted['over_time'] += delta
        processed.append(adjusted)
        last_time = gift['appear_time']  # keep the original time for comparison
        
    return processed

def calculate_moves(gifts):
    """calculate the time and position of each gift"""
    # generate the event stream
    events = []
    for idx, gift in enumerate(gifts):
        events.append((gift['appear_time'], 'start', idx))
        events.append((gift['over_time'], 'end', idx))
    events.sort(key=lambda x: (x[0], x[1] == 'start'))  # ensure the end event is processed first
    
    # status tracking
    active = []
    max_layers = 2
    
    for time, event_type, idx in events:
        if event_type == 'start':
            # trigger the move of the existing active item
            for active_idx in active:
                gift = gifts[active_idx]
                gift['move'] += 1
                gift['height'] += 1
                
                # record the key time points
                if gift['move'] == 1:
                    gift['move_time'] = time
                elif gift['move'] == 2:
                    gift['disappear_time'] = time
                    
            # add the new active item
            active.append(idx)
            if len(active) > max_layers:
                # remove the earliest one
                expired = active.pop(0)
                
        else:  # end event
            if idx in active:
                active.remove(idx)
                
    return gifts

def print_gift_2_ass(start_time,end_time,height,gift_user,giftname_out):
    # gift danmakus print to ass
    layer = 0
    style = "message_box"
    
    effect_stay = f"\\pos(100,{height})"
    line = f"Dialogue: {layer},{start_time},{end_time},{style},,0000,0000,0000,,{{{effect_stay}}}{gift_user}{giftname_out}\n"
    return line

def generate_ass_line(gift, resolution_y, font_size):
    """generate a single ASS line"""
   
    appear_time = gift['appear_time']
    over_time = gift['over_time']
    move_time = gift['move_time']
    disappear_time = gift['disappear_time']

    start_time = format_time(appear_time)
    end_time = format_time(over_time)
    mid_time = format_time(move_time)
    dis_time = format_time(disappear_time)

    color_text = get_color(int(gift['price']))[2]
    gift_user = f"{{{color_text}\\b1}}{gift['user']}:{{{color_text}\\b0}}"
    giftname_out = f"{gift['name']} x{gift['count']}"
        
    move_status = gift['move']  # the number of moves
    
    # one move, the upper one disappears earlier
    if move_status == 2:
        line0 = print_gift_2_ass(start_time,mid_time,resolution_y-1*font_size,gift_user,giftname_out)
        line1 = print_gift_2_ass(mid_time,dis_time,resolution_y-2*font_size,gift_user,giftname_out)

        return (line0 + line1)
    # one move, the upper one does not disappear earlier
    elif move_status == 1:
        line0 = print_gift_2_ass(start_time,mid_time,resolution_y-1*font_size,gift_user,giftname_out)
        line1 = print_gift_2_ass(mid_time,end_time,resolution_y-2*font_size,gift_user,giftname_out)
        return (line0 + line1)
    # one move
    elif move_status == 0:
        line = print_gift_2_ass(start_time,end_time,resolution_y-1*font_size,gift_user,giftname_out)
        return line
