# Need more info? Check out the blogpost:
# how-to-make-a-bot-that-automatically-replies-to-comments-on-facebook-post

"""
NEED MORE INFO? CHECK OUT THE BLOGPOST
https://thegrowthrevolution.com/how-to-make-a-bot-that-automatically-replies-to-comments-on-facebook-post
"""

import sqlite3
from time import sleep
import facebook
from PIL import Image
from io import BytesIO
import os, random


APP_ID = ''
APP_SECRET = ''

PAGE_ID = ''
POST_ID_TO_MONITOR = ''
LONG_LIVED_ACCESS_TOKEN = ''

COMBINED_POST_ID_TO_MONITOR = '%s_%s' % (PAGE_ID, POST_ID_TO_MONITOR)
	
def get_random_image():
    file = random.choice(os.listdir("images"))
    im = Image.open("images/" + file)
    bytes_array = BytesIO()
    im.save(bytes_array, format='PNG')
    bytes_array = bytes_array.getvalue()
    return bytes_array

def comment_on_comment(graph, comment):
    comment_id = comment['id']
    
    comment_message = comment['message']
    profile = None

    print("Let's comment!")
    graph.put_like(object_id=comment_id)

    photo_to_post = get_random_image()

    posted_photo = graph.put_photo(
        image=photo_to_post,
        album_path='307245273147646/photos',
        no_story=True,
        published=False
    )

    graph.put_object(parent_object=comment_id, connection_name='comments', message='Hola copain. Hier is uwe foto, mijn gedacht!', attachment_id=posted_photo['id'])

    print('Posted a photo')


def monitor_fb_comments():
    graph = facebook.GraphAPI(LONG_LIVED_ACCESS_TOKEN)

    while True:
        print('I spy with my little eye...🕵️ ')
        sleep(5)

        comments = graph.get_connections(COMBINED_POST_ID_TO_MONITOR,
                                         'comments',
                                         order='chronological')

        for comment in comments['data']:
            if not Posts().get(comment['id']):
                comment_on_comment(graph, comment)

                Posts().add(comment['id'])

        while 'paging' in comments:
            comments = graph.get_connections(COMBINED_POST_ID_TO_MONITOR,
                                             'comments',
                                             after=comments['paging']['cursors']['after'],
                                             order='chronological')

            for comment in comments['data']:

                if not Posts().get(comment['id']):
                    comment_on_comment(graph, comment)
                    Posts().add(comment['id'])

class Posts:
    def __init__(self):
        self.connection = sqlite3.connect('comments.sqlite3')
        self.cursor = self.connection.cursor()

    def get(self, id):
        self.cursor.execute("SELECT * FROM comments where id='%s'" % id)

        row = self.cursor.fetchone()

        return row

    def add(self, id):
        try:
            self.cursor.execute("INSERT INTO comments VALUES('%s')" % id)
            lid = self.cursor.lastrowid
            self.connection.commit()
            return lid
        except sqlite3.IntegrityError:
            return False

if __name__ == '__main__':
    monitor_fb_comments()
