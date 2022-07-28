import requests
import json
import os

BIT0 = 0
BIT32 = 32
BIT64 = 64


class Resources(object):

    def __init__(self, settings, callbacks=None, log=True):
        if callbacks is None:
            callbacks = {}
        self.callbacks = callbacks
        self.debug_info = log
        self.debug("Downloading client.json")
        self.client_json = requests.get(settings["client_url"]).json()

        if not os.path.exists(settings["minecraft_folder"]):
            os.mkdir(settings["minecraft_folder"])

        custom_files = [
            "servers", "options"
        ]
        for x in custom_files:
            if x in settings:
                servers_url = settings[x]["url"]
                with open(settings["minecraft_folder"] + "/" + settings[x]["path"], "wb") as srv_file:
                    srv_file.write(requests.get(servers_url).content)

        self.libraries = []
        self.version = {
            "name": self.client_json["id"],
            "url": self.client_json["downloads"]["client"]["url"]
        }

        os_type, os_bit = self.detectPlatform()

        self.minecraft = {
            "folder": settings["minecraft_folder"],
            "natives": settings["minecraft_folder"] + "/versions/natives",
            "assets": settings["minecraft_folder"] + "/assets",
            "config_file": settings["client_url"],
            "version": self.client_json["id"],
            "classPath": "",
            "os": {
                "type": os_type,
                "bit": os_bit
            }
        }

        # Create natives and assets folders
        if not os.path.exists(self.minecraft["natives"]):
            os.makedirs(self.minecraft["natives"])
        if not os.path.exists(self.minecraft["assets"]):
            os.makedirs(self.minecraft["assets"])

        # ClassPath
        self.parseClassPath()
        self.downloadClassPathFiles()
        self.buildClassPath()

        # Assets
        self.downloadAssets()

    def debug(self, text):
        if self.debug_info:
            print(f"[pyMinecraft] [Resources] {text}")

    # name, path, url, os
    def parseClassPath(self):
        downloads = []
        for x in self.client_json["libraries"]:
            check_rules = "rules" in x.keys()
            if not check_rules:
                # Any OS
                downloads.append({
                    "name": x["name"],
                    "path": self.minecraft["folder"] + "/libraries/" + x["downloads"]["artifact"]["path"],
                    "url": x["downloads"]["artifact"]["url"],
                    "os": "any"
                })
            else:
                os_type, os_bit = self.detectPlatform()

                # Mac OS
                if os_type == "macos" and x["rules"][0]["os"]["name"] == "osx":
                    lib_bit = BIT0
                    if x["name"].endswith("macos-arm64"):
                        lib_bit = BIT64
                    elif x["name"].endswith("macos"):
                        lib_bit = BIT32
                    else:
                        downloads.append({
                            "name": x["name"],
                            "path": self.minecraft["folder"] + "/libraries/" + x["downloads"]["artifact"]["path"],
                            "url": x["downloads"]["artifact"]["url"],
                            "os": "macos"
                        })

                    if str(lib_bit) == str(os_bit):
                        downloads.append({
                            "name": x["name"],
                            "path": self.minecraft["folder"] + "/libraries/" + x["downloads"]["artifact"]["path"],
                            "url": x["downloads"]["artifact"]["url"],
                            "os": "macos" + os_bit
                        })

                # Windows OS
                if os_type == "windows" and x["rules"][0]["os"]["name"] == "windows":
                    lib_bit = BIT0
                    if x["name"].endswith("windows"):
                        lib_bit = BIT64
                    elif x["name"].endswith("windows-x86"):
                        lib_bit = BIT32
                    else:
                        downloads.append({
                            "name": x["name"],
                            "path": self.minecraft["folder"] + "/libraries/" + x["downloads"]["artifact"]["path"],
                            "url": x["downloads"]["artifact"]["url"],
                            "os": "windows"
                        })

                    if str(lib_bit) == str(os_bit):
                        downloads.append({
                            "name": x["name"],
                            "path": self.minecraft["folder"] + "/libraries/" + x["downloads"]["artifact"]["path"],
                            "url": x["downloads"]["artifact"]["url"],
                            "os": "windows" + os_bit
                        })

                # Linux OS
                if os_type == "linux" and x["rules"][0]["os"]["name"] == "linux":
                    lib_bit = BIT0
                    if x["name"].endswith("x86_64"):
                        lib_bit = BIT32
                    elif x["name"].endswith("aarch_64"):
                        lib_bit = BIT64
                    else:
                        downloads.append({
                            "name": x["name"],
                            "path": self.minecraft["folder"] + "/libraries/" + x["downloads"]["artifact"]["path"],
                            "url": x["downloads"]["artifact"]["url"],
                            "os": "linux"
                        })

                    if str(lib_bit) == str(os_bit):
                        downloads.append({
                            "name": x["name"],
                            "path": self.minecraft["folder"] + "/libraries/" + x["downloads"]["artifact"]["path"],
                            "url": x["downloads"]["artifact"]["url"],
                            "os": "linux" + os_bit
                        })

                # Unknown OS
                if not os_type == "macos" and "windows" and "linux":
                    print("### OS TYPE IS MISSING", "\nYour os: ", os_type, "\nNeedle os: macos/linux/windows")
                    exit(0)

        downloads.append({
            "name": "client",
            "path": self.minecraft["folder"] + "/versions/client.jar",
            "url": self.version["url"]
        })
        self.libraries = downloads

    def downloadClassPathFiles(self):
        for x in self.libraries:
            folder = "/".join(x['path'].split("/")[:-1])
            if not os.path.exists(folder):
                os.makedirs(folder)
            if not os.path.exists(x['path']):
                self.debug(f"Downloading: {x['path']} from {x['url']}")

                with open(x['path'], "wb") as lib_file:
                    lib_file.write(requests.get(x["url"]).content)
                    lib_file.close()

    def buildClassPath(self):
        paths_ = []
        for x in self.libraries:
            paths_.append(x['path'])

        os_type, _ = self.detectPlatform()
        if os_type == "macos" or "linux":
            self.minecraft["classPath"] = ":".join(paths_)
        elif os_type == "windows":
            self.minecraft["classPath"] = ";".join(paths_)
        else:
            print("### OS TYPE IS MISSING", "\nYour os: ", os_type, "\nNeedle os: macos/linux/windows")
            exit(0)

    def downloadAssets(self):
        """ TODO: Download assets file """

    def detectPlatform(self):
        import platform, struct
        platform_type = {
            "Darwin": "macos",
            "Windows": "windows",
            "Linux": "linux"
        }[platform.system()]
        bit_size = struct.calcsize("P")
        if bit_size == 8:
            os_bit = "64"
        elif bit_size == 4:
            os_bit = "32"
        else:
            os_bit = "unknown"
        return platform_type, os_bit
