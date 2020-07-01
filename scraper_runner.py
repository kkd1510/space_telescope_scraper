import logging

from multiprocessing import Pool, Manager

from scraper.image import download_image
from scraper.text_data import get_text_data

from scraper.images_ids import IMAGES_IDS  # ToDo: Pickle images
from scraper.progress_bar import print_progress_bar

TOTAL_IMAGES = len(IMAGES_IDS)

logging.basicConfig(filename='scrapper_runner.log', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    execution_pool = Pool()
    execution_manager = Manager()
    queue = execution_manager.Queue()

    #ToDo: Argument based execution

    # mapped_func = download_image
    mapped_func = get_text_data

    args = [(image_id, queue) for image_id in IMAGES_IDS]
    all_downloads = execution_pool.map_async(mapped_func, args)

    print_progress_bar(iteration=0, total=TOTAL_IMAGES)
    while not all_downloads.ready():
        size = queue.qsize()
        if size % 100 == 0 or size == TOTAL_IMAGES:
            logger.info(f"Processed {size}.")
        print_progress_bar(iteration=size, total=TOTAL_IMAGES)

    all_downloads.get()
