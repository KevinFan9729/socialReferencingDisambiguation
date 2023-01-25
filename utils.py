# non_pickable= ['person', 'bed','diningtable','cell phone','toilet','suitcase',
# 'oven','sink','refrigerator','chair','tvmonitor', 'laptop', 'mouse','keyboard',
# 'clock', 'tie']

non_pickable= ['person', 'bed','diningtable','toilet','suitcase',
'oven','sink','refrigerator','chair','tvmonitor', 'laptop', 'mouse','keyboard',
'clock', 'tie', 'microwave']

def get_pickable_item_in_view(detected_objs):
    #remove non-pickable objects
    for item in non_pickable:
        detected_objs = list(filter((item).__ne__, detected_objs))
    return detected_objs

def get_non_pickable_item_index(detected_objs):
    #extract indices of all non-pickable objects
    obj_not_to_include = []
    for item in non_pickable:
        obj_not_to_include += [i for i, x in enumerate(detected_objs) if x == item]
    return obj_not_to_include
