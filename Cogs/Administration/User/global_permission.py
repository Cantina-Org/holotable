from flask import request, redirect, url_for, render_template
from cantinaUtils.verify_login import verify_login
from Utils.Administration.User.check_global_permission_edit import check_perm


def global_permission_cogs(database):
    if verify_login(database) and verify_login(database) != 'desactivated':
        # On récupère les modules afin de pouvoir faire une redirection sur la page via la sidebar
        modules_info = database.select("""SELECT * FROM cantina_administration.modules""", None)

        # On récupère le thème de l'utilisateur afin de pouvoir l'afficher
        local_user_theme = database.select('''SELECT theme FROM cantina_administration.user WHERE token= %s''',
                                           (request.cookies.get('token')), 1)

        permission = []
        for i in ['edit_username', 'edit_password', 'edit_email', 'edit_profile_picture', 'edit_a2f']:
            permission.append(database.select('''SELECT content FROM cantina_administration.config WHERE name = %s''',
                                              (i,), number_of_data=1)[0])

        user_permission = database.select('''SELECT * FROM cantina_administration.permission WHERE user_token = %s''',
                                          (request.cookies.get('token')), number_of_data=1)
        if not user_permission[14] and not user_permission[15] and not user_permission[16] and not user_permission[17] and not user_permission[18] and not user_permission[32]:
            return redirect(url_for('home'))

        if request.method == 'POST': # Si la request est de type "POST" on mets à jour les permission et on affiche les dernières valeurs
            for i in ['edit_username', 'edit_password', 'edit_email', 'edit_profile_picture', 'edit_a2f']:
                database.exec(f'''UPDATE cantina_administration.permission SET {i} = %s''', (check_perm(i)))
                database.exec('''UPDATE cantina_administration.config SET content = %s WHERE name = %s''',
                              (check_perm(i), i))

            permission = []
            for i in ['edit_username', 'edit_password', 'edit_email', 'edit_profile_picture', 'edit_a2f']:
                permission.append(
                    database.select('''SELECT content FROM cantina_administration.config WHERE name = %s''',
                                    (i,), number_of_data=1)[0])


        return render_template('Administration/global_permission.html', permission=permission,
                               user_permission=user_permission, modules_info=modules_info, local_user_theme=local_user_theme)

    elif verify_login(database) == "desactivated":
        return redirect(url_for('sso_login', error='2'))
    else:
        return redirect(url_for('sso_login'))
