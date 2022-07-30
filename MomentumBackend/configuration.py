import os
from pathlib import Path

class Configuration:
  __DEFENITION = {
    "EMAIL_ADDRESS": {
      "type": str,
      "required": True,
      "help": "The email address the server will use to send emails.",
    },
    "EMAIL_PASSWORD": {
      "type": str,
      "required": True,
      "help": "The password of the email address the server will use to send emails.",
    },
    "EMAIL_HOST": {
      "type": str,
      "required": True,
      "help": "The host of the email server.",
    },
    "EMAIL_PORT": {
      "type": int,
      "required": False,
      "help": "The port of the email server.",
      "default": 587,
    },
    "ADMIN_USERNAME": {
      "type": str,
      "required": False,
      "help": "The username of the default admin account.",
      "default": "admin",
    },
    "ADMIN_PASSWORD": {
      "type": str,
      "required": False,
      "help": "The password of the default admin account.",
      "default": "admin",
    },
    "TRAINER_USERNAME": {
      "type": str,
      "required": False,
      "help": "The username of the default trainer account.",
      "default": "trainer",
    },
    "TRAINER_PASSWORD": {
      "type": str,
      "required": False,
      "help": "The password of the default trainer account.",
      "default": "trainer",
    },
    "USER_USERNAME": {
      "type": str,
      "required": False,
      "help": "The username of the default user account.",
      "default": "user",
    },
    "USER_PASSWORD": {
      "type": str,
      "required": False,
      "help": "The password of the default user account.",
      "default": "user",
    },
    "DATABASE_USE_POSTGRESQL": {
      "type": bool,
      "required": False,
      "help": "Whether to use Postgres or the fallback SQLITE DB.",
      "default": "True",
    },
    "DATABASE_NAME": {
      "type": str,
      "required": "DATABASE_USE_POSTGRESQL",
      "help": "The name of the database.",
    },
    "DATABASE_USER": {
      "type": str,
      "required": "DATABASE_USE_POSTGRESQL",
      "help": "The username of the database.",
    },
    "DATABASE_PASSWORD": {
      "type": str,
      "required": "DATABASE_USE_POSTGRESQL",
      "help": "The password of the database.",
    },
    "DATABASE_HOST": {
      "type": str,
      "required": "DATABASE_USE_POSTGRESQL",
      "help": "The host of the database.",
    },
    "DATABASE_PORT": {
      "type": int,
      "required": "DATABASE_USE_POSTGRESQL",
      "help": "The port of the database.",
    },
    "VIDEO_PATH": {
      "type": Path,
      "required": True,
      "help": "The relative path to store video files.",
    },
    "ALLOWED_ORIGINS": {
      "type": list,
      "required": True,
      "help": "The allowed origins of the server.",
    },
    "ALLOWED_HOSTS": {
      "type": list,
      "required": True,
      "help": "The allowed hosts of the server.",
    },
    "DEBUG": {
      "type": bool,
      "required": False,
      "help": "Whether the server is in debug mode.",
      "default": "False",
    }
  }

  def verify():
    # load data from environment variables
    # 1. evaluate all variables
    correctness = True
    data = {}
    for key, definition in Configuration.__DEFENITION.items():
      # set default value
      value = definition["default"] if "default" in definition else None
      # load real data if available
      value = os.environ[key] if key in os.environ else value
      # cast to correct type
      try:
        if value == None:
          pass
        elif definition["type"] == str:
          value = str(value)
        elif definition["type"] == int:
          value = int(value)
        elif definition["type"] == Path:
          Path(value)
        elif definition["type"] == list:
          value = value.split(",")
        elif definition["type"] == bool:
          value = value.lower() == "true"
      except Exception:
        print(f"[ERROR] Invalid type for configuration key {key}: {value}")
        print(f"        Help: {definition['help']}")
        correctness = False
      
      data[key] = value

    # 2. check if all required variables are set
    for key, definition in Configuration.__DEFENITION.items():
      if (value is None and definition["required"] and
            (type(definition["required"]) == bool or 
            (type(definition["required"]) == str and
            data[definition["required"]]))):
        print(f"[ERROR] Missing required variable: {key}")
        print(f"        Help: {definition['help']}")
        correctness = False

    return data if correctness else False

  def load():
    data = Configuration.verify()
    if not data:
      print("Configuration is incorrect or incomplete.")
      exit(1)
    
    conf = {
      "email_address": data["EMAIL_ADDRESS"],
      "email_password": data["EMAIL_PASSWORD"],
      "email_smtp_server": data["EMAIL_HOST"],
      "email_smtp_port": data["EMAIL_PORT"],
      "admin_username": data["ADMIN_USERNAME"],
      "admin_password": data["ADMIN_PASSWORD"],
      "trainer_username": data["TRAINER_USERNAME"],
      "trainer_password": data["TRAINER_PASSWORD"],
      "user_username": data["USER_USERNAME"],
      "user_password": data["USER_PASSWORD"],
      "database": {
          "name": data["DATABASE_NAME"],
          "user": data["DATABASE_USER"],
          "password": data["DATABASE_PASSWORD"],
          "host": data["DATABASE_HOST"],
          "port": data["DATABASE_PORT"],
      },
      "video_dir": data["VIDEO_PATH"],
      "allowed_origins": data["ALLOWED_ORIGINS"],
      "allowed_hosts": data["ALLOWED_HOSTS"],
      "debug": data["DEBUG"],
      "use_postgres": data["DATABASE_USE_POSTGRESQL"],
    }
    return conf