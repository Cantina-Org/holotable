from cantinaUtils.verify_login import verify_login
from flask import redirect, url_for, request, render_template


def smtp_config_cogs(database):
    if verify_login(database) and verify_login(database) != 'desactivated':
        user_permission = database.select('''SELECT * from cantina_administration.permission WHERE user_token = %s''',
                                          (request.cookies.get('token')), 1)
        if not user_permission[31] and not user_permission[32]:  # Si l'utilisateur n'as pas la permission, redirection vers la page d'accueil
            return redirect(url_for('home'))

        # On récupère les modules afin de pouvoir faire une redirection sur la page via la sidebar
        modules_info = database.select("""SELECT * FROM cantina_administration.modules""", None)

        # On récupère le thème de l'utilisateur afin de pouvoir l'afficher
        local_user_theme = database.select('''SELECT theme FROM cantina_administration.user WHERE token= %s''',
                                           (request.cookies.get('token')), 1)

        if request.method == 'POST':
            for element in request.form:
                database.exec('''UPDATE cantina_administration.config SET content = %s
                WHERE name = %s''', (request.form[element], element))

            return redirect(url_for('smtp_config'))
        else:
            smtp_info = database.select("""SELECT * FROM cantina_administration.config WHERE name='SMTP_URL' 
            OR name='SMTP_PORT' OR name='SMTP_EMAIL' OR name='SMTP_PASSWORD' OR name='MAIL_VERIFICATION_SUJET' 
            OR name='MAIL_VERIFICATION_CONTENU'""", None)
            return render_template('Administration/smtp_config.html', smtp_info=smtp_info,
                                   user_permission=user_permission, modules_info=modules_info, local_user_theme=local_user_theme)
    elif verify_login(database) == 'desactivated':
        return redirect(url_for('sso_login', error='2'))
    else:
        return redirect(url_for('sso_login'))
