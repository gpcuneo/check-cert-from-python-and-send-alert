from socket import socket
from OpenSSL import SSL
from datetime import datetime
import idna
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

smtpServer = 'smtp.gmail.com'
smtpPort = 465
login = 'email@gmail.com'
password = 'password'

listSites = ['site1.com' , 'site2.com', 'site3.com']
port = 443
now = datetime.now()
limitDays = 15

def sendMail(site, days):
    msg = MIMEMultipart("alternative")
    msg['From'] = login # in this case the sender email it's the same as login email.
    msg['To'] = 'destinatary@gmail.com'
    msg['Subject'] = f"Alert for expire cert from {site}"
    html = f"""\
        <html>
            <body>
                <p>The cert of {site} it is aboute to expire </br>
                Remain {days} days for expire.
                </p>
            <html>
        <body>"""
    body = MIMEText(html, "html")
    msg.attach(body)
    with smtplib.SMTP_SSL(smtpServer, smtpPort) as server:
        server.login(login, password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())

def getCert(site, port):
    sock = socket()
    sock.connect((site, port), )
    context = SSL.Context(SSL.SSLv23_METHOD)
    sock_ssl = SSL.Connection(context, sock)
    sock_ssl.set_tlsext_host_name(idna.encode(site)) 
    sock_ssl.set_connect_state()
    sock_ssl.do_handshake()
    cert = sock_ssl.get_peer_certificate()
    sock_ssl.close()
    sock.close()
    return cert

for site in listSites:
    cert = getCert(site, port)
    expiration = cert.get_notAfter().decode('ascii')
    expirationDate = datetime.strptime(expiration, '%Y%m%d%H%M%SZ')
    daysToDie = (expirationDate - now).days
    if daysToDie < limitDays:
        sendMail(site, daysToDie)
    else:
        print("The cert of " + site + " its ok.")
