import smtplib
import configparser

config = configparser.ConfigParser()

config.read('./config.ini')
#
# password = config['email']['password']


def send_email(subject, body):
    # Replace the placeholders with your email and password
    sender_email = "barseghyangor8@gmail.com"
    # sender_password = password
    # receiver_email = "barseghyangor@outlook.com"
    #
    # message = f"Subject: {subject}\n\n{body}"
    #
    # with smtplib.SMTP("smtp.gmail.com", 587) as server:
    #     server.starttls()
    #     server.login(sender_email, sender_password)
    #     server.sendmail(sender_email, receiver_email, message)


if __name__ == '__main__':
    subject = 'Test Email'
    body = 'This is test email'
    send_email(subject, body)