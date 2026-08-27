Created 2026 August 27th

Steps
    first you must install the google authentication to log into youtube (pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client )
    Another install to connect to the google cloud (pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client)
        python -m pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
            check using (python3 -m pip show google-auth-oauthlib)

    create 2 files "client_secret.json" and requiremtns .txt file and fill the requirements text file with 
        "google-auth-oauthlib>=1.2.0
        google-auth-httplib2>=0.2.0
        google-api-python-client>=2.100.0"
    Google cloud
        look it up in google
        go to overview and click Try agent platform, then new project in the top right corner, and create it
        click the 3 bars in the top left and go to  api and services, library
        look up youtube and click on Youtube API v3 and enable it
        then go to Oauth consent screen which should appear on the left
        get started by adding a name, your email, external audience (a certain list of users can use it, add the account you want to use)
        add the account details in the Audience section under Test users
        go back to the API and Services and go to Credentials and create Credentials for a Oauth client ID
        probably just go with desktop app and name it whatever you want (these credentials are now only for the test users you setup previously)
        in the clients section click on the name of the client you just made, and then download its file, and put its contents or make it the file of client_secret.json
    next attempt to run it and resolve any issues (liekly with if your python has the correct installs to run the code) otherwise It will being running
    It will prompt you to log in with a google account (the test user you added previously), and once logged in it will return to the terminal
        







optimization methods
    storing list of all songs from their initial call in cache 


required to have
    vs Code with python
    a google cloud account
    a youtube account with playlists

running
    you will type in python (filename currently "Playlist_editor.py") 
    note that a token.json will be created when you do this

Inputs
    to select a playlst to edit, choose the number that is beside the name of the playlists

