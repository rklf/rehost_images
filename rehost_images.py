#!/usr/bin/python
'''
    Allow to replace old hosted images by new hosted images on imgBB (or your own FTP)
'''

import sys
from datetime import datetime
import re
import requests
from PIL import Image

if len(sys.argv) != 2:
    sys.exit("Usage: ./%s <html_file>" % sys.argv[0])


def upload_img(original_img):
    '''
        Allow to host images found in html source code from link in <img src="{link}">
    '''
    try:
        api = "YOUR_API_KEY_HERE"
        url = "https://api.imgbb.com/1/upload?key=" + api
        data = {'image': original_img}
        req = requests.post(url, data)
        json = req.json()
        return json['data']['url']
    except Exception as err:
        print("[x] Error while uploading image: " +
              str(err) + " (" + original_img + ")")
        return None


def is_pixel(original_img):
    '''
        Process to check whether the image is a tracking pixel or not
    '''
    try:
        # ext = (".jpg", ".jpeg", ".png", ".gif")
        pil_img = Image.open(requests.get(original_img, stream=True).raw)
        img_width, img_height = pil_img.size
        if (img_width in {0, 1} and img_height in {0, 1}): # or not original_img.endswith(ext)
            print("[$]\tInfo: Image is a pixel, skipping...")
            return True
        return False
    except Exception as err:
        print("[x] Error while checking image size: " +
              str(err) + " (" + original_img + ")")
        return True


def get_image(img_group):
    '''
        Returning the image found from regex either from "<img ... />" or "backgroung: url(...)"
    '''
    for img in img_group:
        if img is not None:
            return img
    return None


def fillfound():
    '''
        Find and replace images found in html source code
    '''
    html_file = open(sys.argv[1], 'r', encoding='utf-8')
    source_code = html_file.read()
    file_nb = 0
    retry = 0
    max_retry = 10
    pattern = re.compile(
        r'<img \s*.*?src\s*=\s*(?:\'|")(.+?)(?:\'|")|:\s*.*url(?:\(\s*[\'"]?)(.*?)(?:[\'"]?\s*\))',
        flags=re.I)

    for imgs in re.finditer(pattern, str(source_code)):
        real_img = get_image(imgs.groups())
        if is_pixel(real_img) is True:
            continue
        while True:
            try:
                uploaded_img = upload_img(real_img)
                if uploaded_img is None:
                    continue
                source_code = source_code.replace(real_img, uploaded_img)
                print("[*] Image replaced: (%s)" % real_img)
                file_nb += 1
                break
            except IOError:
                print("[x] Connection error, reconnecting... %s of %s" %
                      (retry+1, max_retry))
                retry += 1
                if retry == max_retry:
                    print("[x] Too many retries, program interrupted...")
                    return file_nb
                continue
            except (KeyboardInterrupt, SystemExit):
                print("\n[x] Program Interrupted...")
                return file_nb
            except Exception as err:
                print("[x] Error: " + str(err))
                return file_nb

    with open(sys.argv[1], 'w', encoding='utf-8') as file:
        file.write(source_code)
    html_file.close()

    return file_nb


def main():
    '''
        Main function which process and returns number of images replaced
    '''
    actual_time = datetime.now()
    file_nb = fillfound()
    print("\n[*] Scanning completed, %s image(s) replaced, elapsed time: %s." %
          (file_nb, datetime.now() - actual_time))


if __name__ == "__main__":
    main()
    sys.exit()
