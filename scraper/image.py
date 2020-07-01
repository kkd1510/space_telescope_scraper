import requests
import shutil
from bs4 import BeautifulSoup
from urllib import request
import ast
import logging
from os.path import exists
from scraper.images_ids import IMAGES_IDS


URL = "https://www.spacetelescope.org/images/viewall/page"
DOWNLOAD_URL = "https://cdn.spacetelescope.org/archives/images/large"
DOWNLOAD_URL_ORIGINAL = "https://cdn.spacetelescope.org/archives/images/original"
DOWNLOAD_URL_ORIGINAL_2 = "https://www.spacetelescope.org/static/archives/images/original/"

JPG = "jpg"
TIF = "tif"
PAGES = 20

CHOSEN_PATH = TIF
CHOSEN_URL = DOWNLOAD_URL_ORIGINAL_2
ORIGINAL = True

LOG_FILENAME = f"image_scraper_{CHOSEN_PATH}.log"
NOT_FOUND_LOG_FILENAME = f"not_found_images_{CHOSEN_PATH}.log"

logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
logger = logging.getLogger(__name__)
logging_file_handler = logging.FileHandler(LOG_FILENAME)
logger.addHandler(logging_file_handler)


def download_image(args):
    if exists(NOT_FOUND_LOG_FILENAME):
        append_write = 'a'
    else:
        append_write = 'w'

    image_id, queue = args
    extension = CHOSEN_PATH
    current_url = CHOSEN_URL
    url = f"{current_url}/{image_id}.{extension}"
    local_filename = url.split('/')[-1]
    path = "images/large"

    if extension == TIF:
        path = "images/original"

    if extension == JPG and ORIGINAL:
        path = "images/original_jpg"

    full_local_path = f"{path}/{local_filename}"

    if exists(full_local_path):
        queue.put(image_id)
        logger.info(f"{image_id} already downloaded.")
        return None

    with requests.get(url, stream=True) as r:
        if r.status_code == 404:
            queue.put(image_id)
            with open(NOT_FOUND_LOG_FILENAME, append_write) as not_found_file:
                not_found_file.write(f"{image_id}\n")
            logger.info(f"{image_id} not found / available.")
            return None
        with open(full_local_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    queue.put(image_id)
    return local_filename


def get_images_over_pages(pages):
    all_images_list = []
    for page in range(1, pages + 1):
        url = f"{URL}/{page}/"
        all_images_list.extend(get_images(url))
    print(f"Received {len(all_images_list)} images.")
    return all_images_list


def get_all_ids(images_list):
    return [image_data.get('id') for image_data in images_list]

def save_images_to_cache():
    #ToDo: Pickle images
    print(get_all_ids(get_images_over_pages(PAGES)))

def get_images(url):
    http_obj = request.urlopen(url)
    soup = BeautifulSoup(http_obj, features="html.parser")
    script_str = soup.find_all("script")[0]
    images_lst_str = script_str.text.split("=", 1)[1].strip()
    images_lst_str = images_lst_str.replace('\r', '').replace('\n', '').replace('        ', '')
    images_lst_str = images_lst_str.replace("id:", "'id':")
    images_lst_str = images_lst_str.replace("title:", "'title':")
    images_lst_str = images_lst_str.replace("width:", "'width':")
    images_lst_str = images_lst_str.replace("height:", "'height':")
    images_lst_str = images_lst_str.replace("src:", "'src':")
    images_lst_str = images_lst_str.replace("url:", "'url':")
    images_lst_str = images_lst_str.replace("potw:", "'potw':")
    clean_images_lst = images_lst_str[:-6] + "]"
    images_list = ast.literal_eval(clean_images_lst)
    return images_list



