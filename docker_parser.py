import argparse
import json
import pathlib
import re

DOCKERFILE_PATTERN = "Dockerfile$"
BUILD_SCRIPT = "build.sh"

DOCKER_BUILD_PATTERN = r"docker build .*-t ([\w\-.\/]+).* (\S+)$"
DOCKER_BUILD_F_PARAMETER = "-f (.*) .*"
DOCKER_FROM_PATTERN = "from ([\w\-.\/]+).*"


def find_files(path, pattern=DOCKERFILE_PATTERN):
    path = pathlib.Path(path)
    if not path.is_dir():
        return []
    files = []
    for file in path.iterdir():
        if file.is_dir():
            files += find_files(file, pattern)
        elif re.match(pattern, file.name, re.IGNORECASE):
            files.append(file)
    return files


def parse_file(file, pattern, *return_groups):
    if return_groups is None:
        return_groups = []
    f = open(file, "r")
    lines = f.readlines()
    for line in lines:
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            res = []
            for group in return_groups:
                res.append(match.group(group))
            f.close()
            return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("projects_root", type=str, nargs="?", default=".")
    args = parser.parse_args()
    projects_root = args.projects_root
    path = pathlib.Path(projects_root)
    if path.exists() and path.is_dir():
        projects = [project for project in path.iterdir() if project.is_dir()]
        dockerfile_paths = []
        build_scripts = []
        dockerfiles = []
        for project in projects:
            dockerfile_paths += find_files(project, DOCKERFILE_PATTERN)
            build_scripts += find_files(project, BUILD_SCRIPT)
        for dockerfile in dockerfile_paths:
            dockerfiles.append({"path": dockerfile, "from": parse_file(
                dockerfile, DOCKER_FROM_PATTERN, 1)[0]})
        nodes = []
        links = []

        link_build_scripts_and_dockerfiles(build_scripts, dockerfiles, projects)
        res = filter(lambda x: "name" not in x, dockerfiles)
        print(len(dockerfiles), len(list(res)))

        for dockerfile in dockerfiles:
            for df in dockerfiles:
                if "name" in dockerfile and df["from"] == dockerfile["name"]:
                    df["from"] = dockerfile["project_name"]

            if "name" in dockerfile:
                node = {"id": dockerfile["project_name"] if "project_name" in dockerfile else dockerfile["name"]}
                if "project_name" in dockerfile:
                    node["type"] = "repo"
                if node not in nodes:
                    nodes.append(node)
                    start = len(nodes) - 1
                else:
                    start = nodes.index(node)
                node = {"id": dockerfile["from"]}
                if node not in nodes:
                    nodes.append(node)
                    end = len(nodes) - 1
                else:
                    end = nodes.index(node)
                links.append({"source": start, "target": end})

        with open("D3_visualisation/graph_rockflows.json", "w") as f:
            json.dump({"nodes": nodes, "links": links}, f)


def link_build_scripts_and_dockerfiles(build_scripts, dockerfiles, projects):
    i = 0
    for script in build_scripts:
        res = parse_file(script, DOCKER_BUILD_PATTERN, 1, 2, 0)
        if res:
            image_name, relative_path = res[0], res[1]
            print(res)
            match = re.search(DOCKER_BUILD_F_PARAMETER, res[2])
            if match:
                relative_path = str(pathlib.Path(match.group(1)).parent)
            joinpath = script.parent.joinpath(relative_path)

            for dockerfile in dockerfiles:

                if dockerfile["path"].match(str(joinpath) + "/*"):
                    dockerfile["name"] = image_name
                    i += 1
                    for project in projects:
                        if project == joinpath or project in joinpath.parents:
                            dockerfile["project_name"] = str(project.name)
                            break


if __name__ == '__main__':
    main()
