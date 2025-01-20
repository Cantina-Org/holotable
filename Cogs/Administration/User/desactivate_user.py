from Utils.verify_login import verify_login
from flask import redirect, url_for, request


def desactivate_user_cogs(database):
    # Vérification de si l'utilisateur est bien connecté et n'a pas un compte désactivé
    if verify_login(database) and verify_login(database) != 'desactivated':
        # Si l'utilisateur n'a pas les permissions, redirection vers la page d'accueil
        user_permission = database.select("""SELECT desactivate_account, admin FROM cantina_administration.permission WHERE user_token = %s""", (request.cookies.get('token')), 1)
        print(user_permission)
        if not user_permission[0] and not user_permission[1]:
            return redirect(url_for('show_user'))

        # Désactivation dans la base de donneés de l'utilisateur
        database.exec('''UPDATE cantina_administration.user SET desactivated = NOT desactivated WHERE token = %s''',
                      (request.form['token_to_desactivate']))
        return redirect(url_for('show_user', user_token=request.form['token_to_desactivate']))

    elif verify_login(database) == "desactivated":
        return redirect(url_for('sso_login', error='2'))
    else:
        return redirect(url_for('sso_login'))
