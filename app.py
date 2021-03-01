from flask import Flask, render_template, flash, redirect, url_for, session, request
import googleapiclient.discovery
import os
import xlsxwriter
from leia import SentimentIntensityAnalyzer


#encoding: utf-8

# Antes de usar, você precisa de uma developer key do YT
DEVELOPER_KEY = "AIzaSyDQ99WFIPJOjO4Sijgt0RT2YPqGbioyj7s"
app = Flask(__name__)
app.secret_key = "asy_by_mimi"

@app.route("/")
def index():
    if 'user' not in session or session['user'] == None:
        return redirect(url_for('login'))
    return render_template('index.html', result="")

@app.route("/login")
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST', ])
def authenticate():
    if(request.form['username'] == "marcia" and request.form['password'] == "Tyk9iP1@3"):
        session['user'] = request.form['username']
        return redirect(url_for('index'))
    flash('ERRO: Usuário e/ou senha incorretos. Por favor, tente novamente.')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session['user'] = None
    return redirect(url_for('login'))

@app.route('/analyse', methods=['Post', ])
def analyse():
    if 'user' not in session or session['user'] == None:
        return redirect(url_for('login'))

    video = request.form['video']
    word = request.form['word']

    if(video == ""):
        flash('ERRO: Insira o Link do Video')
        return redirect(url_for('index'))

    if(request.form.get("search") and word == ""):
        flash('ERRO: Insira a palavra')
        return redirect(url_for('index'))


    video_id = get_video_id(video)
    comments = get_comments(video_id)
    if(request.form.get("analyse")):
        result = analyse_sentiment(comments)
        comments_result = ""
    else:
        [result,comments_result] = analyse_words(comments, word)
    return render_template('index.html', result=result, comments_result=comments_result, link=video, word=word)

def get_video_id(video):
    start = video.find('?v=') +3
    end = video.find('&')
    if(end >= 0):
        video_id = video[start:end]
    else:
        video_id = video[start:]
    return video_id

def get_comments(video_id):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    nextPageToken = ''
    comments = []

    while True:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            pageToken=nextPageToken
        )
        response = request.execute()

        for item in response['items']:
            comments.append(item['snippet']['topLevelComment']['snippet']['textOriginal'])

        try:
            nextPageToken = response['nextPageToken']
        except:
            break

    return comments


def analyse_sentiment(comments):
    s = SentimentIntensityAnalyzer()

    result = {
        #'negatives': [],
        #'positives': [],
        #'neutros': [],
        'Commentários totais': 0,
        'Total positivos': 0,
        'Total negativos': 0,
        'Total neutros': 0,
        }

    max_positive = 0.05
    max_negative = -0.05

    for comment in comments:
        score = s.polarity_scores(comment)
        result['Commentários totais'] += 1
        if score['compound'] >= 0.05:
            #result['positives'].append(comment)
            result['Total positivos']+=1;
        elif score['compound'] <= -0.05:
            #result['negatives'].append(comment)
            result['Total negativos']+=1;
        else:
            #result['neutros'].append(comment)
            result['Total neutros']+=1;

        if score['compound'] >= max_positive:
            max_positive = score['compound']

        if score['compound'] <= max_negative:
            max_negative = score['compound']

    return result

def analyse_words(comments, word):
    result = {
        'Commentários totais': 0,
        'Frequencia': 0,
    }
    comments_result = []
    #workbook = xlsxwriter.Workbook('uploads/Youtube_Comments.xlsx')
    #worksheet = workbook.add_worksheet()

    search_word = word.lower()

    for comment in comments:
        result['Commentários totais'] += 1

        if search_word in comment.lower():
            #worksheet.write(result['Frequencia'], 0, comment)
            comments_result.append(comment)
            result['Frequencia'] += 1

    #workbook.close()
    return [result, comments_result]

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory='uploads', filename=filename)


if __name__ == '__main__':
    app.run(debug=True)
