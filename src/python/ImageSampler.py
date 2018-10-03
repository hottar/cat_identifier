#!/usr/bin/python
# -*- coding: UTF-8 -*-

from google_images_download import google_images_download  # importing library


class ImageSampler(object):

    def __init__(self, keyword):
        self.keyword = keyword

        response = google_images_download.googleimagesdownload()  # class declaration

        arguments = {  # json format to search google image
            "keywords": self.keyword,
            "limit": 100,
            "format": "png"
        }

        paths = response.download(arguments)  # running library
        print(paths)  # printing paths of downloaded images


if __name__ == 'main':
    sampler = ImageSampler("cat")

# sum = lambda arg1, arg2: arg1 + arg2;
