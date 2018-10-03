#!/usr/bin/python
# -*- coding: UTF-8 -*-

from io import BytesIO
from os import walk

import numpy as np
import requests
import twitter
from PIL import Image


class ImageLoader(object):

    def __init__(self):
        self.img_urls = None

    def browse_image(self, search_term="dog", sample_amount=100):
        subscription_key = None
        # assert subscription_key
        search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
        headers = {"Ocp-Apim-Subscription-Key": subscription_key}
        params = {"q": search_term, "license": "public", "imageType": "photo"}
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()

        search_results = response.json()  # collect search results as json

        self.img_urls = [img["contentUrl"] for img in search_results["value"][:sample_amount]]  # collect direct links.

    def load_image(self, in_file_name, out_type):
        img = Image.open(in_file_name)
        img.load()
        data = np.asarray(img, dtype="int32")
        if out_type == "anArray":
            return data
        if out_type == "aList":
            return list(data)

    # prereq: At least one image file exists under given directory.
    def load_all_image(self, my_path):
        _, _, file_names = next(walk(my_path), (None, None, []))  # Create a list of file names under given directory.

        return file_names

    def download_image(self, url):
        img_data = requests.get(url)  # request for image file
        img_data.raise_for_status()  # check if response is successful
        return self.load_image(BytesIO(img_data.content), "anArray")

    # Saving each image as separate csv files under current directory.
    # Each image is directly accessed through stored set of url.
    def convert_url_csv(self, search_term):
        for url_index in range(len(self.img_urls)):
            file_name = str(search_term) + '_' + str(url_index) + ".csv"
            dataset = self.download_image(self.img_urls[url_index])
            np.savetxt(file_name, dataset, delimiter=",")

    # Executor function of this class.
    # Searches for bing images with given keywords and stores first 100 links as csv.
    def execute(self, search_term):
        self.browse_image(search_term)
        self.convert_url_csv(search_term)


class TweeTrend(object):
    def __init__(self):
        mem = ''

    def mine_trends(self):
        api = twitter.Api()
        trends = api.GetTrendsCurrent(exclude='cat')
        assert trends
        return trends

    def extract_hashtag(self, trends):
        tag_names = [trend['name'][1:] for trend in trends['trends']]  # Store only the name str excluding '#' in front.
        return tag_names


class ImageSampler(object):
    def __init__(self):
        self.search_term = None

    def execute(self, search_term):
        img_loader = ImageLoader()  # Initialize object to download images for sample
        img_loader.execute(search_term)  # Download csv converted images of the main target to classify.

        twitter_trend = TweeTrend()  # Initialize object to fetch the global top 10 trends of the day.
        trends = twitter_trend.mine_trends()  # Get data of top 10 trends as json
        tag_names = twitter_trend.extract_hashtag(trends)  # Create a list with only the name of the trends.

        [img_loader.execute(bad_terms) for bad_terms in tag_names]  # Download csv converted images of bad samples.

        # By end of the execution, there should be 100 good samples and 1000 bad samples stored under directory.


if __name__ == "__main__":
    print('Executing ImageSampler\n')
    sampler = ImageSampler()
    sampler.execute("cat")
    print('done\n')
