import sys
import os
import argparse
import subprocess
import importlib
import importlib.util
import shutil
import glob

react_file_names = ["package.json"]


def import_settings(name, path):
    spec = importlib.util.spec_from_file_location(f"{name}.{name}.settings", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["settings"] = module
    spec.loader.exec_module(module)
    return module


def isdir(path):
    """Returns path if its a directory, otherwise None"""
    return path if os.path.isdir(path) else None


def move_static_files(src, dst, delete_old=False, old_folders=["js", "media", "css"]):
    print(f"Moving static files to {dst}")
    if not os.path.isdir(src):
        print(f"Source folder is not a directory!\nSource:{src}")
        return
    if not os.path.isdir(dst):
        print(f"Destination folder is not a directory!\Destination:{src}")
        return
    if delete_old:
        print("Removing old files...")
        if not old_folders:
            old_folders = ["js", "media", "css"]
        for folder in old_folders:
            print(f"Removing {folder}...")
            if full_path := isdir(f"{dst}\\{folder}"):
                shutil.rmtree(full_path)
    shutil.copytree(src, dst, dirs_exist_ok=True)


def move_misc_files(src, dst, ignore_html=True):
    files = glob.glob(src + "/*.*")
    print(f"Moving misc files to {dst}")
    for file in files:
        if ignore_html and file[-4] == ".html":
            continue
        shutil.copy(file, dst)


def move_index_file(src, dst):
    files = glob.glob(src + "/*.html")
    print(f"Moving index file to {dst}")
    for file in files:
        shutil.copy(file, dst)


def determine_package_manager(root):
    if os.path.isfile(root + "\\yarn.lock"):
        return "yarn"
    elif os.path.isfile(root + "\\package-lock.json"):
        return "npm"
    return "unk"


def determine_project_paths(base):
    dirs = os.listdir(base)
    django_path = None
    django_found = False

    react_path = None
    react_found = False
    for dir in dirs:
        if os.path.isdir(dir):
            files = [ab for ab in os.listdir(dir)]
            for file in files:
                if file == "manage.py":
                    if django_found:
                        raise RuntimeError("Multiple Django projects found!")
                    else:
                        django_path = os.path.abspath(dir)
                        django_found = True
                elif file in react_file_names:
                    if react_found:
                        print("Multiple react folders found!", end="\n\n")
                        react_path = None
                    else:
                        react_path = os.path.abspath(dir)
                        react_found = True
    return (django_path, react_path)


def find_settings_path(django_path):
    """Searches for settings.py in maximum of 2 depth,
    cause thats how a normal django project should be (TODO: make it recursive)"""
    dirs = os.listdir(django_path)
    for dir in dirs:
        if dir == "settings.py":
            print("WARNING: found settings.py in django base path!")
        if os.path.isdir(dir):
            files = [f for f in os.listdir(dir)]
            if "settings.py" in files:
                return dir
    return None


def run_build(pm):
    pm = pm.lower()
    if pm == "yarn":
        process = subprocess.run(["yarn", "build"], cwd=os.getcwd(), shell=True)
    elif pm == "npm":
        process = subprocess.run(["npm", "run", "build"], cwd=os.getcwd(), shell=True)
    return process.returncode


def run_install(pm):
    pm = pm.lower()
    if pm == "yarn":
        process = subprocess.run(["yarn", "install"], cwd=os.getcwd(), shell=True)
    elif pm == "npm":
        process = subprocess.run(["npm", "install"], cwd=os.getcwd(), shell=True)
    return process.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Build React Project and Deploy with Django!"
    )
    parser.add_argument(
        "-S",
        "--skip-build",
        action="store_true",
        help="Skip react build (Use what is already in \\build\)",
    )
    parser.add_argument(
        "--npm",
        action="store_true",
        help="use npm as the package manager of the react project",
    )
    parser.add_argument(
        "--yarn",
        action="store_true",
        help="use yarn as the package manager of the react project",
    )
    parser.add_argument(
        "-D",
        "--delete-old",
        action="store_true",
        help="Delete old static files",
    )
    parser.add_argument(
        "-I",
        "--install",
        action="store_true",
        help="Run install command before building (use if you haven't installed the required packages)",
    )
    parser.add_argument(
        "--folders-old",
        nargs="*",
        action="store",
        help="Name of the folders to delete (Doesn't work if --delelete-old is not provided), separated by space",
    )
    parser.add_argument("react_path", help="React folder name (RELATIVE PATH)")
    parser.add_argument("django_path", help="Django folder name (RELATIVE PATH)")
    parser.add_argument("app_name", help="Name of the app that holds index.html")
    args = parser.parse_args()

    base_path = os.getcwd()
    print("=====Django & React Packager=====")
    print(f"Base Directory: {base_path}")

    settings_path = base_path + f"\\{args.django_path}\\{args.django_path}\\settings.py"
    settings = import_settings(args.django_path, settings_path)
    # settings = importlib.import_module(
    #     f"{args.django_path}.{args.django_path}.settings"
    # )
    os.chdir(f"./{args.react_path}")
    src = os.getcwd() + f"\\build"

    if args.install:
        print("=====Installing Dependencies=====")
        if args.yarn:
            run_install("yarn")
        elif args.npm:
            run_install("npm")
        else:
            pm = determine_package_manager(os.getcwd())
            run_install(pm)

    if not args.skip_build:
        print("=====Building the React Project=====")
        if args.yarn:
            flag = run_build("yarn")
        elif args.npm:
            flag = run_build("npm")
        else:
            print("Package manager not provided...")
            print(f"Detected {pm} as the package manager.")
            flag = run_build(pm)
        print("React project successfuly built...")
    else:
        print("=====Skipping build=====")
        flag = 0
    # If build is successful, returncode is 0
    if flag == 0:
        print("=====Moving React files=====")
        build = src + f"\\static\\"
        dst = settings.STATIC_ROOT
        move_static_files(
            build, dst, delete_old=args.delete_old, old_folders=args.folders_old
        )
        move_misc_files(src, dst)
        app_path = (
            base_path
            + f"\\{args.django_path}\\{args.app_name}\\templates\\{args.app_name}\\"
        )
        move_index_file(src, app_path)
    print("=====All Done!=====")


if __name__ == "__main__":
    main()
