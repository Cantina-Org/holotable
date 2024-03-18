from pyotp import random_base32, totp
from flask import request, render_template, redirect, url_for
from Utils.verify_login import verify_A2F


def doubleFA_add_cogs(database):
    if request.method == 'POST':
        if verify_A2F(database):
            database.exec('''UPDATE cantina_administration.user SET A2F = 1 WHERE token=%s''',
                          (request.cookies.get('token')))
            return redirect(url_for('home'))
        else:
            key = database.select('''SELECT A2F_secret FROM cantina_administration.user WHERE token = %s''',
                                  (request.cookies.get('token')), number_of_data=1)[0]
            totp_auth = totp.TOTP(key).provisioning_uri(
                name='Cantina Olympe',
                issuer_name=database.select("""SELECT username FROM cantina_administration.user WHERE token = %s""",
                                            (request.cookies.get('token'),), number_of_data=1)[0]
            )
            return render_template('Administration/2FA-add.html', totp_auth=totp_auth,
                                   error=1)
    elif request.method == 'GET':
        if database.select('''SELECT A2F FROM cantina_administration.user WHERE token=%s''',
                           (request.cookies.get('token')), number_of_data=1)[0]:
            return redirect(url_for('home'))

        if database.select('''SELECT A2F_secret FROM cantina_administration.user WHERE token = %s''',
                           (request.cookies.get('token')), number_of_data=1)[0] is None:
            key = random_base32()
            database.exec("""UPDATE cantina_administration.user SET A2F_secret = %s WHERE token = %s""",
                          (key, request.cookies.get('token')))
        else:
            key = database.select('''SELECT A2F_secret FROM cantina_administration.user WHERE token = %s''',
                                  (request.cookies.get('token')), number_of_data=1)[0]
        totp_auth = totp.TOTP(key).provisioning_uri(
            name='Cantina Olympe',
            issuer_name=database.select("""SELECT username FROM cantina_administration.user WHERE token = %s""",
                                        (request.cookies.get('token'),), number_of_data=1)[0]
        )
        return render_template('Administration/2FA-add.html', totp_auth=totp_auth,
                               error=0)