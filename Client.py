import requests
import subprocess

from Minecraft.Resources import Resources


class Client:

    def __init__(self, resources: Resources, java, client):
        self.subprocess_args = None
        self.java = java
        self.client = client
        self.res = resources.minecraft
        self.cfg = requests.get(self.res["config_file"]).json()
        self.clientConfig = {}
        self.parseStart()

    def parseStart(self):
        self.clientConfig["version"] = self.res["version"]

        jvm_ = self.cfg["arguments"]["jvm"]
        additional = {
            "macos32": [],
            "macos64": [],
            "windows32": [],
            "windows64": [],
            "linux32": [],
            "linux64": []
        }
        for x in jvm_:
            current_os_type = self.res["os"]["type"]
            current_os_bit = self.res["os"]["bit"]
            if type(x) is dict:
                if "name" in x["rules"][0]["os"]:
                    if current_os_type == "macos" and x["rules"][0]["os"]["name"] == "osx":
                        additional["macos32"].append(x["value"][0])
                        additional["macos64"].append(x["value"][0])
                    if current_os_type == "windows" and x["rules"][0]["os"]["name"] == "windows":
                        additional["windows32"].append(x["value"])
                        additional["windows64"].append(x["value"])
                    if current_os_type == "linux" and x["rules"][0]["os"]["name"] == "linux":
                        additional["linux32"].append(x["value"])
                        additional["linux64"].append(x["value"])
                if "arch" in x["rules"][0]["os"]:
                    if current_os_bit == 32 and x["rules"][0]["os"]["arch"] == "x86":
                        additional["macos32"].append(x["value"])
                        additional["windows32"].append(x["value"])
                        additional["linux32"].append(x["value"])
                    if current_os_bit == 64 and x["rules"][0]["os"]["arch"] == "x64":
                        additional["macos64"].append(x["value"])
                        additional["windows64"].append(x["value"])
                        additional["linux64"].append(x["value"])

        arguments = [
            f"java", f"-client",
            f"-Xmx{self.java['xmx']}", f"-Xmn{self.java['xmn']}", f"-Xms{self.java['xms']}",
        ]

        arguments += additional[self.res["os"]["type"]+self.res["os"]["bit"]]

        arguments += [
            f"-Djava.library.path={self.res['natives']}",
            f"-cp", f"{self.res['classPath']}",
            f"{self.cfg['mainClass']}",
            f"--username", f"{self.client['nickname']}",
            f"--version", f"{self.res['version']}",
            f"--gameDir", f"{self.res['folder']}",
            f"--assetsDir", f"{self.res['assets']}",
            f"--assetIndex", f"{self.res['version']}",
            "--uuid", f"{self.client['uuid']}",
            "--accessToken", f"{self.client['token']}",
            "--userType", f"{self.client['userType']}"
        ]

        self.subprocess_args = arguments

    def start(self):
        subprocess.call(self.subprocess_args)