
import os
import shutil
from pathlib import Path
import subprocess  
import tomlkit
import toml
from collections import defaultdict
from packaging.requirements import Requirement
import logging


class AlignDependencies:
    """
        Align dependancies by checking pyproject.toml dependancies
        Attempts to align, if possible update all
    """
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PYPROJECT_TOML = "pyproject.toml"
    PYPROJECT_TOML_BCK = "pyproject.toml.bck"
    DOCKERFILE = "Dockerfile"
    DOCKERFILE_TEMP = "Dockerfile.temp"
    APPS = "apps"

    upgrades = {
        "numpy": ["2.2.1", "2.3.0", "2.3.1"],
        "pandas": ["2.2.3", "2.3.0", "2.3.1"],
        "psutil": ["6.1.1", "7.0.0"],
        "structlog": ["24.4.0", "25.1.0", "25.2.0"]
    }
    
    
    def __init__(self):
        # Get the current dep
        self.project_dependencies = self.load_pyproject_deps()
        self.package_updates = None
        # If there are dep
        if self.project_dependencies:
            self.inject_base_dependencies()
            self.package_updates = self.find_alignment()
        else:
            logging.info("No Dependencies")
        
    def alignment_available(self) ->bool:
        """
            Check if upgrades are available
            Returns boolean
        """
        return bool(self.package_updates)

    
    def find_alignment(self)->defaultdict:
        """
            If alignment is possible update the Dockerfile and pyproject.toml 
            Returns defaultdict of [{numpy: 'new_version'},..]
        """
        dependencies = defaultdict(list)
        total_apps = self.get_apps_count()
        for package, version in self.load_pyproject_deps().items():
            upgrades = self.search_dependencies_alignment(package)
            if len(upgrades.keys()) == total_apps:
                # Check if the current version is in list
                if version[2:] in upgrades.values():
                    continue
                else:
                    new_version = list(upgrades.values())[0]
                    dependencies[package] = new_version
        return dependencies
    
    def remove_file(self, file_path: Path)->bool:
        """
            Remove file given a path object.
            Returns: boolean
        """
        try:
            file_path.unlink()
            return True
        except Exception as e:
            logging.info(f"Unable to remove file {file_path.name}, error {e}")
            return False


    def test_pyproject(self) ->bool:
        """
            Runs "make build-base" on newly created toml file.
        """
        if not self.alignment_available():
            return False
        pyproject_path = Path(self.CURRENT_DIR).resolve().parent / self.PYPROJECT_TOML
        pyproject_path_backup = Path(self.CURRENT_DIR).resolve().parent / self.PYPROJECT_TOML_BCK
        if not pyproject_path_backup.exists():
            return False
        if not pyproject_path.exists():
            return False
        try:
            completed = subprocess.run(
                ["make", "build-base"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,       
                check=True       
            )
        except subprocess.CalledProcessError as e:
            logging.info("Build base failed with exit code", e)
            logging.info("Output: ", e.output)
            self.remove_file(pyproject_path)
            return False
        else:
            logging.info("Build-base success")
            logging.info("Output \n", completed.stdout)
            self.remove_file(pyproject_path_backup)
            return True


    def update_pyproject(self) -> list:
        """
        Safely update main dependencies in pyproject.toml by first
        backing the file up to pyproject.toml.bck alongside it, then
        overwriting pyproject.toml with the updated versions.

        Returns:
            List[str]: the list of updated "name==version" entries
                    (empty if none applied or on error).
        """
        proj_file = Path(self.CURRENT_DIR).resolve().parent / self.PYPROJECT_TOML
        if not self.package_updates:
            return []
        backup_file = proj_file.with_name(self.PYPROJECT_TOML_BCK)
        updates = []
        try:
            original_text = proj_file.read_text(encoding="utf-8")
            toml_data = tomlkit.parse(original_text)
            shutil.copy2(proj_file, backup_file)
            deps = toml_data["project"]["dependencies"]
            for idx, dep in enumerate(deps):
                name, _ = dep.split("==", 1)
                if name in self.package_updates:
                    new_ver = self.package_updates[name]
                    deps[idx] = f"{name}=={new_ver}"
                    updates.append(f"{name}=={new_ver}")

            proj_file.write_text(tomlkit.dumps(toml_data), encoding="utf-8")
        except (FileNotFoundError, tomlkit.TOMLKitError, OSError, shutil.Error) as e:
            logging.info(f"Failed to update pyproject.toml: {e}")
            if backup_file.exists():
                shutil.copy2(backup_file, proj_file)
                logging.info(f"Restored original from {backup_file}")
            return []

        return updates  
        

    def get_apps_count(self)->int:
        """
            Get the number of apps in /apps directory by delimter "-"
            Returns: int
        """
        parent_dir = Path(self.CURRENT_DIR).resolve().parent
        apps_dir = parent_dir / self.APPS
        count = 0
        for dir in apps_dir.iterdir():
            if not dir.is_dir():
                continue
            if len(dir.name.split("-")) > 1:
                count += 1
        return count
    

    def search_dependencies_alignment(self, package: str)->defaultdict:
        """
            Given a package check if docker build and docker run succeeds. 
            Args: 
            package : Check possible alignments for package prefix
        """
        parent_dir = Path(self.CURRENT_DIR).resolve().parent
        apps_dir = parent_dir / self.APPS
        successful = defaultdict(str)
        for ch in apps_dir.iterdir():
            if not ch.is_dir():
                continue
            directory_content = ch.name.split("-")
            if len(directory_content) < 1:
                continue
            prefix, suffix = directory_content[0], directory_content[1]
            job_dir = apps_dir / f"{prefix}-{suffix}"
            dockerfile, dockerfile_temp = job_dir / self.DOCKERFILE, job_dir / self.DOCKERFILE_TEMP
            orig_text  = dockerfile.read_text().splitlines()
            # extract current version 
            cur_ver = self.project_dependencies[package][2:]
            # start from the current version index
            start_idx = self.upgrades[package].index(cur_ver)
            for candidate in self.upgrades[package][start_idx+1:]:
                # build a temp Dockerfile
                new_lines = []
                for ln in orig_text:
                    if ln.strip().startswith("FROM python-base"):
                        new_lines.append(ln)
                        new_lines.extend([
                            f"RUN pip install {package}=={candidate} pytest",
                        ])
                    else:
                        new_lines.append(ln)
                dockerfile_temp.write_text("\n".join(new_lines)+"\n")

                # try build+test
                tag = f"verify-{prefix}-{suffix}-{candidate}"
                try:
                    subprocess.run(
                        ["docker", "build", "-f", str(dockerfile_temp), "-t", tag, '.'],
                        cwd=parent_dir, check=True, stdout=subprocess.DEVNULL
                    )
                    container_id = subprocess.check_output(
                        ["docker", "run", "-d", tag],
                        cwd=parent_dir
                    ).decode().strip()
                    logging.info("Container ID", container_id)
                    logs = subprocess.check_output(["docker", "logs", container_id]).decode()
                    if "Traceback" in logs or "ERROR" in logs:
                        break
                    key = f"{prefix}-{suffix}"
                    successful[key] = candidate
                    break
                except subprocess.CalledProcessError:
                    logging.info(f"{prefix}-{suffix} failed with {package}=={candidate}")
                finally:
                    dockerfile_temp.unlink(missing_ok=True)
                    subprocess.run(["docker", "stop", container_id], check=False)
                    subprocess.run(["docker", "rmi", "-f", tag], check=False)
            else:
                logging.info("No changes need to be made")
                dockerfile_temp.unlink(missing_ok=True)

        return successful


    def load_pyproject_deps(self)->dict[str, str]:
        """
            Return a base dependencies dictionary from pyproject.toml file.
            Returns: 
                dict {"pandas==1.2.3", "numpy==1.2.3"}
        """
        PROJECT_ROOT = Path(__file__).resolve().parent.parent             
        pyproject_file = PROJECT_ROOT / self.PYPROJECT_TOML
        data = toml.loads(pyproject_file.read_text())
        result: dict[str, str] = {}
        proj = data.get("project", {})
        if isinstance(proj.get("dependencies"), list):
            for item in proj["dependencies"]:
                # item is a string like "pkg==1.2.3" or "pkg>=1.0,<2.0"
                req = Requirement(item)
                result[req.name] = str(req.specifier)
            return result
        return None


    def inject_deps_once(self, dockerfile: Path, deps: dict[str, str])->bool:
        """
        Checks if dependencies have already been injected into the Dockerfile.
        Args:
            Dockerfile: Path to the Dockerfile
            Deps: Dictionary of package dependencies (e.g., {"numpy": "==1.21.0"})
        
        Returns:
            bool: True if all dependencies are found, False otherwise
        """
        try:
            text = dockerfile.read_text()
        except IOError:
            return False
        dep_patterns = [f"{pkg}{ver}" for pkg, ver in deps.items()]
        return all(pattern in text for pattern in dep_patterns)
            

    def inject_base_dependencies(self) -> bool:
        """
        Try pkg==version into each app’s Dockerfile by generating a Dockerfile.temp.
        Return True if at least one temp-Dockerfile was written.
        """
        parent_dir = Path(self.CURRENT_DIR).resolve().parent
        apps_dir = parent_dir / self.APPS
        any_injected = False
        for app_dir in apps_dir.iterdir():
            if not app_dir.is_dir():
                continue
            dockerfile = app_dir / self.DOCKERFILE
            if not dockerfile.exists():
                continue
            if self.inject_deps_once(dockerfile, self.project_dependencies):
                continue

            lines = dockerfile.read_text().splitlines()
            new_lines = []
            injected = False

            for line in lines:
                new_lines.append(line)
                if not injected and line.strip().startswith("FROM python-base"):
                    for pkg, ver in self.project_dependencies.items():
                        new_lines.append(f"RUN pip install {pkg}=={ver}")
                    injected = True

            if injected:
                temp_dockerfile = app_dir / self.DOCKERFILE_TEMP
                temp_dockerfile.write_text("\n".join(new_lines) + "\n")
                any_injected = True

        return any_injected
    

            
            
        



