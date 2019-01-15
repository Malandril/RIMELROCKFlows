import argparse
import pathlib
import re

DOCKERFILE_PATTERN = "Dockerfile"
BUILD_SCRIPT = "build.sh"

DOCKER_BUILD_PATTERN = r"docker build .*-t (\S+).* (\S+)$"
DOCKER_FROM_PATTERN = "from (.*)"


def find_dockerfiles(path):
    path = pathlib.Path(path)
    if not path.is_dir():
        return []
    dockerfiles = []
    for file in path.iterdir():
        if file.is_dir():
            dockerfiles += find_dockerfiles(file)
        elif re.match(DOCKERFILE_PATTERN, file.name, re.IGNORECASE):
            dockerfiles.append(file)
    return dockerfiles


def parse_dockerfile(dockerfile: pathlib.Path):
    f = open(dockerfile, "r")
    lines = f.readlines()
    from_name = None
    for line in lines:
        match = re.match(DOCKER_FROM_PATTERN, line, re.IGNORECASE)
        if match:
            from_name = match.group(1)
            break
    f.close()

    glob = list(dockerfile.parent.glob(BUILD_SCRIPT))
    name = None
    dest = None
    if glob and len(glob) > 0:
        build = glob[0]
        f = open(build, "r")
        lines = f.readlines()
        for line in lines:
            match = re.match(DOCKER_BUILD_PATTERN, line)
            if match:
                name = match.group(1)
                dest = match.group(2)
                break
    return from_name, name, dest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("projects_root", type=str, nargs="?", default=".")
    args = parser.parse_args()
    projects_root = args.projects_root
    path = pathlib.Path(projects_root)
    if path.exists() and path.is_dir():
        projects = [project for project in path.iterdir() if project.is_dir()]
        dockerfiles = []
        for project in projects:
            dockerfiles += find_dockerfiles(project)
        for dockerfile in dockerfiles:
            print(parse_dockerfile(dockerfile))


if __name__ == '__main__':
    main()