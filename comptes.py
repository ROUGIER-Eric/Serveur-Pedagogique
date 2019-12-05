# -*- coding: UTF-8 -*-

import os
import csv

# Administrateur Jupyter Hub
ADMIN = "callisto"


print("1 Installation des modules nécessaires pour Jupyter-Hub.")
print("2 Copie des fichiers dans le répertoire de l'admin Jupyter-Lab.")
print("3 Installation des groupes et répertoires partagés.")
print("4 Création des comptes des élèves.")
print("5 Déploiement de la conf nbgrader pour les profs.")
print("6 Supprimer des comptes.")
rep = input("Que faire ? : ")

if rep == "1":
    os.system("apt-get update && apt-get install -yq --no-install-recommends"
              +" python3-pip"+" git"+" g++"+" gcc"+" libc6-dev"
              +" libffi-dev"+" libgmp-dev"+" make"+" xz-utils"
              +" zlib1g-dev"+" gnupg"+" vim"+" texlive-xetex"
              +" pandoc"+" sudo"+" netbase"+" locales")
    os.system("pip install SQLAlchemy==1.2.19 nbgrader nbconvert==5.4.1 && "\
              +"jupyter nbextension install --sys-prefix --py nbgrader --overwrite && "\
              +"jupyter nbextension enable --sys-prefix --py nbgrader && "\
              +"jupyter serverextension enable --sys-prefix --py nbgrader && "\
              +"jupyter nbextension disable --sys-prefix formgrader/main --section=tree && "\
              +"jupyter serverextension disable --sys-prefix nbgrader.server_extensions.formgrader")
    os.system(f"pip install mobilechelonian nbconvert pandas matplotlib folium geopy ipython-sql metakernel"\
              +" pillow nbautoeval jupyterlab-server jupyter_contrib_nbextensions")
    os.system("jupyter contrib nbextension install --sys-prefix")

if rep == "2":
    os.system(f"mkdir -p /home/{ADMIN}/.jupyter && mkdir /home/{ADMIN}/source")
    os.system(f"cp nbgrader_config.py /home/{ADMIN}/.jupyter/nbgrader_config.py")
    os.system(f"cp header.ipynb /home/{ADMIN}/source")
    os.system(f"chown -R {ADMIN} /home/{ADMIN} && chmod 700 /home/{ADMIN}")
    os.system(f"mkdir -p /srv/nbgrader/exchange && chmod ugo+rw /home/{ADMIN}/srv/nbgrader/exchange")
    os.system(f"cp -R exemples /home/{ADMIN}")
    os.system(f"chown -R {ADMIN} /home/{ADMIN}/exemples")

if rep == "3":
   os.system("/usr/sbin/groupadd ELEVE")
   os.system("/bin/mkdir /var/eleves")
   os.system("/bin/chgrp -R ELEVE /var/eleves")
   os.system("/bin/chmod -R 750 /var/eleves")
   os.system("/usr/sbin/groupadd PROF")

   groupes = ['SNT', '1NSI', 'TNSI', '1STI', 'TSTI']
   for groupe in groupes:
      os.system(f"/bin/mkdir /var/eleves/{groupe}")
      os.system(f"/bin/mkdir /var/eleves/{groupe}/partage")
      os.system(f"/usr/sbin/groupadd {groupe}")
      os.system(f"/bin/chown root:PROF /var/eleves/{groupe}")
      os.system(f"/bin/chmod -R 1775 /var/eleves/{groupe}")
      os.system(f"/bin/chown root:{groupe} /var/eleves/{groupe}/partage")
      os.system(f"/bin/chmod -R 775 /var/eleves/{groupe}/partage")


if rep == "4":
    #file = open('login-NSI-test.csv','r')
    file = open('login-eleves-rectif.csv','r')

    reader = csv.DictReader(file, delimiter=',')

    liste = []
    for row in reader:
        liste.append({'LOGIN' : row['NOMLOGMI'],\
         'PRENOM' : row['PRENOM1'],\
         'NOM' : row['NOM'],\
         'PASS' : 'pgdg',\
         'GROUP' : row['SGR']\
         })
    file.close()

    for user in liste:
        user['GROUP'] = user['GROUP'][:1]
        if user['GROUP'] == '1':
            user['GROUP'] = '1NSI'
        elif user['GROUP'] == '2':
            user['GROUP'] = 'SNT'
        elif user['GROUP'] == "T":
            user['GROUP'] = 'ISN'
        LOGIN = user['LOGIN']
        COMMENTAIRE = user['NOM'] + "," + user['PRENOM'] + "," + user['GROUP']
        print(f"Création du compte {LOGIN}")
        os.system(f"/usr/sbin/useradd {LOGIN} --comment {COMMENTAIRE} --home /home/{LOGIN} --create-home --shell /bin/bash")
        os.system(f"echo {LOGIN}:pgdg | /usr/sbin/chpasswd")
        os.system(f"/bin/chmod -R 700 /home/{LOGIN}/")
        os.system(f"/bin/mkdir /home/{LOGIN}/public_html")
        os.system(f"/bin/chmod -R 755 /home/{LOGIN}/public_html")
        os.system(f"/bin/chown -R {LOGIN}:{LOGIN} /home/{LOGIN}")
        os.system(f"usermod -aG ELEVE {LOGIN}")
        GROUP = user['GROUP']
        os.system(f"usermod -aG {GROUP} {LOGIN}")
        os.system(f"mkdir /home/{LOGIN}/partages")
        os.system(f"mount --bind /var/eleves/{GROUP} /home/{LOGIN}/partages")
        fichier = open("/etc/partages/partages-bind", "a")
        fichier.write(f"/var/eleves/{GROUP};{LOGIN}\n")
        fichier.close()

if rep == "5":
   r = "o"
   while r == "O" or r == "o":
       LOGIN = input("Nom d'utilisateur : ")
       rep2 = input("Faut-il créer le compte ? (O/n)) ")
       if rep2 == "O" or rep2 == "o":
           print(f"Création du compte {LOGIN}")
           os.system(f"/usr/sbin/useradd {LOGIN} --home /home/{LOGIN} --create-home --shell /bin/bash")
           os.system(f"echo {LOGIN}:pgdg | /usr/sbin/chpasswd")
           os.system(f"/bin/chmod -R 700 /home/{LOGIN}/")
           os.system(f"/bin/mkdir /home/{LOGIN}/public_html")
           os.system(f"/bin/chmod -R 755 /home/{LOGIN}/public_html")
           os.system(f"mkdir /home/{LOGIN}/partages")
           os.system(f"mount --bind /var/eleves /home/{LOGIN}/partages")
           fichier = open("/etc/partages/partages-bind", "a")
           fichier.write(f"/var/eleves/;{LOGIN}\n")
           fichier.close()
       GROUPS = ["PROF", "SNT", "1NSI", "ISN", "ELEVE"]
       for GROUP in GROUPS:
           os.system(f"usermod -aG {GROUP} {LOGIN}")
   # Deploiement de la conf nbgrader pour les profs
       os.system(f"mkdir -p /home/{LOGIN}/.jupyter")
       os.system(f'cat /home/{ADMIN}/.jupyter/nbgrader_config.py |sed -e "s/{ADMIN}/{LOGIN}/g" > /home/{LOGIN}/.jupyter/nbgrader_config.py')
       os.system(f"mkdir /home/{LOGIN}/source")
       os.system(f"cp /home/{ADMIN}/source/header.ipynb /home/{LOGIN}/source")
       os.system(f"cp -r /home/{ADMIN}/exemples /home/{LOGIN}")
       os.system(f"mv /home/{LOGIN}/exemples/nbgrader/* /home/{LOGIN}/source")
       os.system(f"rm -r /home/{LOGIN}/exemples/nbgrader")
       os.system(f"/bin/chown -R {LOGIN}:{LOGIN} /home/{LOGIN}/source")
       os.system(f'su {LOGIN} -c "/usr/local/bin/jupyter nbextension enable --user formgrader/main --section=tree"')
       os.system(f'su {LOGIN} -c "/usr/local/bin/jupyter serverextension enable --user nbgrader.server_extensions.formgrader"')
       r = input("Un autre ? (O/n) ")


if rep == "6":
   r = "o"
   while r == "O" or r == "o":
       LOGIN = input("Nom d'utilisateur : ")
       os.system(f"umount /home/{LOGIN}/partages")
       os.system(f"sed -i -e '/{LOGIN}/ d' /etc/partages/partages-bind")
       os.system(f"userdel -r {LOGIN}")
       r = input("Un autre ? (O/n) ")

os.system("service jupyterhub restart")
