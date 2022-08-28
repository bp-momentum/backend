<h1 align="center">
  <img src=".preview/Logo.png" width="250"><br>
  Momentum Backend
</h1>

<div align="center">
  
  [![GitHub license](https://img.shields.io/github/license/bp-momentum/backend.svg)](https://github.com/bp-momentum/backend/blob/main/LICENSE)
  [![GitHub commits](https://badgen.net/github/commits/bp-momentum/backend/main)](https://GitHub.com/bp-momentum/backend/commit/)
  [![Github stars](https://img.shields.io/github/stars/bp-momentum/backend.svg)](https://GitHub.com/bp-momentum/backend/stargazers/)
  [![Deploy](https://img.shields.io/github/workflow/status/bp-momentum/backend/Deploy)](https://github.com/bp-momentum/backend/actions/workflows/deploy.yml)

</div>

## Setup

### Database
When developing you can simply rely on SQLite.
For deployment you will need to use a database server.
Please refer to the [documentation](https://github.com/bp-momentum/documentation) for more information.

### Entrypoint
You will find a file called `manage.py`. This is the main entrypoint for all operations with this Django backend server.

### Configuration
The configuration is done through environment variables.

The following environment variables are available:

| Variable | Required <> Default Value | Description |
| --- | --- | --- |
|EMAIL_ADDRESS|Required|The email address the server will use to send emails.|
|EMAIL_PASSWORD|Required|The password of the email address the server will use to send emails.|
|EMAIL_HOST|Required|The host of the email server.|
|EMAIL_PORT|`587`|The port of the email server.|
|ADMIN_USERNAME|`admin`|The username of the default admin account.|
|ADMIN_PASSWORD|`admin`|The password of the default admin account.|
|TRAINER_USERNAME|`trainer`|The username of the default trainer account.|
|TRAINER_PASSWORD|`trainer`|The password of the default trainer account.|
|USER_USERNAME|`user`|The username of the default user account.|
|USER_PASSWORD|`user`|The password of the default user account.|
|DATABASE_USE_POSTGRESQL|`true`|Whether to use PostgreSQL or SQLite.|
|DATABASE_NAME|Required|The name of the database.|
|DATABASE_USER|Required|The username of the database.|
|DATABASE_PASSWORD|Required|The password of the database.|
|DATABASE_HOST|Required|The host of the database.|
|DATABASE_PORT|Required|The port of the database.|
|VIDEO_PATH|Required|The relative path to store videos files.|
|ALLOWED_ORIGINS|Required|The allowed origins of the server as a comma separated list.|
|ALLOWED_HOSTS|Required|The allowed hosts of the server as a comma separated list.|
|DEBUG|`False`|Whether the server is running in debug mode.|
|AI_URL|Required|The URL of the AI server.|

`VIDEO_PATH` is the relative path to the video folder, where video recordings may be stored.

`ALLOWED_ORIGINS` are the urls that can be used to refer to the server.
This should contain the frontend url and for testing possibly `localhost` and similar.

`ALLOWED_HOSTS` are the hosts that the server listens to.
If run behind a reverse proxy this should contain the address behind the proxy.

`WEBSITE_URL` needs to be the url of the frontend.
This is used to generate links sent by email to users.

`DATABASE_USE_POSTGRESQL` should only be set for testing purposes. For production, PostgreSQL should always be preferred.

### Starting the Server
Before you can start the server you need to set at least the required environment variables.

Before the first start of the server, the tables must be created in the database.
To do that, run
```bash
python3 manage.py makemigrations
```
and
```bash
python3 manage.py migrate
```
This will automatically adjust the database and create all missing tables.
Now, the database is ready to be used.

After configuration, you can start the server by running
```bash
python3 manage.py runserver <host-address>:<port>
```
If there are any issues with your settings, you will see errors in the output. After successfully starting the server, it will
be reachable at the `<host-address>:<port>` you specified.
As an example you can type the command `python3 manage.py runserver 0.0.0.0:8000`
Make sure the host and port configuration you use is part of the `ALLOWED_HOSTS` variable.

Now the server can be reached by the frontend if the ports are allowed in the firewall.
