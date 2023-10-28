import logging
import time
import concurrent.futures
import pyvips
from . import projection
from . import simple_downloader
from collections import deque
from tqdm import tqdm
import gc

class TimeMachine(object):
    dest_img = None
    list_images = deque([])

    def __init__(self, dm_map):
        self._dm_map = dm_map

    def straight_download(self, img_url):
        # download image
        while (1):
            try:
                img_data = simple_downloader.download(img_url, True)

                return img_data
            except Exception as e:
                # prevent skipping tiles which can lead to black spaces on final img
                logging.info(f"Failed with {e}. Trying again...")
                time.sleep(10)

    # tile download and paste to img function
    def download_and_paste_tile(self, x, y, to_tile, from_tile, zoomed_scale, map, t_loc, processed, total_tiles):
        try:
            # get image location & url
            img_rel_path = map.image_url(projection.TileLocation(x, y, t_loc.zoom))
            img_url = self._dm_map.url + img_rel_path

            im = self.straight_download(img_url)

            # open image

            # get tile size
            box = (int(abs(x - from_tile.x) * 128 / zoomed_scale),
                   int((abs(to_tile.y - y) - zoomed_scale) * 128 / zoomed_scale))

            while (1):
                self.list_images.append([box[0] / 128, box[1] / 128, im])
                break
            # logging.info('pasted tile %d of %d @ [%d, %d]', processed, total_tiles, box[0] / 128, box[1] / 128)
        except Exception as e:
            # logging.error('error downloading tile [%d, %d]', x, y)
            logging.error(f'error: {e}')

    def capture_single(self, map, t_loc, size, pause=0.25, num_workers=500):
        from_tile, to_tile = t_loc.make_range(size[0], size[1])
        zoomed_scale = projection.zoomed_scale(t_loc.zoom)

        width, height = (
            abs(to_tile.x - from_tile.x) * 128 / zoomed_scale, abs(to_tile.y - from_tile.y) * 128 / zoomed_scale)
        logging.info('final size in px: [%d, %d]', width, height)

        logging.info('downloading tiles...')
        total_tiles = len(range(from_tile.x, to_tile.x, zoomed_scale)) * len(
            range(from_tile.y, to_tile.y, zoomed_scale))
        processed = 0

        # Use a single tqdm instance to track overall progress
        with tqdm(total=total_tiles, desc="Downloading Tiles", unit="tile") as pbar:
            tile_tasks = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                for y in range(from_tile.y, to_tile.y, zoomed_scale):
                    for x in range(from_tile.x, to_tile.x, zoomed_scale):
                        processed += 1
                        task = executor.submit(self.download_and_paste_tile, x, y, to_tile, from_tile, zoomed_scale,
                                               map,
                                               t_loc, processed, total_tiles)
                        tile_tasks.append(task)
                        pbar.update(1)

                # Wait for all tile tasks to complete
                concurrent.futures.wait(tile_tasks, timeout=None, return_when=concurrent.futures.ALL_COMPLETED)
                logging.info("Tasks complete!")

        logging.info("Sorting...")
        sorted_list = sorted(self.list_images, key=lambda x: (x[1], x[0]))
        logging.info("Sorted!")
        new_list = []

        for im in tqdm(sorted_list, desc="Turning tiles into images", unit="tiles"):
            im[2] = pyvips.Image.new_from_buffer(im[2], "", access='sequential')
            if im[2].bands == 3:
                new_list.append(im[2])
            elif im[2].bands == 4:
                im[2] = im[2][0:3]
                new_list.append(im[2])
        del sorted_list
        gc.collect()

        logging.info("The joining begins...")
        self.dest_img = pyvips.Image.arrayjoin(new_list, across=width / 128)
        logging.info("Joined.")
        del new_list

        return self.dest_img

    def compare_images(self, image1, image2):
        file1data = list(image1.getdata())
        file2data = list(image2.getdata())

        diff = 0
        for i in range(len(file1data)):
            if file1data[i] != file2data[i]:
                diff += 1

        return float(diff) / len(file1data)
