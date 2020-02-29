import uuid
import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session  # https://pythonhosted.org/Flask-Session
import msal
import re
import app_config
from bs4 import BeautifulSoup
import warnings
import logging
import pandas as pd
from pivottablejs import pivot_ui

warnings.filterwarnings("ignore", category=UserWarning, module='urllib2')
data_df = pd.DataFrame(columns=["date","  ", " ", "   "])
graph_data_list=[]
app = Flask(__name__)
app.config.from_object(app_config)
Session(app)


@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template('index.html', user=session["user"], version=msal.__version__)

@app.route("/login")
def login():
    session["state"] = str(uuid.uuid4())
    auth_url = _build_auth_url(scopes=app_config.SCOPE, state=session["state"])
    return render_template("login.html", auth_url=auth_url, version=msal.__version__)

@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    if request.args.get('state') != session.get("state"):
        return redirect(url_for("index"))  # No-OP. Goes back to Index page
    if "error" in request.args:  # Authentication/Authorization failure
        return render_template("auth_error.html", result=request.args)
    if request.args.get('code'):
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            scopes=app_config.SCOPE,  # Misspelled scope would cause an HTTP 400 error here
            redirect_uri=url_for("authorized", _external=True))
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))


@app.route("/notebooks")
def notebooks():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.GET_NOTEBOOKS_ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()

    return render_template('display.html', result=graph_data)


@app.route("/sections")
def sections():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.GET_SECTIONS_ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    
    return render_template('display.html', result=graph_data)

def get_todo(input_text, window=50):
    if str(input_text).lower().find('todo') > -1:
        return(input_text[str(input_text).lower().find('todo') - window : str(input_text).lower().find('todo') + window])
    else: 
        return -1


def get_todo_all(input_text, search_value='todo', window=50):
    output_text=''
    idx_list = [m.start() for m in re.finditer(search_value, input_text)]
    for idx in idx_list:
        output.append(idx)

    return output


def get_todo_color(input_text, search_value='todo', window=50):
    return input_text.lower().replace('todo', "<h5>todo</h5>")


def content(contentUrlList):
    global data_df
    global graph_data_list

    token = _get_token_from_cache(app_config.SCOPE)

    pic_data = requests.get(  # Use token to call downstream service
            session["user"]['iss']+'/me/photo',
            headers={'Authorization': 'Bearer ' + token['access_token']},
            ).text

    print("session['user']['iss']: ", session["user"]['iss']+'/me/photo')
    print('pic_data: ', pic_data)

    if not token:
        return redirect(url_for("login"))

    for url_list_item in contentUrlList:        
        graph_data = requests.get(  # Use token to call downstream service
            url_list_item['contentUrl'],
            headers={'Authorization': 'Bearer ' + token['access_token']},
            ).text
        graph_data_list.append(graph_data)

        soup = BeautifulSoup(graph_data)
        inputTag = soup.find_all("meta")[1]['content']
        output = inputTag
        print("output: ", output)

        list = soup.findAll('div')
        final_text=''
        for i,list_item in enumerate(list):
            output_text = ''.join(text for text in list_item.find_all(text=True, recursive=True))
            final_text += output_text+'\n'
            todo_text = get_todo_color(output_text)
            data_df.loc[len(data_df)] = [output.split('T')[0], url_list_item['title'], output_text, todo_text]


    print('data_df: ', data_df)
    return render_template('display_new.html', tables=data_df, titles=data_df.columns.values, user=session["user"], version=msal.__version__)


@app.route("/pagescontent")
def pagescontent():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.GET_PAGES_ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()

    return content(graph_data['value']) 


@app.route("/pages")
def pages():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.GET_PAGES_ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()

    return render_template('display.html', result=graph_data) # # #



@app.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    print('token: ', token)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    return render_template('display.html', result=graph_data)


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

app.jinja_env.globals.update(_build_auth_url=_build_auth_url)  # Used in template

if __name__ == "__main__":
    app.run()

