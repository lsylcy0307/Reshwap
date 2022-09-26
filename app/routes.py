from flask import Flask, redirect, render_template, request, jsonify, url_for
from flask import render_template
import flask
from app import app

from utils import generate_user_id, generate_random_id, time_now

import google.oauth2.credentials
import google_auth_oauthlib.flow

import datetime
import json

import os
import random

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from app import *

import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

from app.awsresource import get_bucket

import boto3
from botocore.client import Config
# from boto3 import ClientError

oauth_scopes = [
"https://www.googleapis.com/auth/userinfo.email", #gets google profile
"openid",
"https://www.googleapis.com/auth/userinfo.profile", #gets google email adress
]

cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred)
db = firestore.client()

users_ref = db.collection('users')
items_ref = db.collection('items')

s3_accessKey='AKIA2QYVIRBAO2SLB3X4'
s3_accessSecret='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'
s3_bucketName='reswhap-imgs'

client_s3 = boto3.client(
    's3',
    aws_access_key_id=s3_accessKey,
    aws_secret_access_key=s3_accessSecret
)

from firestoremodels import *


@app.route('/')
def home():
    if is_logged_in():
        return redirect(url_for('index', category='all'))
    else:
        return render_template('home.html', title='lvilleTrade')
    

@app.route('/index/<category>')
def index(category):
    if not is_logged_in():
        return render_template('home.html', title='lvilleTrade')

    all_items = []
    sold_items = []
    slc_category = "All Items"

    if category=="all":
        items = items_ref.where("sold","==",False).get()
        solds = items_ref.where("sold","==",True).get()
    else:
        slc_category=category
        items = items_ref.where("item_category","==",category).where("sold","==",False).get()
        solds = items_ref.where("item_category","==",category).where("sold","==",True).get()

    for item in items:
        all_items.append(item.to_dict())

    for item in solds:
        sold_items.append(item.to_dict())

    my_bucket = get_bucket()

    image_url=[]

    for item in all_items:
        image_url.append(item['image_url'][0])

    print(image_url)

    return render_template('index.html', title='Home', items = all_items, sold_items = sold_items, img_url=image_url, category=slc_category)

@app.route('/item/<item_id>')
def item(item_id):
    if not is_logged_in():
        return render_template('home.html', title='lvilleTrade')

    if item_id != "":
        user = users_ref.where("email","==",flask.session["user_info"]["email"]).get()
        user = user[0].to_dict()

        selected_itm = items_ref.where("id","==", item_id).get()
        selected_itm = selected_itm[0].to_dict()

        itm_seller = user_found = users_ref.where("email","==",selected_itm["seller_email"]).get()
        itm_seller = itm_seller[0].to_dict()

        following = False
        saved = False
        sold = selected_itm["sold"]

        if item_id in user["saved_items"]:
            saved = True

        if itm_seller["email"]==flask.session["user_info"]["email"]:
            print("the user owns this")
            cur_user = True
        else:
            cur_user = False

        
        if cur_user == False:
            if itm_seller["user_id"] in user["following"]:
                following = True
            else:
                following = False

        my_bucket = get_bucket()
        summaries = my_bucket.objects.filter(Prefix=item_id)

        image_url = selected_itm["image_url"]

        seller_itm = []
        user_items = items_ref.where("seller_email","==", itm_seller["email"]).get()
        
        # seller_itm_img=[]
        if len(user_items) > 1:
            seller_itm.append(user_items[0].to_dict())
            seller_itm.append(user_items[1].to_dict())
        else:
            seller_itm.append(user_items[0].to_dict())

        return render_template('itemPage.html', title='item', item = selected_itm, img_url = image_url, itm_seller = itm_seller, seller_itm=seller_itm, cur_user=cur_user, following=following, saved=saved, sold=sold)

@app.route('/user/<user_id>')
def user(user_id):
    if not is_logged_in():
        return render_template('home.html', title='lvilleTrade')

    cur_user = users_ref.where("email","==",flask.session["user_info"]["email"]).get()
    cur_user = cur_user[0].to_dict()
    cur_user_id = cur_user["user_id"]

    all_items = []

    if cur_user_id == user_id :
        print("current user")
        return redirect(url_for('profile'))
    else:
        print("different from the current user")

        user_found = users_ref.where("user_id","==",user_id).get()
        user_found = user_found[0].to_dict()
        user_found_email = user_found["email"]

        user_items = items_ref.where("seller_email","==", user_found_email).get()
        
        for item in user_items:
            all_items.append(item.to_dict())
        
        return render_template('sellerProfile.html', title='seller profile', user=user_found, items = all_items, saved_items = None, sold_items = None)


@app.route('/update', methods=['POST'])
def update():
    if not is_logged_in():
        return render_template('home.html', title='lvilleTrade')

    cur_user = users_ref.where("email","==",flask.session["user_info"]["email"]).get()
    cur_user = cur_user[0].to_dict()

    list_type = request.form['list_type']

    all_items = []

    if list_type=="saved":
        saved_items = cur_user["saved_items"]
        for item in saved_items:
            found_item = items_ref.where("id","==", item).get()
            all_items.append(found_item[0].to_dict())
    print(all_items)
    return jsonify({'result':'success', 'items':all_items})
    

@app.route('/saveitem/<itemid>')
def saveitem(itemid):
    
    user_found = users_ref.where("email","==",flask.session["user_info"]["email"]).get()
    user_found = user_found[0].to_dict()

    saved_items = user_found["saved_items"]
    user_found_id = user_found["user_id"]
    
    if itemid not in saved_items:
        print("saving...")
        saved_items.append(itemid)
    else:
        print("unsaving...")
        saved_items.remove(itemid)

    doc = users_ref.document(user_found_id)
    field_update = {"saved_items":saved_items}
    doc.update(field_update)

    return redirect(url_for('profile'))


@app.route('/sold/<itemid>')
def sold(itemid):
    doc = items_ref.document(itemid)
    field_update = {"sold":True}
    doc.update(field_update)
    print("marked sold")

    return redirect(url_for('profile'))

@app.route('/unsold/<itemid>')
def unsold(itemid):
    doc = items_ref.document(itemid)
    field_update = {"sold":False}
    doc.update(field_update)
    print("marked unsold")

    return redirect(url_for('profile'))


@app.route('/sendContactEmail/<email>/<item_id>')
def sendContactEmail(email, item_id):

    user_found = users_ref.where("email","==",flask.session["user_info"]["email"]).get()
    user_found = user_found[0].to_dict()
    buyer_name = user_found["name"]
    buyer_email = user_found["email"]

    seller_found = users_ref.where("email","==",email).get()
    seller_found = seller_found[0].to_dict()
    seller_name = seller_found["name"]
    seller_email = seller_found["email"]

    found_item = items_ref.where("id","==", item_id).get()
    item = found_item[0].to_dict()

    seller_mail_title = "[Reshwap - {}] Interest Notification".format(item["item_name"])
    seller_msg = Message(seller_mail_title, sender = 'reshwap2019@gmail.com', recipients = [email])
    seller_msg.body = "Hello,\n\nname: {}\nemail: {}\n\nshowed interest to your item [{}].\nContact them to sell your item.\n\n-Reshwap".format(buyer_name, buyer_email, item["item_name"])
    mail.send(seller_msg)

    buyer_mail_title = "[Reshwap - {}] Successfully Sent an Interest Notification".format(item["item_name"])
    buyer_msg = Message(buyer_mail_title, sender = 'reshwap2019@gmail.com', recipients = [buyer_email])
    buyer_msg.body = "Hello,\n\nSuccessfull sent an interest notification to\n\nname: {}\nemail: {}\n\nfor the item [{}].\nThe seller will reach back to you soon.\n\n-Reshwap".format(seller_name, seller_email, item["item_name"])
    mail.send(buyer_msg)

    return redirect(url_for('item', item_id = item_id))


@app.route('/follow/<userid>')
def follow(userid):
    if not is_logged_in():
        return render_template('home.html', title='lvilleTrade')

    following_user_found = users_ref.where("email","==",flask.session["user_info"]["email"]).get()
    following_user_found = following_user_found[0].to_dict()
    following_user_id = following_user_found["user_id"]
    following = following_user_found["following"]
    # print(following)

    if userid not in following:
        following.append(userid)

        doc = users_ref.document(following_user_id)
        field_update = {"following":following}
        doc.update(field_update)
    else:
        print("already following")

        # ---
    user_found = users_ref.where("user_id","==",userid).get()
    user_found = user_found[0].to_dict()
    follower = user_found["follower"]

    if following_user_id not in follower:
        follower.append(following_user_id)

        doc = users_ref.document(userid)
        field_update = {"follower":follower}
        doc.update(field_update)
    else:
        print("already followed")

    return redirect(url_for('user', user_id=userid))

@app.route('/unfollow/<userid>')
def unfollow(userid):
    if not is_logged_in():
        return render_template('home.html', title='lvilleTrade')

    following_user_found = users_ref.where("email","==",flask.session["user_info"]["email"]).get()
    following_user_found = following_user_found[0].to_dict()
    following_user_id = following_user_found["user_id"]
    following = following_user_found["following"]

    print(following)
    if userid in following:
        following.remove(userid)

        doc = users_ref.document(following_user_id)
        field_update = {"following":following}
        doc.update(field_update)

        print(following)
    else:
        print("not following")
    
    # ---

    user_found = users_ref.where("user_id","==",userid).get()
    user_found = user_found[0].to_dict()
    follower = user_found["follower"]

    if following_user_id in follower:
        follower.remove(following_user_id)

        doc = users_ref.document(userid)
        field_update = {"follower":follower}
        doc.update(field_update)
    else:
        print("not followed")

    return redirect(url_for('user', user_id=userid))

@app.route('/profile')
def profile():
    if not is_logged_in():
        return render_template('home.html', title='lvilleTrade')
    user_email = flask.session["user_info"]["email"]
    user_items = items_ref.where("seller_email","==", user_email).where("sold","==", False).get()
    cur_user = users_ref.where("email","==",user_email).get()
    cur_user = cur_user[0].to_dict()

    sold = items_ref.where("seller_email","==", user_email).where("sold","==", True).get()

    all_items = []
    for item in user_items:
        all_items.append(item.to_dict())

    saved_items = []
    saved_items_id = cur_user["saved_items"]
    for item in saved_items_id:
        found_item = items_ref.where("id","==", item).get()
        saved_items.append(found_item[0].to_dict())
        
    sold_items = []
    for item in sold:
        sold_items.append(item.to_dict())

    return render_template('profile.html', title='profile', items = all_items, saved_items=saved_items, sold_items=sold_items)

@app.route('/upload', methods =["GET", "POST"])
def upload():
    if request.method == "POST":
        itm_name = request.form.get("itm_name")
        itm_category = request.form.get("itm_category") 
        itm_desc = request.form.get("itm_desc") 
        itm_price = request.form.get("itm_price") 
        itm_exchange = request.form.get("itm_exchange")
        itm_quality = request.form.get("itm_quality") 
        negotiable = request.form.get("negotiable")
        email = flask.session["user_info"]["email"]
        name = flask.session["user_info"]["name"]
        itm_id = generate_random_id()

        file1 = request.files['itm_photo_1']
        file2 = request.files['itm_photo_2']
        file3 = request.files['itm_photo_3']

        my_bucket = get_bucket()

        image_url=[]

        file_name = itm_id + '/1'
        my_bucket.Object(file_name).put(Body=file1)
        image_url.append("https://reswhap-imgs.s3.amazonaws.com/"+file_name)

        if (file2.filename!=""):
            file_name = itm_id + '/2'
            my_bucket.Object(file_name).put(Body=file2)
            image_url.append("https://reswhap-imgs.s3.amazonaws.com/"+file_name)
        
        if (file3.filename!=""):
            file_name = itm_id + '/3'
            my_bucket.Object(file_name).put(Body=file3)
            image_url.append("https://reswhap-imgs.s3.amazonaws.com/"+file_name)

        new_item = items_model(itm_category, email, name, itm_name, itm_desc, itm_quality, itm_price, itm_exchange, negotiable, itm_id, image_url)
        items_ref.document(itm_id).set(new_item)

        user_found = users_ref.where("email","==",flask.session["user_info"]["email"]).get()
        user_found = user_found[0].to_dict()
        user_id = user_found["user_id"]
        item_sold = user_found["number_of_items"]
        item_sold += 1

        doc = users_ref.document(user_id)
        field_update = {"number_of_items":item_sold}
        doc.update(field_update)

        return redirect(url_for('profile'))

    return render_template('upload_item.html', title='upload an item')

# ----login
@app.route('/login')
def login():

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow stepsself.
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
      json.loads(os.environ['CLIENT_SECRET']),#os.environ['CLIENT_SECRET']
      scopes=oauth_scopes,
      redirect_uri= flask.request.url_root + 'oauth2callback'
    )

    authorization_url, state = flow.authorization_url(
      prompt='consent',
      include_granted_scopes='true')

    flask.session['state'] = state

    return redirect(authorization_url)

def credentials_to_dict(credentials):
    return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

@app.route('/oauth2callback')
def oauth2callback():
    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_config(json.loads(os.environ['CLIENT_SECRET']), scopes=oauth_scopes, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    print(credentials_to_dict(credentials))
    flask.session['credentials'] = credentials_to_dict(credentials)

    if flask.session['credentials']['refresh_token'] == None:
        flask.session['credentials']['refresh_token'] = "1/NWvP0mjD4Vp3xs22FkvdqWHw-_7VUyC2VN7zcsthHcw"

    session = flow.authorized_session()
    user_info = session.get('https://www.googleapis.com/userinfo/v2/me').json()

    flask.session["user_info"] = user_info

    if not is_logged_in():
        #generate new user
        email = flask.session["user_info"]["email"]
        name = flask.session["user_info"]["name"]
        id = generate_user_id()
        new_user = user_model(name, email, id)
        users_ref.document(id).set(new_user)

    # check_email = flask.session["user_info"]["email"]
    # domain = check_email[len(check_email) - 17 :]
    # if domain  ==  "lawrenceville.org" :
    #     print("yay lawrenceville")
    # print(domain)
    return redirect(url_for('index', category='all'))


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    flask.session.pop('credentials', None)
    flask.session.pop('state', None)
    flask.session.pop('user_info', None)
    return redirect('/')

def is_logged_in():
    if("user_info" in flask.session.keys()):
        user_found = users_ref.where("email","==",flask.session["user_info"]["email"]).get()
        if len(user_found) > 0:
            return True
        return False
    return False

def is_logged_in():
    if("user_info" in flask.session.keys()):
        user_found = users_ref.where("email","==",flask.session["user_info"]["email"]).get()
        if len(user_found) > 0:
            return True
        return False
    return False