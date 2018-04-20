#!/usr/bin/python

import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

import requests
import requests_cache
import json
import re
import numpy as np
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go
import sqlite3 as sqlite


CACHE_FNAME = 'cache_game.json'
CACHE_FNAME2 = 'cache_contents.json'

try:
    f = open(CACHE_FNAME, "r")
    fileread = f.read()
    CACHE_DICT = json.loads(fileread)
    f.close()
except:
    CACHE_DICT = {}

try:
    f2 = open(CACHE_FNAME2, "r")
    fileread2 = f2.read()
    CACHE_DICT2 = json.loads(fileread2)
    f2.close()
except:
    CACHE_DICT2 = {}



# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secret.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
      message=MISSING_CLIENT_SECRETS_MESSAGE,
      scope=YOUTUBE_READ_WRITE_SCOPE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
      flags = argparser.parse_args()
      credentials = run_flow(flow, storage, flags)

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      http=credentials.authorize(httplib2.Http()))

    return youtube


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyA3rvJw4nMNAwLsMQJwGiG54XKkJ6efVM8"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(data):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  videos = {'game_name':[], "videoid":[], "title":[], "description":[], 'publishedat':[]}
  for game in data:
      if game not in CACHE_DICT:
          # print('Creating cache file...')
          search_response = youtube.search().list(
            q=game,
            part="id,snippet",
            maxResults=50
          ).execute()
          CACHE_DICT[game] = search_response
          dumped_json_cache = json.dumps(CACHE_DICT)
          fw=open(CACHE_FNAME,'w')
          fw.write(dumped_json_cache)
          fw.close()
          for search_result in search_response.get("items", []):
              if search_result["id"]["kind"] == "youtube#video":
                  videos['game_name'].append(game)
                  videos['videoid'].append(search_result['id']['videoId'])
                  videos['title'].append(search_result['snippet']['title'])
                  videos['description'].append(search_result['snippet']['description'])
                  videos['publishedat'].append(search_result['snippet']['publishedAt'][0:10])
      else:
          # print("Getting cached data...")
          search_response = CACHE_DICT[game]
          for search_result in search_response.get("items", []):
              if search_result["id"]["kind"] == "youtube#video":
                  videos['game_name'].append(game)
                  videos['videoid'].append(search_result['id']['videoId'])
                  videos['title'].append(search_result['snippet']['title'])
                  videos['description'].append(search_result['snippet']['description'])
                  videos['publishedat'].append(search_result['snippet']['publishedAt'][0:10])
  return videos





def contents_search(words, youtube):
  #youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
#    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  contents = {'videoid':[], 'tags':[], 'duration':[], 'viewcount':[], 'likecount':[], 'dislikecount':[], 'commentcount':[]}
  for i in words['videoid']:
      if i not in CACHE_DICT2:
          print('Creating cache(2) file...')
          search_response = youtube.videos().list(
            part="id,snippet,contentDetails,statistics",
            id=i,
            maxResults=50
          ).execute()

          CACHE_DICT2[i] = search_response
          dumped_json_cache = json.dumps(CACHE_DICT2)
          fw=open(CACHE_FNAME2,'w')
          fw.write(dumped_json_cache)
          fw.close()
          try:
              for search_result in search_response.get("items", []):
                  contents['videoid'].append(search_result['id'])
                  contents['tags'].append(len(search_result['snippet']['tags']))
                  contents['duration'].append(search_result['contentDetails']['duration'])
                  contents['viewcount'].append(search_result['statistics']['viewCount'])
                  contents['likecount'].append(search_result['statistics']['likeCount'])
                  contents['dislikecount'].append(search_result['statistics']['dislikeCount'])
                  contents['commentcount'].append(search_result['statistics']['commentCount'])
          except:
              contents['likecount'].append(0)
              contents['dislikecount'].append(0)
              contents['commentcount'].append(0)
              contents['tags'].append(0)
              contents['duration'].append(0)
              contents['viewcount'].append(0)
      else:
        # print("Getting cached data(2)...")
        search_response = CACHE_DICT2[i]
        try:
            for search_result in search_response.get("items", []):
                contents['videoid'].append(search_result['id'])
                contents['tags'].append(len(search_result['snippet']['tags']))
                contents['duration'].append(search_result['contentDetails']['duration'])
                contents['viewcount'].append(search_result['statistics']['viewCount'])
                contents['likecount'].append(search_result['statistics']['likeCount'])
                contents['dislikecount'].append(search_result['statistics']['dislikeCount'])
                contents['commentcount'].append(search_result['statistics']['commentCount'])
        except:
            contents['likecount'].append(0)
            contents['dislikecount'].append(0)
            contents['commentcount'].append(0)
            contents['tags'].append(0)
            contents['duration'].append(0)
            contents['viewcount'].append(0)


  return contents

# create database
DBNAME = 'youtube_game.db'

def create_search_table(data):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()

    ####### create search table ########
    statement ='''
        DROP TABLE IF EXISTS 'Search' ;
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Search' (
        "videoid" VARCHAR(256) UNIQUE PRIMARY KEY,
        "game_name" VARCHAR(256),
        "title" VARCHAR(256),
        "description" TEXT,
        "publishedat" VARCHAR(8)
        );
    '''
    cur.execute(statement)

    insert_list = []
    for i in range(len(data['game_name'])):
        tmp_list=[]
        tmp_list.append(data['videoid'][i])
        tmp_list.append(data['game_name'][i])
        tmp_list.append(data['title'][i])
        tmp_list.append(data['description'][i])
        tmp_list.append(data['publishedat'][i])
        insert_list.append(tmp_list)


    for item in insert_list :
        insertion =(item[0], item[1], item[2], item[3], item[4])
        statement = '''INSERT INTO Search VALUES (?,?,?,?,?)'''
        cur.execute(statement, insertion)
    conn.commit()
    conn.close()

def create_contents_table(data):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()

    ####### create search table ########
    statement ='''
        DROP TABLE IF EXISTS 'Contents';
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Contents' (
        "videoid" VARCHAR(256),
        "tags" INT,
        "duration" VARCHAR(256),
        "viewcount" INT,
        "likecount" INT,
        "dislikecount" INT,
        "commentcount" INT,
        FOREIGN KEY ("videoid") REFERENCES "Search" ("videoid")
        );
    '''
    cur.execute(statement)


    insert_list = []
    for i in range(len(data['videoid'])):
        tmp_list=[]
        tmp_list.append(data['videoid'][i])
        tmp_list.append(data['tags'][i])
        tmp_list.append(data['duration'][i])
        tmp_list.append(data['viewcount'][i])
        tmp_list.append(data['likecount'][i])
        tmp_list.append(data['dislikecount'][i])
        tmp_list.append(data['commentcount'][i])
        insert_list.append(tmp_list)


    for item in insert_list :
        insertion =(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
        statement = '''INSERT INTO Contents VALUES (?,?,?,?,?,?,?)'''
        cur.execute(statement, insertion)

    statement ='''
        DROP TABLE IF EXISTS 'Combined';
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE Combined AS
        SELECT *
        FROM Search
        INNER JOIN Contents
        ON Search.videoid = Contents.videoid
    '''

    cur.execute(statement)

    conn.commit()
    conn.close()

class Game:

    def __init__(self, name):
        self.name = name
        self.get_stats()

    def get_stats(self):
        DBNAME = 'youtube_game.db'
        conn =sqlite.connect(DBNAME)
        cur = conn.cursor()

        statement = '''
            SELECT game_name, AVG(tags) AT, AVG(viewcount) AV, AVG(likecount) AL, AVG(dislikecount) AD, AVG(commentcount) AC,
            SUM(tags) ST, SUM(viewcount) SV, SUM(likecount) SL, SUM(dislikecount) SD, SUM(commentcount) SC
            FROM Combined GROUP BY game_name HAVING game_name = '''
        statement += '"'
        statement += self.name
        statement += '"'

        cur.execute(statement)
        tuple = cur.fetchone() # list of tuple
        self.AT = round(tuple[1],2)
        self.AV = round(tuple[2],2)
        self.AL = round(tuple[3],2)
        self.AD = round(tuple[4],2)
        self.AC = round(tuple[5],2)
        self.ST = round(tuple[1],2)
        self.SV = round(tuple[2],2)
        self.SL = round(tuple[3],2)
        self.SD = round(tuple[4],2)
        self.SC = round(tuple[5],2)


def plot_viewcount(cl_list):
    x_list = []
    y_list = []
    for i in cl_list:
        x_list.append(i.name)
        y_list.append(i.SV)


    data = [go.Bar(
        x = x_list,
        y = y_list,
        # base = 0,
        marker = dict(
            color = 'blue'
            ),
        name = 'Summary(View Count) ',
        opacity=0.6

        )]
    fig = go.Figure(data=data)
    py.plot(fig)

def plot_like_ratio(game):
    x_list = []
    y_list = []
    x_list.append('like')
    x_list.append('dislike')
    y_list.append(game.SL)
    y_list.append(game.SD)

    data = [go.Pie(
        labels = x_list,
        values = y_list,
        marker = dict(
            # color = 'red',
            line=dict(color='#FFFFFF', width=2)
            ),
        name = 'the ratio of like/dislike',
        )]
    fig = go.Figure(data=data)
    py.plot(fig)

def plot_likes_comments(cl_list):
    x_list = []
    y_list = []
    y2_list = []
    for i in cl_list:
        x_list.append(i.name)
        y_list.append(i.AL)
        y2_list.append(i.AC)

    trace1 = go.Bar(
        x=x_list,
        y=y_list,
        name = 'likes'
    )

    trace2 = go.Bar(
        x=x_list,
        y=y2_list,
        name = 'Comments'
    )
    data = [trace1, trace2]
    layout = go.Layout(barmode='group')

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig)

def plot_commentcount(cl_list):
    x_list = []
    y_list = []
    for i in cl_list:
        y_list.append(i.name)
        x_list.append(i.AC)


    data = [go.Bar(
        x = x_list,
        y = y_list,
        # base = 0,
        marker = dict(
            color = 'red'
            ),
        name = 'Average Comment Count',
        opacity=0.6,
        orientation = 'h'
        )]
    fig = go.Figure(data=data)
    py.plot(fig, filename='horizontal-bar')


def interactive_prompt():
    data = ['overwatch', 'fortnite', 'PUBG', 'hearthstone', 'monster hunter']
    game1 = ''
    game2 = ''
    while game1 != 'exit' and game2 != 'exit':
        print('''
            Choose two games or enter "exit" to quit.
            [overwatch, fortnite, PUBG, hearthstone, monster hunter]
        ''')
        game1 = input('Enter First game: ')
        game2 = input('Enter Second game: ')
        if game1 == 'exit' or game2 == 'exit':
            pass
        elif game1 in data and game2 in data:
            print('Your two games are: {} and {}'.format(game1, game2))
            g1_obj = Game(game1)
            g2_obj = Game(game2)
            print('''
                1  view count
                2  ratio of like:dislike
                3  comparison of likes and Comments
                4  count comments
            ''')
            plotinput = ''
            while plotinput != 'exit':
                if plotinput == 'exit':
                    pass
                else:
                    plotinput = input('choose a number for the plot to see: ')
                    if (plotinput == 'exit'):
                        break
                    elif (plotinput == '1'):
                        plot_viewcount([g1_obj, g2_obj])
                    elif (plotinput == '2'):
                        print('showing plot for the first game...')
                        plot_like_ratio(g1_obj)
                    elif (plotinput == '3'):
                        plot_likes_comments([g1_obj, g2_obj])
                    elif (plotinput == '4'):
                        plot_commentcount([g1_obj, g2_obj])
                    else:
                        print('invalid input')

        else:
            print('Please choose games from the list')



if __name__ == "__main__":
  youtube = get_authenticated_service()

  data = ['overwatch', 'fortnite', 'PUBG', 'hearthstone', 'monster hunter']
  #data = 'overwatch'
  words = youtube_search(data)
  contents = contents_search(words, youtube)
  create_contents_table(contents)

  interactive_prompt()
