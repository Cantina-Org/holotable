from Utils.verify_login import verify_login
from flask import redirect, url_for, request


def delete_user_cogs(database):
    # Vérification de si l'utilisateur est bien connecté et n'a pas un compte désactivé
    if verify_login(database) and verify_login(database) != 'desactivated':
        # Si l'utilisateur n'a pas les permissions, redirection vers la page d'accueil
        user_permission = database.select("""SELECT delete_account FROM cantina_administration.permission WHERE user_token = %s""", (request.cookies.get('token')), 1)
        if not user_permission[0] and not user_permission[1]:
            return redirect(url_for('show_user'))

        # Suppressions des permissions et des données de l'utilisateur.
        database.exec('''DELETE FROM cantina_administration.user WHERE token = %s''',
                      (request.form['token_to_delete']))
        database.exec('''DELETE FROM cantina_administration.permission WHERE user_token = %s''',
                      (request.form['token_to_delete']))
        return redirect(url_for('show_user'))

    elif verify_login(database) == "desactivated":
        return redirect(url_for('sso_login', error='2'))
    else:
        return redirect(url_for('sso_login'))
