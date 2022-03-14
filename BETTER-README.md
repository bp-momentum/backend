### Deployment

#### Database
To create a PostgreSQL database, please refer to this very useful [guide](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart-de).

#### Entrypoint
Inside the `BPBackendDjango` directory, you will find a file called `manage.py`. This is the main entry point for all operations with
this Django backend server.

#### Configuration
To create a default configuration, please start the server once, by running `python3 manage.py runserver <host-address>:<port>`.
After that you will find a newly created `settings.json` file inside the directory. This file contains a newly created JWT Key,
with which all tokens will be signed, but you can also configure your own. Now you can open the file and enter you configuration.

#### Starting the Server
After configuration, please start the server by running `python3 manage.py runserver <host-address>:<port>` again.
If there are any issues with your settings, you will see errors in the output. After successfully starting the server, it will
be reachable at your `<host-address>:<port>`. The admin panel will be reachable at `<host-address>:<port>/admin`.
