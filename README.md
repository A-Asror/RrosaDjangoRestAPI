# Base Django Project ⚙️🛠️

##  Скачать Приложение | Download App 📖
### **HTTPS**
_**git clone:**_ _https://github.com/A-Asror/RrosaDjangoRestAPI.git_

### **SSH**
_**git clone:**_ _git@github.com:A-Asror/RrosaDjangoRestAPI.git_

##  Настройка проекта | Set up the project 🔨
### **Rename core folder and remove .git folder**
```shell
Linux:
  sudo mv ./RrosaDjangoRestAPI <New Folder Name>
  cd <New Folder Name>
  sudo rm -r .git
Windows:
  ren RrosaDjangoRestAPI <New Folder Name>
  cd <New Folder Name>
  rmdir ".git"
```
### **Update .env file**
```shell
Linux
  sudo mv .env.example .env
Windows:
  ren .env.example .env
```

##  Настройка виртуального окружения | Configuring the Virtual Environment ☁️
### **Linux 🐧**
```shell
python3 -m venv venv
OR
python -m venv venv
source venv\bin\activate
```
### **Windows 💻**
```shell
cmd
py -m venv venv
OR
python -m venv venv
venv\scripts\activate
```

##  Установка зависимости | Installing requirements ⚡️
```shell
pip install -r requirements/prod.txt
```

##  Установка pre-commit | Installing Pre-Commit ⚠️️
```shell
pre-commit install
```

##  Запуск проект локально | Run the project locally ✅
``` shell
python manage.py runserver
```

---
![asd](https://d1.awsstatic.com/acs/characters/Logos/Docker-Logo_Horizontel_279x131.b8a5c41e56b77706656d61080f6a0217a3ba356d.png)
##  Запуск проект в docker-compose | Run the project in docker-compose 🐳
```shell
docker-compose -f docker-compose.dev.yaml up -d db backend
```
