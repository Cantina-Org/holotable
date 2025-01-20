from cantinaUtils.verify_login import verify_login
from Utils.email_utils import send_test_email
from flask import redirect, url_for, request


def smtp_test_cogs(database):
    if verify_login(database) and verify_login(database) != 'desactivated':
        user_permission = database.select('''SELECT * from cantina_administration.permission WHERE user_token = %s''',
                                          (request.cookies.get('token')), 1)
        if not user_permission[31] and not user_permission[32]:  # Si l'utilisateur n'as pas la permission, redirection vers la page d'accueil
            return redirect(url_for('home'))

        if request.method == 'POST':
            send_test_email(database)
            return redirect(url_for('smtp_config'))
        else:
            return redirect(url_for('smtp_config'))
    elif verify_login(database) == 'desactivated':
        return redirect(url_for('sso_login', error='2'))
    else:
        return redirect(url_for('sso_login'))
