from flask import Flask, render_template, redirect, request, url_for, session, flash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from jose import jwt
from .auth import login_required, exchange_code_for_token, get_cognito_public_keys, secretFromSM, create_user_session, validate_session

app = Flask(__name__, static_url_path='/usermanagement/static')
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['SECRET_KEY'] = "w?bZ+$f}]sA?k4A"

CORS(app)

# @app.route('/usermanagement/dashboard')
# @login_required
# def dashboard(username):
#     return render_template('dashboard.html', username=username)

@app.route('/index.html')
def dashboard():
    return redirect(request.host_url + 'index/index.html')

@app.route('/usermanagement/callback')
def callback():
    code = request.args.get('code')

    if code:
        # Exchange code for tokens
        tokens = exchange_code_for_token(code)
        keys = get_cognito_public_keys()
        decoded_access_token = jwt.decode(tokens['access_token'], keys, algorithms=['RS256'], audience=secretFromSM['COGNITO_CLIENT_ID'])
        user_id = decoded_access_token['sub']
        additional_info = {'username': decoded_access_token['username'], 'tokenExpiration': tokens['expires_in'], 'EntireToken': tokens }

        session['userId'] = user_id
        session['sessionId'] = create_user_session(user_id, additional_info)

        dashboard_url = url_for('dashboard') #+ "?sessionId=" + session['sessionId']
        return redirect(dashboard_url)
    else:
        # Handle error or redirect to login page
        flash("Something went wrong, please try logging in again")
        return redirect(url_for('landing'))


@app.route('/usermanagement/landingpage')
def landing():
    CognitoDomain = secretFromSM['COGNITO_DOMAIN']
    CognitoClientID = secretFromSM['COGNITO_CLIENT_ID']
    redirectURL = request.host_url[:-1]+url_for('callback')

    if ('cloudfront' in redirectURL):
        redirectURL = redirectURL.replace("http://", "https://")

    hostedUIURL = f'{CognitoDomain}/login?response_type=code&client_id={CognitoClientID}&redirect_uri={redirectURL}'

    return render_template("landingpage.html", hostedUIURL=hostedUIURL)

@app.route('/usermanagement/cognitologout')
def logout():
    session_id = session.get('sessionId') or request.args.get('sessionId')
    if session_id:
        if validate_session(session_id):
            session.pop('sessionId', None)
            CognitoDomain = secretFromSM['COGNITO_DOMAIN']
            CognitoClientID = secretFromSM['COGNITO_CLIENT_ID']
            cognito_logout_url = (
                f'{CognitoDomain}/logout?'
                f'client_id={CognitoClientID}&'
                f'logout_uri={url_for("post_logout", _external=True)}'
            )
            return redirect(cognito_logout_url)
    return redirect(url_for("landing"))

@app.route('/usermanagement/logout')
def post_logout():
    return render_template("logout.html")

# @app.route('/transcription/transcription')
# def transcribe():
#     return redirect(request.host_url + 'transcription/transcription')

# @app.route('/documentmanagement/report')
# def report():
#     return redirect(request.host_url+ 'documentmanagement/report')

# @app.route('/documentmanagement/audio')
# def audiofile():
#     return redirect(request.host_url+ 'documentmanagement/audio')

@app.route('/health')
def healthcheck():
    return "OK", 200
