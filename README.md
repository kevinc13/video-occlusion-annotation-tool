# django-vue-scaffold
An easy-to-use, flexible scaffold for integrating a Vue.js SPA into a Django application

* Works with Vue CLI 3 and Django 2.1+
* Relies on the `django-webpack-loader` and `webpack-bundle-tracker` plugins
* Based on this article: https://ariera.github.io/2017/09/26/django-webpack-vue-js-setting-up-a-new-project-that-s-easy-to-develop-and-deploy-part-1.html

## Overview
The Django project is located within the `backend` directory, and the Vue project is located within the `frontend` directory. 
The `backend/templates/spa.html` is the Django template that loads the Vue SPA, and its URL endpoint can be configured in `backend/project/urls.py`. 

Includes:
* Django Rest Framework
* Custom environment-based configuration of Django settings using an `env.json` file
* Vue Router
* Vue E2E (Cypress) and Unit Testing (Jest)

## Shared Static Files
Static files that are shared across the two projects (such as favicon.ico, logos, etc.) can be stored in the `shared_static` directory. 

The Django settings file has already been configured to resolve references to these shared static files when using `{% static [some_shared_static_file] %}.` An alias has also been included in `frontend/vue.config.js` to allow these files to be referenced in Vue templates using `~__SHARED_STATIC__/some_shared_static_file`.

## Requirements
* Python 3.6+
  * pip
  * virtualenv
* Node + NPM

## Setup
```bash
# In frontend directory
$ npm install

# In backend directory
$ python3 -m virtualenv venv # Or whatever you want your virtualenv to be called
$ source venv/bin/activate
$ pip install -r requirements.txt
```

**IMPORTANT: Create an `env.json` file in `backend/project` with at least the following:**
```json
{
    "ENV_NAME": "development",
    "SECRET_KEY": "lmm%+bo1flphkd9*btm8e-^6*%+b!+ad+2(x*4=dda)(tsw6#*",
    "DEBUG": true
}
```

See the `settings.py` file for more configuration options (you can easily add/customize options to your desire)

## Development
During development, open two terminal sessions and start the Webpack dev server (on port 8080) in one session and run the Django dev server (on port 8000) in the other.

`$ npm run serve`

`$ python manage.py runserver`

Go to http://localhost:8000/app to see the Vue SPA, and http://localhost:8000/api/hello to see the included hello world API endpoint.

## Production
To deploy the application for production, run the following commands:

```bash
# In frontend directory
$ npm run build

# In backend directory
$ python manage.py collectstatic
```

The Vue files along with any other Django static assets will be copied into a `public` directory at the root of the project, which can be accessed via the `/static` URL endpoint (configured in the Django `settings.py` file).

**Additionally, you will want to modify the `backend/project/env.json` file by setting `DEBUG` to `false`, setting the `ALLOWED_HOSTS`, and changing the `ENV_NAME` to `production`.**
