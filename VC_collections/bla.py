import datetime

from VC_collections.Collection import find_catalog_gspread, connect_to_google_drive


def create_date_for_921_933(date_string):
    d = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M")
    return datetime.date.strftime(d, "%y%m")

# df['תאריך הרישום'].apply(create_date_for_921_933)



#
# collection = Collection('Alma', 'Architect', 'POrWe')
#
#
# types= [type(getattr(collection, name)).__name__ for  name in dir(collection) if name[:2] != '__' and name[-2:] != '__']
#
# # pprint.pprint(dict(zip(names, types)))
#
# file_path = collection.digitization_path / "ROS" / (collection.collection_id + "_907.xml")
#
# tree = ET.parse(file_path)
# root = tree.getroot()
#
# print(root)
#
# with open('597.txt', encoding='utf8', ) as f:
#     print(f.readlines())
#
# df = pd.read_csv('597.txt', sep='\t')
# print(df.set_index('סימול אוסף'))

#y = ros_dict['990049469550205171']['907a']
#a = '907a'[3:]

# field2tag = ros_dict[id]
# for id, field2tag in ros_dict.items():
#     words = []
#     for field, tag in field2tag.items():
#         words.append(field[3:] + tag)
#     l = '$$' + '$$'.join(words)
#

client, google_sheet_file_id, google_sheet_file_name = find_catalog_gspread(connect_to_google_drive(), 'גלריות נושאים _ארבעת האשכולות')
print(google_sheet_file_id, google_sheet_file_name)