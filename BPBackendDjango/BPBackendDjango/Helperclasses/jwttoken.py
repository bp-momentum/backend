from jwcrypto import jwt, jwk
import json
import time
import hashlib
from ..models import User
from pathlib import Path

from ..settings import TOKEN_KEY
from ..models import *
from ..serializers import *

def check_tokentime(token_time, seconds):
    now = int(time.time())
    age = now - token_time
    if age < 0:
        return False
    if age < seconds:
        return True
    return False

def check_tokentype(token_type, compare):
    return token_type == compare

def check_refreshpswd(username, refreshpswd):
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
    elif Trainer.objects.filter(username=username).exists():
        user = Trainer.objects.get(username=username)
    elif Admin.objects.filter(username=username).exists():
        user = Admin.objects.get(username=username)
    else:
        return False
    return user.refresh_token == refreshpswd

def get_pswd(username):
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
    elif Trainer.objects.filter(username=username).exists():
        user = Trainer.objects.get(username=username)
    elif Admin.objects.filter(username=username).exists():
        user = Admin.objects.get(username=username)
    else:
        return None
    return user.refresh_token



class JwToken(object):
    
    @staticmethod
    def create_session_token(username, account_type):

        key = jwk.JWK(**TOKEN_KEY)

        #sign token
        signed_token = jwt.JWT(header={"alg": "HS256"}, claims={"username": username, "tokentime": int(time.time()), "account_type": account_type, "tokentype": "session"})
        signed_token.make_signed_token(key)

        #encrypt the token
        #token = jwt.JWT(header={"alg": "A256KW", "enc": "A256CBC-HS512"}, claims=signed_token.serialize())
        #token.make_encrypted_token(key)
        return signed_token.serialize()

    @staticmethod
    def check_session_token(token):          
        key = jwk.JWK(**TOKEN_KEY)
        
        #decrypt token
        # try:
        #     ET = jwt.JWT(key=key, jwt = token)
        # except:
        #     print("Decryption failed")
        #     return False, ""

        #check validation
        try:
            ST = jwt.JWT(key=key, jwt = token)
        except:
            print("Signature is not valid")
            return {"valid": False, "info": {}}
        #check if the token is still valid (1 day) and of right type
        info = json.loads(str(ST.claims))

        # check if token is a session token
        if not check_tokentype(info['tokentype'], "session"):
            return {"valid": False, "info": {}}

        # check if token is not older than 24 hours
        if not check_tokentime(info['tokentime'], 86400):
            return {"valid": False, "info": {}}

        #check if token didnt got invalidated
        if User.objects.filter(username=info["username"]).exists():
            user = User.objects.get(username=info["username"])
        elif Trainer.objects.filter(username=info["username"]).exists():
            user = Trainer.objects.get(username=info["username"])
        elif Admin.objects.filter(username=info["username"]).exists():
            user = Admin.objects.get(username=info["username"])
        else:
            return {"valid": False, "info": {}}

        if user.token_date - info['tokentime'] >= 0:
            return {"valid": False, "info": {}}

        return {"valid": True, "info": {"username": info["username"], "account_type": info["account_type"]}}

    @staticmethod
    def create_new_user_token(initiator, first_name, last_name, email_address, create_account_type):

        key = jwk.JWK(**TOKEN_KEY)

        #sign token
        signed_token = jwt.JWT(header={"alg": "HS256"}, claims={"first_name": first_name,
            "last_name": last_name, "email_address": email_address,
            "tokentime": int(time.time()), "create_account_type": create_account_type, "initiator": initiator})
        
        signed_token.make_signed_token(key)

        #encrypt the token
        #token = jwt.JWT(header={"alg": "A256KW", "enc": "A256CBC-HS512"}, claims=signed_token.serialize())
        #token.make_encrypted_token(key)
        return signed_token.serialize()

    def check_new_user_token(token):
        key = jwk.JWK(**TOKEN_KEY)
        
        #decrypt token
        # try:
        #     ET = jwt.JWT(key=key, jwt = token)
        # except:
        #     print("Decryption failed")
        #     return False, ""

        #check validation
        try:
            ST = jwt.JWT(key=key, jwt = token)
        except:
            print("Signature is not valid")
            return {"valid": False, "info": {}}
        #check if the token is still valid (14 day)
        info = json.loads(str(ST.claims))
        
        if not check_tokentime(info['tokentime'], 1209600):
            return {"valid": False, "info": {}}

        return  {"valid": True, "info": {"initiator": info["initiator"], "first_name": info["first_name"], "last_name": info["last_name"], "email_address": info["email_address"], "create_account_type": info["create_account_type"]}}    

    @staticmethod
    def create_refresh_token(username, account_type, set_pswd):
        #load key
        key = jwk.JWK(**TOKEN_KEY)

        #sign token
        pswd = get_pswd(username)
        if(set_pswd or pswd == None):
            pswd = JwToken.create_refreshpswd(username, int(time.time()))
            signed_token = jwt.JWT(header={"alg": "HS256"}, claims={"username": username, "tokentime": int(time.time()), "account_type": account_type, "tokentype": "refresh", "refreshpswd": pswd})
            JwToken.save_refreshpswd(username, pswd)
        else:
            signed_token = jwt.JWT(header={"alg": "HS256"}, claims={"username": username, "tokentime": int(time.time()), "account_type": account_type, "tokentype": "refresh", "refreshpswd": pswd})
        signed_token.make_signed_token(key)

        return signed_token.serialize()

    @staticmethod
    def check_refresh_token(token):
        #load key
        key = jwk.JWK(**TOKEN_KEY)

        #check validation
        try:
            ST = jwt.JWT(key=key, jwt = token)
        except:
            print("Signature is not valid")
            return {"valid": False, "info": {}}
        #check if the token is still valid (30 days), of right type and pswd is valid
        info = json.loads(str(ST.claims))
        
        if not check_tokentype(info['tokentype'], "refresh"):
            return {"valid": False, "info": {}}

        if not check_tokentime(info['tokentime'], 2592000):
            return {"valid": False, "info": {}}

        if not check_refreshpswd(info['username'], info['refreshpswd']):
            return {"valid": False, "info": {}}

        return  {"valid": True, "info": {"username": info["username"], "account_type": info["account_type"]}}

    @staticmethod
    def save_refreshpswd(username, pswd):
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
        elif Trainer.objects.filter(username=username).exists():
            user = Trainer.objects.get(username=username)
        elif Admin.objects.filter(username=username).exists():
            user = Admin.objects.get(username=username)
        else:
            return False
        user.refresh_token = pswd
        user.save(force_update=True)
        return True

    @staticmethod
    def create_refreshpswd(username, time):
        uhstr = username + str(time)
        hstr = str(hashlib.sha3_256(uhstr.encode('utf8')).hexdigest())
        return hstr

    @staticmethod
    def invalidate_session_token(username):
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
        elif Trainer.objects.filter(username=username).exists():
            user = Trainer.objects.get(username=username)
        elif Admin.objects.filter(username=username).exists():
            user = Admin.objects.get(username=username)
        else:
            return
        user.token_date = int(time.time())-10
        user.save(force_update=True)









        