import praw
import sys
import re
import string
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from imgurpython import ImgurClient
# import sys
import click
import os
import time
nltk.download('stopwords')
nltk.download('punkt')
import random
import datetime
# url = sys.argv[1]


# subreddit = reddit.subreddit('me_irl')
# bot_phrase = 'i am in boys'

# submission = reddit.submission(url= url)
# print(submission.title)
# print(submission.title)  # Output: the submission's title
# print(submission.score)  # Output: the submission's score
# print(submission.id)     # Output: the submission's ID
# print(submission.url)    # Output: the URL the submission points to
# for top_level_comment in submission.comments:
#     print(top_level_comment.body)

# count = 0
# submission.comments.replace_more(limit=None)
# for comment in submission.comments.list():
#     print(comment.body)
#     count +=1 

# print(count)

# for message in reddit.inbox.messages(limit=5):
#     print(message.subject)

def find_root_submission(comment):
    ancestor = comment
    refresh_counter = 0
    while not ancestor.is_root:
        ancestor = ancestor.parent()
        if refresh_counter % 9 == 0:
            ancestor.refresh()
        refresh_counter += 1
    print('Top-most Ancestor: {}'.format(ancestor))
    return ancestor

def clean_text(corpus):
    # After a text is obtained, we start with text normalization.
    # Text normalization includes:
    # from https://medium.com/@datamonsters/text-preprocessing-in-python-steps-tools-and-examples-bf025f872908
    
    # 0. remove links
    corpus = re.sub(r'http\S+', '', corpus)

    # 1. converting all letters to lower or upper case
    corpus = corpus.lower()

    # 2. converting numbers into words or removing numbers
    corpus = re.sub(r'\d+', '', corpus)

    # 3. Remove punctuation
    corpus = corpus.translate(str.maketrans('', '', string.punctuation))

    # 4. Remove whitespaces
    corpus = corpus.strip()

    # 5. Stop words removal
    stop_words = set(stopwords.words('english'))
    from nltk.tokenize import word_tokenize
    tokens = word_tokenize(corpus)
    tokens = [i for i in tokens if not i in stop_words]


    return tokens



def comments_to_corpus(submission):
    count = 0
    corpus = ''
    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
        corpus += comment.body + " "
        count +=1 
    return corpus
    


def word_cloud_this_post():

    clouds = 0
    mess = 0
    unread_mess = reddit.inbox.unread(limit=None)
    # print('found ', len(unread_mess), ' messages')
    for item in unread_mess:
        # if isinstance(item, reddit.inbox.mentions):
        # print(item.author)
        if item.body.find('u/word_cloud_this_post') != -1:

            mention = item
            item.mark_read()
        
            print('{}\n{}\n'.format(mention.author, mention.body))
            # mention.mark_unread()   
            # mention.reply('hey thanks for mentioning me')
            submission = mention.submission
            print(submission.title,submission.score)
            corpus = comments_to_corpus(submission)
            # print(corpus)
            clntxt = clean_text(corpus)
            # print(clntxt)
            imgName = wc_corpus(clntxt,submission.id)
            link = upload_img(imgName)
            os.remove(imgName)
            # now post this link as reply to the comment which summoned this bot
            try:
                mention.reply("here's the wordcloud of this post : " + link)
                clouds += 1
            except:
                print('some error occured I am unable to reply to the comment')
            mess += 1
    return clouds,mess

                







def wc_corpus(tokens,rid):
    strtoken = ''
    for word in tokens: 
        strtoken += word + ' '

    wordcloud = WordCloud(width = 1600, height = 900, 
    background_color ='white').generate(strtoken) 
    '''
    width = 800, height = 800, 
    background_color ='white', 
    stopwords = stopwords, 
    min_font_size = 10
    '''
    #tit = random.randint(0,100)
    #overinding rid var
    rid = random.randint(1000,9999)
    imgName = str(rid) + '.png'
    wordcloud.to_file(imgName)
    
    return imgName
    # # plot the WordCloud image                        
    # plt.figure(figsize = (16, 9), facecolor = None) 
    # plt.imshow(wordcloud) 
    # plt.axis("off") 
    # plt.tight_layout(pad = 0) 

    # plt.show() 

    
def read_imgur_cred():
    # txt file for imgur cred
    f = open('imgur.txt','r')
    lines = f.readlines()
    imgurID = lines[1][:-1]
    imgurSecret = lines[3][:-1]
    return imgurID,imgurSecret

def read_reddit_cred():
    # txt file of reddit creds
    f = open('reddit.txt','r')
    lines = f.readlines()
    redID = lines[1][:-1]
    redSecret = lines[3][:-1]
    redPass = lines[5][:-1]
    return redID,redSecret,redPass
  
def upload_img(imgName):
    """Uploads an image file to Imgur"""

    client_id,client_secret = read_imgur_cred()
    if client_id is None or client_secret is None:
        click.echo('Cannot upload - could not find IMGUR_API_ID or IMGUR_API_SECRET config file')
        return

    client = ImgurClient(client_id, client_secret)
    click.echo('Uploading file {}'.format(click.format_filename(imgName)))
    response = client.upload_from_path(imgName)
    click.echo('File uploaded - see your gif at {}'.format(response['link']))

    return response['link']

  
print("starting reddit bot - word cloud this post")
redID, redSecret, redPass = read_reddit_cred()

reddit = praw.Reddit(client_id=redID,
                     client_secret=redSecret,
                     password=redPass,
                     user_agent='testscript by /u/word_cloud_this_post',
                     username='word_cloud_this_post')

print(reddit.user.me())




while True:
    clouds = 0
    clouds,mess = word_cloud_this_post()
    print(datetime.datetime.now(),' --- Made ',clouds,' clouds out of ',mess,' requests')
    time.sleep(180)
