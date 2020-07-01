import json
from urllib import request
from bs4 import BeautifulSoup


IMAGE_DATA_FIELDS = ['Id:', 'Type:', 'Release date:', 'Name:', 'Distance:', 'Constellation:', 'Category:']

IMAGE_PUBLICATION_URL = 'https://www.spacetelescope.org/images'
DATA_PATH = 'data'


def save_to_json(image_id, image_data, object_data):
    image_data_file_name = f'{DATA_PATH}/image/{image_id}_i.json'
    object_data_file_name = f'{DATA_PATH}/object/{image_id}_o.json'
    with open(image_data_file_name, "w") as write_file:
        json.dump(image_data, write_file)
    with open(object_data_file_name, "w") as write_file:
        json.dump(object_data, write_file)


def get_text_data(args):
    image_id, queue = args
    url = f"{IMAGE_PUBLICATION_URL}/{image_id}/"
    http_obj = request.urlopen(url)
    soup = BeautifulSoup(http_obj, features="html.parser")
    p_list = soup.find_all('p')
    description = []

    for p in p_list:
        if p.text not in description:
            description.append(p.text)
    description = ' '.join(description)
    tables = soup.find_all('table')

    image_data = {'description': description}
    object_data = {}

    for table_index, table in enumerate(tables):
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            for col_index, col in enumerate(cols):
                field_name = col.text.strip()
                if field_name in IMAGE_DATA_FIELDS:
                    dict_field_name = field_name.replace(':', '').strip()
                    field_value = cols[col_index + 1].text.strip()
                    if table_index == 0:  # Image data
                        if field_name == 'Release date:':
                            field_value = field_value.split(',')[0].strip()
                        image_data[dict_field_name] = field_value
                    elif table_index == 1:  # Object Data
                        object_data[dict_field_name] = field_value

    save_to_json(image_id, image_data, object_data)
    queue.put(image_id)



