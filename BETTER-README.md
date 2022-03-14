### Deployment

#### Database
To create a PostgreSQL database, please refer to this very useful [guide](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart-de).

#### Entrypoint
Inside the `BPBackendDjango` directory, you will find a file called `manage.py`. This is the main entrypoint for all operations with
this Django backend server.

#### Configuration
To create a default configuration, please start the server once, by running `python3 manage.py runserver <host-address>:<port>`.
After that you will find a newly created `settings.json` file inside the directory. Now you can open the file and enter you configuration.
You don't have to fill in the `token_key` object inside the json, as it will be created automatically upon the first server start.

First you have to give the information for the email-service. Here you need to give your email address, your password and the 
smtp server (for gmail: smtp.gmail.com). Then you can change the standard admin trainer and user
details. These users will created only once when you firstly start the server. 

Now you have to give the database information which you defined while creating 
the database. "name" is here the database name, which you want to use and must du already created.

"Video_dir" is the relative path to the video folder, where the videos are stored.

The secret key doesn't have to be changed. This is a random 16 long string.


The allowed origins are the urls from where the server can be reached.
Here you should give the frontend url and maybe the localhost addresses for testing.
For the website url you have to give the url of the frontend.

last_leaderboard_reset should not be changed


#### Starting the Server
After configuration, please start the server by running `python3 manage.py runserver <host-address>:<port>` again.
If there are any issues with your settings, you will see errors in the output. After successfully starting the server, it will
be reachable at your `<host-address>:<port>`. The admin panel will be reachable at `<host-address>:<port>/admin`.
As an example you can type the command "python manage.py runserver 0.0.0.0:8000"

Now the database will be adjusted, and the tables will be created and the server can be reached by the frontend.