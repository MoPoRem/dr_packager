

# Django-React Packager ![version](https://img.shields.io/pypi/v/dr-packager)
React-Django packager helps you ship a react front end with django as backend.
This package automatically builds your react project and places the static and index file in their appropriate place in your django project.

## Installation
Install the package using pip:
```bash
pip install dr_packager
```
and thats it!
## Motivation
React is one of the most popular front-end frameworks, and with django being one of the most popular backend choices, there are a lot of websites built with this stack.
You can serve django on a different server than the react project and communicate between them using an API, but for smaller projects (or even bigger ones), Having 2 separate server is not justified. Copying react build files to your server is not fun either (which can be simplified with a CI\CD).

This project helps you serve react project with django (that can be deployed on a single server). This package was made out of frustration of building react project and manually copying everything to django project.
## Usage
To use the packager, you should have both the react folder & django folder in the same parent folder as follows (Absolute path is still not supported in this version):
```bash
├───root_folder
│   ├───django_project
│   ├───react_project
```
Your django project should contain:
- An app that serves the `index.html`
- A static folder (set by STATIC_ROOT variable in your settings)
> IMPORTANT: Your django project root folder and base app should have the same name
> for example, settings.py should be located at `example.example.settings.py`

Open terminal in `root_folder`, and run the following command:
```bash
dr_package <react_path> <django_path> <django_front_app_name>
```
Following the above folder example, consider that we have an app named `front` in our django project:
```bash
dr_package react_project django_project front
```
> IMPORTANT: Your django settings files should contain STATIC_ROOT variable

### Commands
```bash
usage: dr_package [-h] [-S] [--npm] [--yarn] [-D] [-I] [--folders-old [FOLDERS_OLD ...]]
                  react_path django_path app_name

Build React Project and Deploy with Django!

positional arguments:
  react_path            React folder name (RELATIVE PATH)
  django_path           Django folder name (RELATIVE PATH)
  app_name              Name of the app that holds index.html

optional arguments:
  -h, --help            show this help message and exit
  -S, --skip-build      Skip react build (Use what is alredy in \build\)
  --npm                 use npm as the package manager of the react project
  --yarn                use yarn as the package manager of the react project
  -D, --delete-old      Delete old static files
  -I, --install         Run install command before building (use if you haven't installed the required packages)
  --folders-old [FOLDERS_OLD ...]
                        Name of the folders to delete (Doesn't work if --delelete-old is not provided), separated by
                        space
````

## Roadmap
- Support for absolute path
- Default setting file
- More customization
- Creating a separate django package (to run as management commands) to use with git hooks

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
