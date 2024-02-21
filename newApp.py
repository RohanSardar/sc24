import streamlit as st
import pyrebase
import datetime
import numpy as np
import time
import checkImage

firebaseConfig = {
  'apiKey': "AIzaSyDtNz3j2sKU2IXROB6bP-DaGO6kzehlqF4",
  'authDomain': "solutionschallenge2024.firebaseapp.com",
  'databaseURL': "https://solutionschallenge2024-default-rtdb.firebaseio.com",
  'projectId': "solutionschallenge2024",
  'storageBucket': "solutionschallenge2024.appspot.com",
  'messagingSenderId': "157858101943",
  'appId': "1:157858101943:web:a8c211a49119874582ab32",
  'measurementId': "G-VR7MSJEZCB"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

if 'choice' not in st.session_state:
    st.session_state['choice'] = False
if 'op' not in st.session_state:
    st.session_state['op'] = 'Logout'
if 'activate' not in st.session_state:
    st.session_state['activate'] = True
if 'validity' not in st.session_state:
    st.session_state['validity'] = 'temp'

st.set_page_config(page_title='Environment Care', page_icon=':herb:')

if st.session_state['activate'] == True:

    if st.session_state['op'] == 'Logout':
        def loginLayout():
            def login(e, p):
                try:
                    user = auth.sign_in_with_email_and_password(e, p)
                    st.success('Login successful')
                    st.session_state['user'] = user
                    st.session_state['email'] = email
                    st.session_state['password'] = password
                    st.session_state['op'] = 'Home'
                except:
                    st.error('Incorrect email or password')
                    time.sleep(2)

            email = st.text_input('Email', placeholder='Type your email here')
            password = st.text_input('Password', placeholder='Type your password here', type='password')
            lB = st.button('Login')
            if lB:
                login(email, password)
                st.rerun()

        def signupLayout():
            def signup(e, p, u):
                try:
                    user = auth.create_user_with_email_and_password(e, p)
                    st.success('Sign up successful')
                    st.info('Now login to continue ')
                    db.child(user['localId']).child('ID').set(user['localId'])
                    db.child(user['localId']).child('Handle').set(u)

                except:
                    st.error('Unsuccessful sign up')

            email = st.text_input('Email', placeholder='Type your email here')
            password = st.text_input('Password', placeholder='Type your password here', type='password')
            username = st.text_input('Username', placeholder='Type your username here')
            sB = st.button('Sign Up')
            if sB:
                signup(email, password, username)


        st.title('Account Portal')
        if st.session_state['choice'] == False:
            loginLayout()
        else:
            signupLayout()

        choice = st.checkbox('Create new account', key='choice')

    if st.session_state['op'] == 'My Account' or st.session_state['op'] == 'Search' or \
            st.session_state['op'] == 'Leaderboard' or \
            st.session_state['op'] == 'Home' or st.session_state['op'] == 'Forums':
        user = st.session_state['user']
        col1, col2 = st.columns([0.8, 0.2], gap='large')
        with col1:
            st.title('Welcome {}'.format(db.child(st.session_state['user']['localId']).child('Handle').get().val()))
        op = st.radio('Go to', ['Home', 'Search', 'Leaderboard', 'Forums', 'My Account', 'Logout'], horizontal=True, key='op')

    if st.session_state['op'] == 'My Account':
        user = st.session_state['user']
        newImage = db.child(user['localId']).child("Image").get().val()

        if newImage is not None:
            col1, col2 = st.columns(2, gap='large')
            with col1:
                st.image(newImage, use_column_width='always', caption='My profile picture')
            with col2:
                st.metric('Name', '{}'.format(db.child(st.session_state['user']['localId']).child('Handle').get().val()))
                v = len(db.child(user['localId']).child("Posts").get().val())
                st.metric('Posts', '{}'.format(v), '+{}'.format(v))
            exp = st.expander('Edit profile')
            with exp:
                newImgPath = st.file_uploader('Image upload', type=['png', 'jpg'])
                upload_new = st.button('Upload')
                if upload_new:
                    uid = user['localId']
                    fireb_upload = storage.child(uid).child('Image').put(newImgPath)
                    a_imgdata_url = storage.child(uid).child('Image').get_url(fireb_upload)
                    db.child(uid).child("Image").set(a_imgdata_url)
                    st.success('Success!')
                    st.rerun()
                newName = st.text_input('Name', value='{}'.format(
                    db.child(st.session_state['user']['localId']).child('Handle').get().val()))
                name_up = st.button('Submit')
                if name_up:
                    uid = user['localId']
                    db.child(uid).child('Handle').set(newName)
                    st.success('Success!')
                    st.rerun()

        else:
            col1, col2 = st.columns(2, gap='large')
            with col1:
                st.info("No profile picture yet")
            with col2:
                st.metric('Name',
                          '{}'.format(db.child(st.session_state['user']['localId']).child('Handle').get().val()))
                try:
                    v = len(db.child(user['localId']).child("Posts").get().val())
                    st.metric('Posts', '{}'.format(v), '+{}'.format(v))
                except:
                    pass
            newImgPath = st.file_uploader('Image upload', type=['png', 'jpg'])
            upload_new = st.button('Upload')
            if upload_new:
                uid = user['localId']
                fireb_upload = storage.child(uid).child('Image').put(newImgPath)
                a_imgdata_url = storage.child(uid).child('Image').get_url(fireb_upload)
                db.child(uid).child("Image").set(a_imgdata_url)
                st.success('Success!')
                st.rerun()

    if st.session_state['op'] == 'Search':
        all_users = db.get()
        usrs = []
        for users_handle in all_users.each():
            k = users_handle.val()["Handle"]
            usrs.append(k)

        st.write('User count: ' + str(len(usrs)))

        choice = st.selectbox('Select users', usrs)
        push = st.button('Show Profile')

        if push:
            for users_handle in all_users.each():
                k = users_handle.val()["Handle"]

                if k == choice:
                    uid = users_handle.val()["ID"]
                    handlename = db.child(uid).child("Handle").get().val()

                    nImage = db.child(uid).child("Image").get().val()
                    if nImage is not None:
                        col1, col2, col3 = st.columns(3, gap='large')
                        with col2:
                            st.image(nImage, use_column_width='always', caption=handlename)
                    else:
                        st.info("No profile picture yet.")

                    all_posts = db.child(uid).child("Posts").get()
                    st.write('##### Posts')
                    if all_posts.val() is not None:
                        for posts in reversed(all_posts.each()):
                            with st.container():
                                st.image(posts.val()['pics'], caption="{}: {}".format(posts.val()['Timestamp'],
                                                                    posts.val()['Post']), use_column_width='always')

    if st.session_state['op'] == 'Home':
        user = st.session_state['user']

        exp = st.expander('New post')
        with exp:
            img = st.file_uploader("Upload image", type=['png', 'jpg'])
            try:
                if img.getvalue():
                    with st.spinner('Validating with AI...'):
                        validity = checkImage.get_validation(img)
                        st.session_state['validity'] = str(validity.text).lower().strip()
            except:
                pass

            #st.write(st.session_state)
            if st.session_state['validity'] == 'yes':
                st.session_state['validity'] = 'temp'
                st.success('Image accepted')
                st.image(img, use_column_width=True)
                post = st.text_input("Describe your work")
                add_post = st.button('Share')
                if add_post:
                    now = datetime.datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    post = {'Post': post,
                            'Timestamp': dt_string}
                    results = db.child(user['localId']).child("Posts").push(post)

                    x = storage.child(user['localId']).child('Posts').child(results['name']).child('pics').put(img)
                    url = storage.child(user['localId']).child('Posts').child(results['name']).child('pics').get_url(x)
                    db.child(user['localId']).child('Posts').child(results['name']).child('pics').set(url)

                    st.balloons()
                    st.rerun()
            if st.session_state['validity'] == 'no':
                st.warning('Image not accepted')

        # HOME FEED
        data = {}
        ids = db.get().val().keys()
        for i in ids:
            j = db.child(i).child('Posts').get()
            k = db.child(i).child('Handle').get().val()
            try:
                for x in j.val().keys():
                    z = db.child(i).child('Posts').child(x).get().val()
                    z['Handle'] = k
                    data[db.child(i).child('Posts').child(x).get().val()['Timestamp']] = z
            except:
                pass
            try:
                for k in j.each():
                    temp = j[k]
                    temp['Handle'] = db.child(i).child('Handle').get().val()
                    data[j[k]['Timestamp']] = temp
            except:
                pass

        sdata = sorted(data.keys(), reverse=True)
        for i in sdata:
            h = data[i]['Handle']
            p = data[i]['Post']
            t = data[i]['Timestamp']
            pic = data[i]['pics']
            st.image(pic, caption="{}-{}: {}".format(t, h, p), use_column_width='always')

    if st.session_state['op'] == 'Leaderboard':
        leaderboard = {}
        l = db.get().val()
        for i in l:
            try:
                leaderboard[l[i]['Handle']] = len(l[i]['Posts'])
            except:
                leaderboard[l[i]['Handle']] = 0
        keys = list(leaderboard.keys())
        values = list(leaderboard.values())
        sorted_value_index = np.argsort(values)
        sorted_dict = {keys[i]: values[i] for i in sorted_value_index}
        sorted_dict = dict(reversed(list(sorted_dict.items())))
        for i in sorted_dict.items():
            col1, col2 = st.columns([0.9, 0.1], gap='large')
            with col1:
                st.info(i[0])
            with col2:
                st.info(i[1])

    if st.session_state['op'] == 'Forums':
        db.child('Forums')
        col1, col2 = st.columns([0.8, 0.2])
        #with col1:
            #st.selectbox('Available topics')
        with col2:
            nForum = st.button('Create new')
            if nForum:
                db.child('Forums').set('Sample')
            st.write(db.get().val())
            
