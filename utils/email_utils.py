import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, sender_password, receiver_email, message):
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "Grocery Bill"
        
        # Attach message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login to account
        server.login(sender_email, sender_password)
        
        # Send email
        server.send_message(msg)
        
        # Close connection
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False