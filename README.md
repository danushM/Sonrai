# Sonrai

<div align="center" >
  <strong> The environmental sentiment tool </strong>
</div>

# Software versions used:
```
Cloud: AWS Free Tier
Operating System: RHEL 8
Python: 3.7.3
Django: 2.2.1
MongoDB: 4.0 
vaderSentiment: 3.2.1
Bokeh: 1.3.0
```
# How to use this repo
- Clone the repo: git clone https://github.com/danushM/Sonrai
- Switch to the Repo: **cd Sonrai**
## Environment Configuration
Finish the environment configuration by following the instructions **env_setup/env_setup.txt**. This includes 
```
Installation of Python
Creating Virtual environemnt
Installation of various Python modules
MongoDB installation and Confiugration
Django configuration
```
## Data Collection
- Copy the data collection scripts to the server
```
mkdir /opt/scripts
cp DataCollection and Preprocessing/URLHarvesterGoogleSearch.py /opt/scripts
cp DataCollection and Preprocessing/URLHarvesterGoogleNews.py /opt/scripts
```
- Now configure the below cron jobs which are used to gather the data
```
0 0 * * * /opt/scripts/URLHarvesterGoogleSearch.py
0 5 * * * /opt/scripts/URLHarvesterGoogleNews.py
```
## Configure the web application
- Copy the urls.py: **cp front-end-ui/campaign/campaign/urls.py /opt/project/campaign/campaign/**
- Copy the views.py: **cp front-end-ui/campaign/campaign/views.py /opt/project/campaign/campaign/**
- Copy the html templates: **cp front-end-ui/campaign/templates/\* /opt/project/campaign/templates/**
- Copy the static files (CSS&Java script): **cp front-end-ui/campaign/static/\* /opt/project/campaign/static/**
- Start the Sonrai webapp by running 
```
cd /opt/project/campaign/
python manage.py runserver 0.0.0.0:80
```
- Now access the **Sonraí** using your IP address or hostname of the server.

**For more information on Sonraí, please refer our full report.**
