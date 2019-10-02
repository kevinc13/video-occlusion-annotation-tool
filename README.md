# Video Occlusion Annotation Tool

## Screenshots
![Dashboard Screenshot](https://i.imgur.com/EYmsuiT.png)
![Annotation Screenshot](https://i.imgur.com/8G6fnDB.png)

## Requirements
- Python 3.6+ / pip
- Node / NPM

To install the dependencies for Python backend, run the following within the ```backend``` directory (assuming you have already created a virtualenv):
```
pip install -r requirements.txt
```

To install the dependencies for the frontend, run the following within the ```frontend``` directory:
```
npm install
```

## Development
During development, open two terminal sessions and start the Webpack dev server (on port 8080) in one session and run the Django dev server (on port 8000) in the other.

```
$ npm run serve
```
```
$ python manage.py runserver
```

## Build
Run ```make build``` to build the project for deployment.
