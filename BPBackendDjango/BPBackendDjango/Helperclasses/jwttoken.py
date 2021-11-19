from jwcrypto import jwt, jwk
import json
import time
from pathlib import Path



def check_tokentime(token_time):
    now = int(time.time())
    age = now - token_time
    if now - token_time < 86400:
        return True
    return False



class JwToken(object):
    
    @staticmethod
    def create_session_token(username):
        #load key
        if not Path("/root/BachelorPraktikum/jw_key.json").is_file():   
            print("Erstelle Key File")
            key = jwk.JWK(generate='oct', size=256)
            json.dump(key, open("jw_key.json", "w"))

            
        key_dict = json.load(open("/root/BachelorPraktikum/jw_key.json"))
        key = jwk.JWK(**key_dict)

        #sign token
        signed_token = jwt.JWT(header={"alg": "HS256"}, claims={"username": username, "tokentime": int(time.time())})
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
            return False, ""
        #check if the token is still valid (1 day)
        info = json.loads(str(ST.claims))
        
        if not check_tokentime(info['tokentime']):
            return False, info['username']

        return True, info['username']

    