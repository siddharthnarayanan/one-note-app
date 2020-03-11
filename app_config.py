import os

CLIENT_ID = ""
CLIENT_SECRET = ""
AUTHORITY = "https://login.microsoftonline.com/common"

REDIRECT_PATH = "/getAToken"  

ENDPOINT = 'https://graph.microsoft.com/v1.0/users' 
GET_NOTEBOOKS_ENDPOINT = 'https://graph.microsoft.com/v1.0/me/onenote/notebooks' 
GET_SECTIONS_ENDPOINT = 'https://graph.microsoft.com/v1.0/me/onenote/sections' 
GET_PAGES_ENDPOINT = 'https://graph.microsoft.com/v1.0/me/onenote/pages?$select=title,contentUrl'  

SCOPE = ["Notes.Read"]

SESSION_TYPE = "filesystem"  


