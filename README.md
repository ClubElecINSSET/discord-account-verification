[![](https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Gitea_Logo.svg/48px-Gitea_Logo.svg.png)](https://forge.collabore.fr)

![English:](https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_the_United_States_and_United_Kingdom.png/20px-Flag_of_the_United_States_and_United_Kingdom.png) **club elec** uses **Gitea** for the development of its free softwares. Our GitHub repositories are only mirrors.
If you want to work with us, **fork us on [collabore forge](https://forge.collabore.fr/)** (no registration needed, you can sign in with your GitHub account).

![Français :](https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_France_(1794%E2%80%931815%2C_1830%E2%80%931974%2C_2020%E2%80%93present).svg/20px-Flag_of_France_(1794%E2%80%931815%2C_1830%E2%80%931974%2C_2020%E2%80%93present).svg.png) **club elec** utilise **Gitea** pour le développement de ses logiciels libres. Nos dépôts GitHub ne sont que des miroirs.
Si vous souhaitez travailler avec nous, **forkez-nous sur [collabore forge](https://forge.collabore.fr/)** (l’inscription n’est pas nécessaire, vous pouvez vous connecter avec votre compte GitHub).
* * *

<h2 align="center">discord account verification</h2>
<p align="center">Account verification bot for club elec's Discord server</p>
<p align="center">
    <a href="#about">About</a> •
    <a href="#features">Features</a> •
    <a href="#deploy">Deploy</a> •
    <a href="#configuration">Configuration</a> •
    <a href="#license">License</a>
</p>

## About

[club elec](https://clubelec.insset.fr) needed a tool to validate the Discord accounts of people joining its Discord server.  
Validating student accounts manually is a time-consuming operation requiring the presence of an administrator.  
This Discord bot was therefore created to allow newcomers to easily validate their Discord account by receiving a verification code on their university email address, saving everyone time.

## Features

- ✅ **Easy** to use
- ✅ **Receive** a validation code by **email**
- ✅ **Easy** to deploy
- ✨ Using **Discord interactions**

## Deploy

We have deployed discord account verification on a server running Debian 11.

**Please adapt these steps to your configuration, ...**  
*We do not describe the usual server configuration steps.*

### Install required packages

```
apt install python3-pip python3-venv
```

### Create `discord-account-verification` user

```
groupadd discord-account-verification
```

```
useradd -r -s /sbin/nologin -g discord-account-verification discord-account-verification
```

### Retrieve sources

```
mkdir /opt/discord-account-verification
```

```
chown discord-account-verification:discord-account-verification /opt/discord-account-verification
```

```
cd /opt/discord-account-verification
```

```
runuser -u discord-account-verification -- git clone https://forge.collabore.fr/ClubElecINSSET/discord-account-verification .
```

### Create Python virtual environment

```
runuser -u discord-account-verification -- virtualenv .env
```

### Install Python dependencies

```
runuser -u discord-account-verification -- .env/bin/pip install -r requirements.txt
```

### Install systemd service

```
cp discord-account-verification.service /etc/systemd/system/
```

### Enable and start systemd service

```
systemctl enable discord-account-verification
```

```
systemctl start discord-account-verification
```

## Configuration

To configure discord account verification, please modify the configurations of the systemd service according to your needs.

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see http://www.gnu.org/licenses/.

