
# This is part 2 of a deployment script that launches an AWS instance,
# copy files to the server, and launches the frontend after it is started.

# This part copies application files over to the new instance, install packages,
# and launch the search engine on the server.

import os

if __name__ == "__main__":

    # install git
    os.system("sudo apt-get -y install git")

    # copy application files over from GitHub
    os.system("git clone https://github.com/woodcaroline/search-engine")

    os.system("cd search-engine")

    # install pip
    os.system("sudo apt-get update")
    os.system("sudo apt-get -y install python-pip")

    # install bottle, oauth2client, beaker, BeautifulSoup4, paste
    os.system("sudo pip install bottle")
    os.system("sudo pip install oauth2client")
    os.system("sudo pip install beaker")
    os.system("sudo pip install BeautifulSoup4")
    os.system("sudo pip install Paste")

    # launch the search engine!
    os.system("nohup python main.py")
