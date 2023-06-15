from flask import Flask, render_template, redirect, session, send_file, url_for, request
import os
#from sql_methods import test_conn_new
#from loguru import logger
import urllib
import requests
import pandas as pd
from sql_methods import test_conn_new, write_db_insert

app = Flask(__name__)
app.secret_key = '[app secret key]'


@app.route('/')
def render_index():
    return render_template('index.html')

@app.route('/about')
def render_about():
    return render_template('about.html')

@app.route('/sql')
def render_sql_test():
    print("hi")    
    #return test_conn_new()

def authorize_url():
    app_url = os.getnav('APP_URL', 'http://localhost')
    #logger.debug(f"APP_URL={app_url}")
    params = {
        "client_id": "40695",
        "response_type": "code",
        "redirect_uri": f"https://howeffectiveismyrunningplan.appspot.com/authorization_successful",
        "scope": "read,profile:read_all,activity:read",
        "state": 'https://github.com/sladkovm/strava-oauth',
        "approval_prompt": "force"
    }
    values_url = urllib.parse.urlencode(params)
    base_url = 'https://www.strava.com/oauth/authorize'
    rv = base_url + '?' + values_url
    #logger.debug(rv)
    return rv

@app.route('/client')
def client():
    return "40695"

@app.route('/login')
def authorize():
    return redirect(authorize_url(), code =302)

@app.route('/cronupdate')
def cron_update():
    from cron_update_data import refresh_token
    res = refresh_token()
    print(res)
    return str(res), 200

@app.route('/sendemail')
def send_email():
    emails = pd.DataFrame()
    emails = emails.append({'emails': Flask.request.args.get('email')}, ignore_index=True)
    write_db_insert(emails, 'emails')

    return "Thank you, you will receive an email when your data is processed! In the mean time, <a href='./about'>read about</a> the model.", 200


@app.route('/authoriation_successful')
def authorization_successful():
    from ingest_athlete import get_athlete, get_athlete_data_status, queue_athlete_for_processing

    try:
        token = session['token']
    except Exception:
        session['token'] = ''

    if(session[token]== ''):
        athlete_data = get_athlete(session['token'])
    else:

        params = {
            "client_id": "40695",
            "client_secret": "[client secret]",
            "code": request.args.get('code'),
            "grant_type": "authorization_code"
        }

        r = requests.post("https://www.strava.com/oauth/token", params)

        logger.debug(r.text)
        session['token'] = r.json()['access_token']
        athlete_data = get_athlete(session['token'])

    try:
        athlete_id = athlete_data['id']
    except Exception:
        try:
            params = {
                "client_id": "40695",
                "client_secret": "[client secret]",
                "code": request.args.get('code'),
                "grant_type": "authorization_code"
            }
            r = requests.post("https://www.strava.com/oauth/token", params)

            logger.debug(r.text)
            session['token'] = r.json()['access_token']
            athlete_data = get_athlete(session['token'])     
        except Exception:
             return "Something went wrong. Please try again later. <a href='./'>Go back home</a>" + str(session['token'])


    athlete_id = athlete_data['id']

    get_athlete_data_status = get_athlete_data_status(athlete_id)

    import random
    if (get_athlete_data_status == 'processed'):
        return render_template('render.html', athlete_id=athlete_id, random_num = str(random.random()))
    elif (get_athlete_data_status == 'processing' or get_athlete_data_status == 'none'):
        return render_template('procesing.html', status = 'processing')
    else:
        queue_athlete_for_processing(athlete_id, r.json()['access_token'], r.json()['refresh_token'])
        return render_template('processing.html', status = 'none')

@app.route("/test_athlete")
def test_athlete():
    from ingest_athlete import get_athlete, get_athlete_data_status, queue_athlete_for_processing  
    import random      
    athlete_id = 14391251
    
    return render_template("render.html", athlete_id=athlete_id, random_num=str(random.random()))

@app.route("/render2")
def render2():
    from ingest_athlete import get_athlete, get_athlete_data_status, queue_athlete_for_processing  
    import random    
    return render_template("render2.html", athlete_id=request.args.get('athlete_id'), random_num=str(random.random()))

@app.route('/plots/athletevsbest', methods = ['GET'])
def athletevsbest():

    from visualizations import athletevsbest
    print(request.args.get('id'))
    bytes_obj = athletevsbest(int(request.args.get('id')))
    return send_file(bytes_obj,
                     attachment_filename='plot.png',
                     mimetype='image/png')

@app.route('/plots/athletevsbestimprovement', methods=['GET'])
def athletevsbestimprovement():
    from visualizations import athletevsbestimprovement
    print(request.args.get('id'))
    bytes_obj = athletevsbestimprovement(int(request.args.get('id')))
    return send_file(bytes_obj,
                     attachment_filename='plot.png',
                     mimetype='image/png')
if __name__ == '__main__':
    app.run()