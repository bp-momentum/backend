from jwcrypto import jwt, jwk
import json
import time
from pathlib import Path



def check_tokentime(token_time, seconds):
    now = int(time.time())
    age = now - token_time
    if now - token_time < seconds:
        return True
    return False



class JwToken(object):
    
    @staticmethod
    def create_session_token(username, account_type):
        #load key
        if not Path("/root/BachelorPraktikum/jw_key.json").is_file():   
            print("Erstelle Key File")
            key = jwk.JWK(generate='oct', size=256)
            json.dump(key, open("jw_key.json", "w"))

            
        key_dict = json.load(open("/root/BachelorPraktikum/jw_key.json"))
        key = jwk.JWK(**key_dict)

        #sign token
        signed_token = jwt.JWT(header={"alg": "HS256"}, claims={"username": username, "tokentime": int(time.time()), "account_type": account_type})
        signed_token.make_signed_token(key)

        #encrypt the token
        #token = jwt.JWT(header={"alg": "A256KW", "enc": "A256CBC-HS512"}, claims=signed_token.serialize())
        #token.make_encrypted_token(key)
        return signed_token.serialize()

    @staticmethod
    def check_session_token(token):
        #load key
        if not Path("/root/BachelorPraktikum/jw_key.json").is_file():   
            print("Erstelle Key File")
            key = jwk.JWK(generate='oct', size=256)
            json.dump(key, open("jw_key.json", "w"))
        
        key_dict = json.load(open("/root/BachelorPraktikum/jw_key.json"))
        key = jwk.JWK(**key_dict)
        
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
        #check if the token is still valid (1 day)
        info = json.loads(str(ST.claims))
        
        if not check_tokentime(info['tokentime'], 86400):
            return {"valid": False, "info": {}}

        return  {"valid": True, "info": {"username": info["username"], "account_type": info["account_type"]}}

    @staticmethod
    def create_new_user_token(initiator, first_name, last_name, email_address, create_account_type):
        #load key
        if not Path("/root/BachelorPraktikum/jw_key.json").is_file():   
            print("Erstelle Key File")
            key = jwk.JWK(generate='oct', size=256)
            json.dump(key, open("jw_key.json", "w"))

            
        key_dict = json.load(open("/root/BachelorPraktikum/jw_key.json"))
        key = jwk.JWK(**key_dict)

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
        #load key
        if not Path("/root/BachelorPraktikum/jw_key.json").is_file():   
            print("Erstelle Key File")
            key = jwk.JWK(generate='oct', size=256)
            json.dump(key, open("jw_key.json", "w"))
        
        key_dict = json.load(open("/root/BachelorPraktikum/jw_key.json"))
        key = jwk.JWK(**key_dict)
        
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
        #check if the token is still valid (1 day)
        info = json.loads(str(ST.claims))
        
        if not check_tokentime(info['tokentime'], 1209600):
            return {"valid": False, "info": {}}

        return  {"valid": True, "info": {"initiator": info["initiator"], "first_name": info["first_name"], "last_name": info["last_name"], "email_address": info["email_address"], "create_account_type": info["create_account_type"]}}    


        