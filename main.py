from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

app = FastAPI()

class EmailRequest(BaseModel):
    subject: str
    to_email: str
    message: str
    html_body: str = None  # Optional HTML body

def send_email(request: EmailRequest):
    try:
        credentials = Credentials.from_authorized_user_info(
            {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "refresh_token": REFRESH_TOKEN}
        )

        service = build("gmail", "v1", credentials=credentials)
        
        if request.html_body:
            message = MIMEMultipart("alternative")
            message.attach(MIMEText(request.message, "plain"))
            message.attach(MIMEText(request.html_body, "html"))
        else:
            message = MIMEText(request.message)
        
        message["to"] = request.to_email
        message["subject"] = request.subject
        message = message.as_string()
        
        raw_message = {"raw": base64.urlsafe_b64encode(message.encode("utf-8")).decode("utf-8")}
        
        service.users().messages().send(userId="me", body=raw_message).execute()

        return {"message": "Email sent successfully"}
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@app.post("/send_email/")
async def send_email_request(request: EmailRequest):
    return send_email(request)

class BulkEmailRequest(BaseModel):
    subject: str
    recipients: list
    message: str
    html_body: str = None  # Optional HTML body

def send_bulk_email(request: BulkEmailRequest):
    try:
        credentials = Credentials.from_authorized_user_info(
            {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "refresh_token": REFRESH_TOKEN}
        )

        service = build("gmail", "v1", credentials=credentials)
        
        if request.html_body:
            message = MIMEMultipart("alternative")
            message.attach(MIMEText(request.message, "plain"))
            message.attach(MIMEText(request.html_body, "html"))
        else:
            message = MIMEText(request.message)
        
        message["subject"] = request.subject

        for recipient in request.recipients:
            msg = message
            msg["to"] = recipient
            msg = msg.as_string()
            raw_message = {"raw": base64.urlsafe_b64encode(msg.encode("utf-8")).decode("utf-8")}
            service.users().messages().send(userId="me", body=raw_message).execute()

        return {"message": "Bulk emails sent successfully"}
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Failed to send bulk emails: {str(e)}")

@app.post("/send_bulk_email/")
async def send_bulk_email_request(request: BulkEmailRequest):
    return send_bulk_email(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
