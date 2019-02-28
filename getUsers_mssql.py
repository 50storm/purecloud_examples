import base64, requests, sys, logging, pyodbc
import PureCloudPlatformClientV2
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
logging.debug("debugging start.")
""" 
 pyodbcのインストール
 pip install pyodbc
 ODBC データソースを作成（ユーザーDNS）する。(手動)　 https://www.ipentec.com/document/windows-create-odbc-data-source-for-sql-server
"""


engine = create_engine("mssql+pyodbc://hiroshi:hiro1128@seatmap")
db = scoped_session(sessionmaker(bind=engine))

# purecloud_user_id=""
# username=""
sqlInsertt = "INSERT INTO users ( purecloud_user_id, username, created_at, updated_at )VALUES( :purecloud_user_id, :username ,current_timestamp, NULL ) "


clientId = "XXXXXXXXXXXXXXXXXXXXXXXXX"
clientSecret = "XXXXXXXXXXXXXXXXXXXXXXXX"

token= clientId + ":" + clientSecret
authorization  =  base64.urlsafe_b64encode(token.encode('UTF-8')).decode('ascii')

# Prepare for POST /oauth/token request
requestHeaders = {
	'Authorization': 'Basic ' + authorization,
	'Content-Type': 'application/x-www-form-urlencoded'
}
requestBody = {
	'grant_type': 'client_credentials'
}

# Get token
response = requests.post('https://login.mypurecloud.jp/oauth/token', data=requestBody, headers=requestHeaders)

# Check response
if response.status_code == 200:
	print ('Got token')
	print (response)
	# print (response["access_token"])
    
else:
	print ( ' Failure: ' + str(response.status_code) + ' - ' + response.reason)
	sys.exit(response.status_code)

# Get JSON response body
responseJson = response.json()

print(responseJson) #{'access_token': 'PRaoxzKvLY75kbuYMBKZuqDP0OW5b89aBgz_kR93kufIQ-r582OPFr3CrzbsmolrdFZItMoKz_YHF9G0FXq6UA', 'token_type': 'bearer', 'expires_in': 86399}
print(responseJson['access_token'])

# Prepare for GET /api/v2/authorization/roles request
requestHeaders = {
	'Authorization': responseJson['token_type'] + ' ' + responseJson['access_token']
}

PureCloudPlatformClientV2.configuration.access_token = responseJson['access_token']
PureCloudPlatformClientV2.configuration.host = 'https://api.mypurecloud.jp'
usersApi = PureCloudPlatformClientV2.UsersApi()
print("====getUsers====")
users = usersApi.get_users()

for user in users.entities :
    print(user.id)
    print(user.name)
    resultInsert = db.execute(sqlInsertt, {"purecloud_user_id":user.id, "username":user.name} )
    
db.commit()
db.close()