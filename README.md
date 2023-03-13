# Base Django Project ⚙️🛠️

##  Скачать Приложение📖
### **HTTPS**
_**git clone:**_ _https://github.com/A-Asror/BaseDjango.git_

### **SSH**
_**git clone:**_ _git@github.com:A-Asror/BaseDjango.git_

##  Настройка проекта 🔨
### **Rename core folder and remove .git folder**
```shell
Linux
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

##  Настройка виртуального окружения ☁️
### **Linux**
```shell
python3 -m venv venv
OR
python -m venv venv
source venv\bin\activate
```
### **Windows**
```shell
cmd
py -m venv venv
OR
python -m venv venv
venv\scripts\activate
```

##  Установка зависимости ⚡️
### **Project Run Local**
```shell
pip install -r requirements/prod.txt
```

##  Установка pre-commit ⚠️️
```shell
pre-commit install
```

##  Запуск проект локально ✅
``` shell
python manage.py runserver
```

---
![asd](https://d1.awsstatic.com/acs/characters/Logos/Docker-Logo_Horizontel_279x131.b8a5c41e56b77706656d61080f6a0217a3ba356d.png)
##  Запуск проект в docker-compose 🐳
```shell
docker-compose -f docker-compose.dev.yaml up -d db backend
```
