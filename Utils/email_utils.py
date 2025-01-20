from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import request
from random import randint


def send_verification_email(database):
    try:
        conn_url = database.select('''SELECT content FROM cantina_administration.config WHERE name='SMTP_URL' ''', None,
                                   number_of_data=1)[0]
        conn_port = database.select('''SELECT content FROM cantina_administration.config WHERE name='SMTP_PORT' ''',
                                    None, number_of_data=1)[0]
        conn_email = database.select('''SELECT content FROM cantina_administration.config WHERE name='SMTP_EMAIL' ''',
                                     None, number_of_data=1)[0]
        conn_passwd = database.select('''SELECT content FROM cantina_administration.config 
        WHERE name='SMTP_PASSWORD' ''', None, number_of_data=1)[0]

        subject = database.select('''SELECT content FROM cantina_administration.config WHERE 
        name='MAIL_VERIFICATION_SUJET' ''', None, number_of_data=1)[0]
        message = database.select('''SELECT content FROM cantina_administration.config WHERE 
        name='MAIL_VERIFICATION_CONTENU' ''', None, number_of_data=1)[0]
        destinataire = database.select('''SELECT email, email_verified FROM cantina_administration.user 
        WHERE token = %s''', (request.cookies.get('token')), number_of_data=1)

        db_code = database.select('''SELECT email_verification_code FROM cantina_administration.user WHERE token = %s''',
                                  (request.cookies.get('token')), number_of_data=1)

    except TypeError:
        return 'error1: Configuration incomplète ou inexistante'

    if destinataire[1]:
        return 'already_check'

    if db_code is None or db_code[0] == 'reset':
        code = get_rand_num_for_email_verif()
        database.exec("""UPDATE cantina_administration.user SET email_verification_code = %s WHERE token = %s""",
                      (code, request.cookies.get('token')))
    else:
        code = database.select('''SELECT email_verification_code FROM cantina_administration.user WHERE token = %s''',
                               (request.cookies.get('token')), number_of_data=1)[0]

    if conn_url is None or conn_port is None or conn_email is None:
        return 'error1: Configuration incomplète ou inexistante.'

    if subject is None or message is None or subject == "" or message == "" or "{}" not in message:
        return 'error2: Message prédéfinis incomplet ou inexistant'

    mail = MIMEMultipart()
    mail['From'] = conn_email
    mail['To'] = destinataire[0]
    mail['Subject'] = subject
    try:
        content = MIMEText(message.format(code).encode('utf-8'), 'plain', 'utf-8')
        mail.attach(content)

        smtp_server = SMTP_SSL(conn_url, int(conn_port))
        smtp_server.ehlo()
        smtp_server.login(conn_email, conn_passwd)

        smtp_server.sendmail(conn_email, destinataire[0], mail.as_string())
        smtp_server.close()

        return 'success'
    except ValueError:
        return 'error1: Configuration incomplète ou inexistante'


def send_test_email(database):
    try:
        conn_url = database.select('''SELECT content FROM cantina_administration.config WHERE name='SMTP_URL' ''', None,
                                   number_of_data=1)[0]
        conn_port = database.select('''SELECT content FROM cantina_administration.config WHERE name='SMTP_PORT' ''',
                                    None, number_of_data=1)[0]
        conn_email = database.select('''SELECT content FROM cantina_administration.config WHERE name='SMTP_EMAIL' ''',
                                     None, number_of_data=1)[0]
        conn_passwd = database.select('''SELECT content FROM cantina_administration.config 
        WHERE name='SMTP_PASSWORD' ''', None, number_of_data=1)[0]

        subject = database.select('''SELECT content FROM cantina_administration.config WHERE 
        name='MAIL_VERIFICATION_SUJET' ''', None, number_of_data=1)[0]
        message = database.select('''SELECT content FROM cantina_administration.config WHERE 
        name='MAIL_VERIFICATION_CONTENU' ''', None, number_of_data=1)[0]
        destinataire = database.select('''SELECT email, email_verified FROM cantina_administration.user 
        WHERE token = %s''', (request.cookies.get('token')), number_of_data=1)[0]


    except TypeError:
        return 'error1: Configuration incomplète ou inexistante'

    if conn_url is None or conn_port is None or conn_email is None:
        return 'error1: Configuration incomplète ou inexistante.'

    if subject is None or message is None or subject == "" or message == "" or "{}" not in message:
        return 'error2: Message prédéfinis incomplet ou inexistant'

    mail = MIMEMultipart()
    mail['From'] = conn_email
    mail['To'] = destinataire
    mail['Subject'] = subject
    try:
        content = MIMEText(message.format("000000").encode('utf-8'), 'plain', 'utf-8')
        mail.attach(content)

        smtp_server = SMTP_SSL(conn_url, int(conn_port))
        smtp_server.ehlo()
        smtp_server.login(conn_email, conn_passwd)

        smtp_server.sendmail(conn_email, destinataire, mail.as_string())
        smtp_server.close()

        return 'success'
    except ValueError:
        return 'error1: Configuration incomplète ou inexistante'


def get_rand_num_for_email_verif():
    code = ''
    for i in range(0, 6):
        code = code + str(randint(0, 9))

    return code
