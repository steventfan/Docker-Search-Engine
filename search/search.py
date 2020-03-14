from multiprocessing import Process, Manager
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import json
import re

SITE_URL = 'https://old.reddit.com/'
REQUEST_AGENT = 'Mozilla/5.0 Chrome/47.0.2526.106 Safari/537.36'

def createSoup(url):
    return BeautifulSoup(requests.get(url, headers={'User-Agent':REQUEST_AGENT}).text, 'lxml')

def getSearchResults(searchUrl):
    posts = []
    while True:
        resultPage = createSoup(searchUrl)
        posts += resultPage.findAll('div', {'class':'search-result-link'})
        footer = resultPage.findAll('a', {'rel':'nofollow next'})
        if footer:
            searchUrl = footer[-1]['href']
        else:
            return posts

def parseComments(commentsUrl):
    commentTree = {}
    commentsPage = createSoup(commentsUrl)
    commentsDiv = commentsPage.find('div', {'class':'sitetable nestedlisting'})
    comments = commentsDiv.findAll('div', {'data-type':'comment'})
    for comment in comments:
        numReplies = int(comment['data-replies'])
        tagline = comment.find('p', {'class':'tagline'})
        author = tagline.find('a', {'class':'author'})
        author = "[deleted]" if author == None else author.text
        date = tagline.find('time')['datetime']
        date = datetime.strptime(date[:19], '%Y-%m-%dT%H:%M:%S')
        commentId = comment.find('p', {'class':'parent'}).find('a')['name']
        content = comment.find('div', {'class':'md'}).text.replace('\n','')
        score = comment.find('span', {'class':'score unvoted'})
        score = 0 if score == None else int(re.match(r'[+-]?\d+', score.text).group(0))
        parent = comment.find('a', {'data-event-action':'parent'})
        parentId = parent['href'][1:] if parent != None else '       '
        parentId = '       ' if parentId == commentId else parentId
        commentTree[commentId] = {'author':author, 'reply-to':parentId, 'text':content,
                                  'score':score, 'num-replies':numReplies, 'date':str(date)}
    return commentTree

def parsePost(post, results):
    time = post.find('time')['datetime']
    date = datetime.strptime(time[:19], '%Y-%m-%dT%H:%M:%S')
    title = post.find('a', {'class':'search-title'}).text
    score = post.find('span', {'class':'search-score'}).text
    score = int(re.match(r'[+-]?\d+', score).group(0))
    author = post.find('a', {'class':'author'}).text
    subreddit = post.find('a', {'class':'search-subreddit-link'}).text
    commentsTag = post.find('a', {'class':'search-comments'})
    url = commentsTag['href']
    numComments = int(re.match(r'\d+', commentsTag.text).group(0))
    commentTree = {} if numComments == 0 else parseComments(url)
    results.append({'title':title, 'url':url, 'date':str(date), 'score':score,
                    'author':author, 'subreddit':subreddit, 'comments':commentTree})

def search(keyword, subreddit):
    if subreddit == None or subreddit == '':
        searchUrl = SITE_URL + 'search?q="' + keyword + '"'
    else:
        searchUrl = SITE_URL + 'r/' + subreddit + '/search?q="' + keyword + '"&restrict_sr=on'
    searchUrl += '&t=' + 'day'

    product = {}
    print('Search URL:', searchUrl)
    posts = getSearchResults(searchUrl)
    print('Started scraping', len(posts), 'posts.')
    product[keyword] = {}
    product[keyword]['subreddit'] = 'all' if subreddit == None or subreddit == '' else subreddit
    results = Manager().list()
    jobs = []
    for (post, i) in zip(posts, range(100)):
        job = Process(target=parsePost, args=(post, results))
        jobs.append(job)
        job.start()
    for job in jobs:
        job.join()
    product[keyword]['posts'] = list(results)

    return product
