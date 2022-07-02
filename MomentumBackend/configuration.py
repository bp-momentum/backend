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
    "DATABASE_NAME": {
      "type": str,
      "required": True,
      "help": "The name of the database.",
    },
    "DATABASE_USER": {
      "type": str,
      "required": True,
      "help": "The username of the database.",
    },
    "DATABASE_PASSWORD": {
      "type": str,
      "required": True,
      "help": "The password of the database.",
    },
    "DATABASE_HOST": {
      "type": str,
      "required": True,
      "help": "The host of the database.",
    },
    "DATABASE_PORT": {
      "type": int,
      "required": True,
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
    "WEBSITE_URL": {
      "type": str,
      "required": True,
      "help": "The url of the website.",
    },
  }

  def verify():
    # load data from environment variables
    correctness = True
    for key, value in Configuration.__DEFENITION.items():
      if key not in os.environ and value["required"]:
        print(f"[ERROR] The environment variable '{key}' is required but not set.")
        print(f"        Help: {value['help']}")
        correctness = False
      elif not value["required"]:
        print(f"[WARNING] The environment variable '{key}' is not required and not set.")
        print(f"          Help: {value['help']}")
      elif key in os.environ:
        # verify type
        if value["type"] == list:
          if not isinstance(os.environ[key].split(","), list):
            print(f"[ERROR] The environment variable '{key}' is not a list.")
            print(f"        Help: {value['help']}")
            print(f"        Lists should always be separated by a comma.")
            correctness = False
        else:
          try: 
            value["type"](os.environ[key])
          except:
            print(f"[ERROR] The environment variable '{key}' is not of type '{value['type']}'.")
            print(f"        Help: {value['help']}")
            correctness = False
    return correctness

  def load():
    if not Configuration.verify():
      print("Configuration is incorrect or incomplete.")
      exit(1)
    
    conf = {
        "email_address": os.getenv("EMAIL_ADDRESS"),
        "email_password": os.getenv("EMAIL_PASSWORD"),
        "email_smtp_server": os.getenv("EMAIL_HOST"),
        "email_smtp_port": Configuration.__DEFENITION["EMAIL_PORT"]["default"] if not os.getenv("EMAIL_SMTP_PORT") else int(os.getenv("EMAIL_SMTP_PORT")),
        "admin_username": Configuration.__DEFENITION["ADMIN_USERNAME"]["default"] if not  os.getenv("ADMIN_USERNAME") else os.getenv("ADMIN_USERNAME"),
        "admin_password": Configuration.__DEFENITION["ADMIN_PASSWORD"]["default"] if not  os.getenv("ADMIN_PASSWORD") else os.getenv("ADMIN_PASSWORD"),
        "trainer_username": Configuration.__DEFENITION["TRAINER_USERNAME"]["default"] if not  os.getenv("TRAINER_USERNAME") else os.getenv("TRAINER_USERNAME"),
        "trainer_password": Configuration.__DEFENITION["TRAINER_PASSWORD"]["default"] if not  os.getenv("TRAINER_PASSWORD") else os.getenv("TRAINER_PASSWORD"),
        "user_username": Configuration.__DEFENITION["USER_USERNAME"]["default"] if not  os.getenv("USER_USERNAME") else os.getenv("USER_USERNAME"),
        "user_password": Configuration.__DEFENITION["USER_PASSWORD"]["default"] if not  os.getenv("USER_PASSWORD") else os.getenv("USER_PASSWORD"),
        "database": {
            "name": os.getenv("DATABASE_NAME"),
            "user": os.getenv("DATABASE_USER"),
            "password": os.getenv("DATABASE_PASSWORD"),
            "host": os.getenv("DATABASE_HOST"),
            "port": int(os.getenv("DATABASE_PORT")),
        },
        "video_dir": os.getenv("VIDEO_PATH"),
        "allowed_origins": os.getenv("ALLOWED_ORIGINS").split(","),
        "allowed_hosts": os.getenv("ALLOWED_HOSTS").split(","),
        "website_url": os.getenv("WEBSITE_URL"),
    }
    return conf