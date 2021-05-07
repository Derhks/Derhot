import os
import requests
import tweepy

from bs4 import BeautifulSoup
from flask import Flask
from os import remove
from os.path import isfile
from requests import get
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env


app = Flask(__name__)


def get_image(images: int) -> None:
    headers = {"User-Agent": os.environ['USER_AGENT']}

    if isfile("/tmp/imagen.jpg"):
        return

    try:
        res = get(os.environ['URL'], headers=headers)

        soup = BeautifulSoup(res.text, 'html.parser')
        img_tags = soup.find_all('img')

        urls = [img['src'] for img in img_tags]
        url_images = []

        for url in urls:
            'statics.memondo' not in url or url_images.append(url)

        res = get(url_images[images])
        file = open("/tmp/imagen.jpg", "wb")
        file.write(res.content)
        file.close()
        res.raise_for_status()

    except requests.exceptions.HTTPError as error:
        raise error


def post_tweet() -> bool:
    # Authenticate to Twitter
    consumer_key = os.environ['CONSUMER_KEY']
    consumer_secret = os.environ['CONSUMER_SECRET']
    access_token = os.environ['ACCESS_TOKEN']
    access_token_secret = os.environ['ACCESS_TOKEN_SECRET']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    msg = os.environ['MESSAGE']

    if isfile("/tmp/imagen.jpg"):
        try:
            api.update_with_media("/tmp/imagen.jpg", msg)
            remove("/tmp/imagen.jpg")

        except tweepy.error.TweepError as Err:
            remove("/tmp/imagen.jpg")
            print(Err)

            return False

    return True


@app.route('/')
def hello_world():
    get_image(images=1)

    if post_tweet() is not True:
        get_image(images=2)
        post_tweet()
    else:
        post_tweet()

    return 'The meme has been published'


if __name__ == '__main__':
    app.run()
