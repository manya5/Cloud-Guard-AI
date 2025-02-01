from flask import Flask,render_template,flash,redirect,url_for,session,make_response, request
from forms import LoginForm  #importing login form from forms.py
import os
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect  #importing csrf protection from flask_wtf
import pymongo #importing pymongo to connect to mongodb
from bson import ObjectId
import jwt 
import bcrypt #importing bcrypt for password protection
import secrets #importing secrets to generate secret 
from flask import Flask, request, jsonify
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler  
from flask_mailman import Mail, EmailMessage


app=Flask(__name__)
mail = Mail()
mail.init_app(app)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = "465"
app.config["MAIL_USERNAME"] = "cloudguardaiapp@gmail.com"
app.config["MAIL_PASSWORD"] = "bfsh xgwl shxl lzpz"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True 


#connecting to mongodb
client=pymongo.MongoClient(os.getenv('MONGO_URI'))
load_dotenv()

#connecting to database
db=client['SkyVaultDB']

#connecting to collections
userCollection = db['users']
filesCollection = db['files']
activityCollection = db['activities']
anomalyCollection = db['anomalies']
# setting secret key for csrf protection
app.config[('SECRET_KEY')] = secrets.token_hex(32)

#enabling csrf protection
# csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = False




# ***************** ANOMALY DETECTION USING ISOLATION FOREST 


from ml_model import AnomalyDetector

detector = AnomalyDetector()

@app.route('/api/train_model')
def train_model():
    try:
        # gets all activities from database
        activities = list(activityCollection.find())
        if not activities:
            return jsonify({
                'status': 'error',
                'message': 'activity data not found'
            }), 400
            
        success = detector.train(activities)


        if success:
            return redirect('/home');
            # return jsonify({
            #     'status': 'success',
            #     'message': 'model training completed'
            # })
        else:
            return jsonify({
                'status': 'error',
                'message': 'error in model training'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'error: {str(e)}'
        }), 500
    




@app.route('/api/check_activity/<activity_id>')
def check_activity(activity_id):

    try:
        activity = activityCollection.find_one({'_id': ObjectId(activity_id)})
        if not activity:
            return jsonify({'error': 'activity not found'}), 404
            
        result = detector.predict_with_score(activity)
        
        response_data = {
            'activity_id': str(activity_id),
            'filename': activity.get('filename', 'unknown'),
            'timestamp': str(activity.get('fileUploadedAt', '')),
            'is_anomaly': bool(result['is_anomaly']),  
            'anomaly_score': float(result['anomaly_score'])  
        }


        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'error: {str(e)}'
        }), 500


# ... existing imports ...
import csv
from io import StringIO
from datetime import datetime

# ... existing code ...

@app.route('/api/export_anomaly_report')
def export_anomaly_report():
    try:
        # get all the activites
        activities = list(activityCollection.find())
        
        if not activities:
            return jsonify({
                'status': 'error',
                'message': 'activity data not found'
            }), 400

        # creating stringId buffer for CSV output
        si = StringIO()
        writer = csv.writer(si)
        
        # write CSV headers
        writer.writerow(['Activity ID', 'Filename', 'Timestamp', 'User', 'Is Anomaly', 'Anomaly Score'])
        
        # get anomaly score for each acitivty and store it into CSV file
        for activity in activities:
            result = detector.predict_with_score(activity)
            writer.writerow([
                str(activity['_id']),
                activity.get('filename', 'unknown'),
                activity.get('fileUploadedAt', ''),
                str(activity.get('user', '')),
                'Yes' if result['is_anomaly'] else 'No',
                f"{result['anomaly_score']:.4f}"
            ])
        
        # prepare CSV responses
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=anomaly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output.headers["Content-type"] = "text/csv"
        
        return output
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'error: {str(e)}'
        }), 500

# *********************************************************************************






# route for login
@app.route('/' ,methods=['GET','POST'])
@app.route('/login' , methods=['GET','POST'])
def login():

    #creating form object
    form = LoginForm()

    #validating form data
    if form.validate_on_submit():
     user_email=form.email.data
     user_password=form.password.data


     #finding user in database
     user=userCollection.find_one({'email':user_email})
     

     #if user is not found
     if user is None:
      flash('User not found')
      return render_template('index.html',form=form)
     
     else:

        #getting hashed password from database
        hashedPassword = user['password']
     
        # Convert password string to bytes before checking
        user_password = user_password.encode('utf-8')
        hashedPassword = hashedPassword.encode('utf-8')

        #checking if password is correct
        authenticate = bcrypt.checkpw(user_password, hashedPassword)
        

        payload = {
           'id': str(user['_id']),   
           'email':user['email'], 
           'username':user['username'], 
           'phone':user['phone']
        }
        # generating token
        token = jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')
        print('token', token)
        res = make_response(redirect(url_for('home')))

 

        # setting token in cookie
        
        res.set_cookie('token', token)

        print(authenticate)

        #if password is correct
        if authenticate:
          flash('Logged in successfully')
        #   return redirect(url_for('home'))        
          return res


        else:
          flash('Invalid credentials')
          return redirect(url_for('login'))
     
     
    return render_template('index.html',form=form)


@app.route('/logout' ,methods=['GET', 'POST'])
def logout():   
    res = make_response(redirect(url_for('login')))
    res.set_cookie('token', value = '', expires=0)
    return res

# route for home page
# @app.route('/home')
# @app.route('/dashboard')
# def home():
#     return render_template('home.html')


@app.route('/home')
@app.route('/dashboard')
def home():
    try:
        # Get user token from cookie
        token = request.cookies.get('token')
        usertoken = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
        user_id = ObjectId(usertoken['id'])

        # Get total files count
        files_count = filesCollection.count_documents({'user': user_id})

        # Get total activities count
        activities_count = activityCollection.count_documents({'user': user_id})

        # Get anomaly count
        activities = list(activityCollection.find({'user': user_id}))
        anomaly_count = 0
        if activities:
            for activity in activities:
                result = detector.predict_with_score(activity)
                if result['is_anomaly']:
                    anomaly_count += 1

        # Get recent activities (last 5)
        recent_activities = list(activityCollection.find(
            {'user': user_id}
        ).sort('fileUploadedAt', -1).limit(5))

        return render_template('home.html', 
                            files_count=files_count,
                            activities_count=activities_count,
                            anomaly_count=anomaly_count,
                            recent_activities=recent_activities,
                            user=usertoken)
    except Exception as e:
        print(f"Error is: {str(e)}")
        return redirect(url_for('login'))


# @app.route('/api/anomaly-insights')
# def get_anomaly_insights():
#     # Example response - replace with your actual data
#     return jsonify({
#         'recentAnomalies': [
#             {
#                 'type': 'Unusual Login Pattern',
#                 'timestamp': '2024-03-20 14:30:00',
#                 'description': 'Multiple login attempts from different locations'
#             },
#             # Add more anomalies...
#         ],
#         'stats': {
#             'total': 15,
#             'highSeverity': 3,
#             'mediumSeverity': 7,
#             'lowSeverity': 5
#         }
#     })


@app.route('/api/get-anomaly-details')
def get_anomaly_details():
    try:
        token = request.cookies.get('token')
        usertoken = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
        user_id = ObjectId(usertoken['id'])

        # Fetch anomalies for the user
        anomalies = list(anomalyCollection.find(
            {'user_id': user_id}
        ).sort('timestamp', -1))  # Sort by newest first

        # Format the response
        anomaly_details = []
        for anomaly in anomalies:
            anomaly_details.append({
                'filename': anomaly.get('filename', 'Unknown File'),
                'timestamp': anomaly.get('timestamp', '').strftime('%Y-%m-%d %H:%M:%S') if anomaly.get('timestamp') else 'Unknown Time',
                'description': anomaly.get('description', 'No description available'),
                'severity': anomaly.get('severity', 'low'),
                'anomaly_score': round(anomaly.get('anomaly_score', 0), 3)
            })

        return jsonify({
            'status': 'success',
            'anomalies': anomaly_details
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/anomaly-insights')
def get_anomaly_insights():
    try:
        token = request.cookies.get('token')
        usertoken = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
        user_id = ObjectId(usertoken['id'])

        recent_anomalies = []
        activities = list(activityCollection.find({'user': user_id}))
        
        for activity in activities:
            result = detector.predict_with_score(activity)
            if result['is_anomaly']:
                # Create anomaly record
                anomaly_data = {
                    'user_id': user_id,
                    'activity_id': activity['_id'],
                    'filename': activity.get('filename', 'unknown'),
                    'timestamp': activity.get('fileUploadedAt', ''),
                    'description': result.get('reason', 'No specific reason provided'),
                    'anomaly_score': result['anomaly_score'],
                    'severity': result.get('severity', 'low'),
                    'detected_at': datetime.now()
                }
                
                # Insert into anomalies collection
                anomalyCollection.insert_one(anomaly_data)
                
                recent_anomalies.append({
                    'type': 'Anomaly Detected',
                    'timestamp': str(activity.get('fileUploadedAt', '')),
                    'description': result.get('reason', 'No specific reason provided'),
                    'severity': result.get('severity', 'low'),
                    'filename': activity.get('filename', 'unknown')
                })

        return jsonify({
            'recentAnomalies': recent_anomalies,
            'stats': {
                'total': len(recent_anomalies),
                'highSeverity': sum(1 for x in recent_anomalies if x.get('severity') == 'high'),
                'mediumSeverity': sum(1 for x in recent_anomalies if x.get('severity') == 'medium'),
                'lowSeverity': sum(1 for x in recent_anomalies if x.get('severity') == 'low')
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

    try:
        # Fetch recent anomalies from your database or anomaly detection logic
        recent_anomalies = []
        activities = list(activityCollection.find())
        
        for activity in activities:
            result = detector.predict_with_score(activity)
            if result['is_anomaly']:
                anomaly_description = result.get('reason', 'No specific reason provided')
                
                # Save anomaly details to the database
                anomaly_data = {
                    'activity_id': activity['_id'],
                    'filename': activity.get('filename', 'unknown'),
                    'timestamp': activity.get('fileUploadedAt', ''),
                    'description': anomaly_description,
                    'anomaly_score': result['anomaly_score']
                }
                anomalyCollection.insert_one(anomaly_data)
                
                recent_anomalies.append({
                    'type': 'Anomaly Detected',
                    'timestamp': str(activity.get('fileUploadedAt', '')),
                    'description': anomaly_description
                })

        return jsonify({
            'recentAnomalies': recent_anomalies
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500
# route for activity page
@app.route('/activity')
def activity():
    token = request.cookies.get('token')
    usertoken = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
    print(usertoken)
    
    activities = activityCollection.find({'user': ObjectId(usertoken['id'])})
    activities = list(activities)
    for activity in activities:
        print(activity)

    return render_template('activity.html', activities = activities)

# route for settings page
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    token = request.cookies.get('token')
    usertoken = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])

    return render_template('settings.html' ,title='CloudGuard AI -Settings', user=usertoken)

@app.route('/api/get_anomaly_stats')
def get_anomaly_stats():
    try:
        # Get all activities
        token = request.cookies.get('token')
        usertoken = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
        activities = list(activityCollection.find({'user': ObjectId(usertoken['id'])}).sort('fileUploadedAt', 1))  # Sort by timestamp
        
        if not activities:
            return jsonify({
                'status': 'error',
                'message': 'No activity data found'
            }), 400
        


        chart_data = {
            'labels': [],
            'anomaly_scores': [],
            'is_anomaly': [],
            'filenames': []
        }

        for activity in activities:
            result = detector.predict_with_score(activity)
            
            # Better timestamp handling
            timestamp = activity.get('fileUploadedAt')
            if timestamp:
                formatted_time = timestamp.strftime('%Y-%m-%d %H:%M')
            else:
                # Use file creation time or current time as fallback
                timestamp = activity.get('createdAt', datetime.now())
                formatted_time = timestamp.strftime('%Y-%m-%d %H:%M')
            
            chart_data['labels'].append(formatted_time)
            chart_data['anomaly_scores'].append(float(result['anomaly_score']))
            chart_data['is_anomaly'].append(bool(result['is_anomaly']))
            chart_data['filenames'].append(activity.get('filename', 'Unnamed File'))

        return jsonify({
            'status': 'success',
            'data': chart_data
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500
    
# @app.route('/monitor')
# def monitor():
#     activities = activityCollection.find()
#     return render_template('monitor.html', title='CloudGuard AI - Monitor', activities=activities)

@app.route('/monitor')
def monitor():
    try:
        # First, train the model
        activities = list(activityCollection.find())
        if activities:
            detector.train(activities)
        
        # Then get activities for display
        activities = activityCollection.find()
        return render_template('monitor.html', title='CloudGuard AI - Monitor', activities=activities)
    except Exception as e:
        flash(f'Error preparing monitoring data: {str(e)}', 'error')
        return render_template('monitor.html', title='CloudGuard AI - Monitor', activities=[])

# route for sky vault page  
@app.route('/sky_vault')
def sky_vault():
    return render_template('sky_vault.html' ,title='Sky Vault')     


@app.route('/change_password')
def changePassword():
    return render_template('changePassword.html')


@app.route('/notification_channel')
def notificationChannel():
    return render_template('notificationChannel.html')


@app.route('/two-factor-authentication')
def twoFactorAuthentication():
    return render_template('twoFA.html')


# @app.route('/verify-otp', methods=['GET', 'POST'])
# def verify_otp():
#     if 'otp' not in session or 'user_id' not in session:
#         return redirect(url_for('login'))
        
#     if request.method == 'POST':
#         user_otp = request.form.get('otp')
        
#         if user_otp == session['otp']:
#             # Get user details
#             user = userCollection.find_one({'_id': ObjectId(session['user_id'])})
            
#             # Create payload for JWT
#             payload = {
#                 'id': str(user['_id']),   
#                 'email': user['email'], 
#                 'username': user['username'], 
#                 'phone': user['phone']
#             }
            
#             # Generate token
#             token = jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')
            
#             # Clear session
#             session.pop('otp', None)
#             session.pop('user_id', None)
            
#             # Create response
#             res = make_response(redirect(url_for('home')))
#             res.set_cookie('token', token)
            
#             return res
#         else:
#             flash('Invalid OTP')
#             return redirect(url_for('verify_otp'))
            
#     return render_template('verify_otp.html')

if __name__=='__main__':
    app.run(debug=True)
    # socketio.run(app, debug=True)