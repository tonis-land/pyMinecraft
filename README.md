# pyMinecraft
Python Minecraft client.

```python
from Minecraft.Resources import Resources
from Minecraft.Client import Client
import uuid

# original client_url for all versions: https://launchermeta.mojang.com/mc/game/version_manifest.json

client = Client(
    resources=Resources(
        settings={
            "client_url": "https://raw.githubusercontent.com/nikitt-code/tonisland-config/main/1.19.json",
            "servers": {
                "path": "servers.dat",
                "url": "https://raw.githubusercontent.com/nikitt-code/tonisland-config/main/servers.dat"
            },
            "options": {
                "path": "options.txt",
                "url": "https://raw.githubusercontent.com/nikitt-code/tonisland-config/main/options.txt"
            },
            "minecraft_folder": "testclient",
        },
        log=False
    ),
    java={
        "xmx": "1G",
        "xmn": "1G",
        "xms": "1G"
    },
    client={
        "nickname": "niki_tt",
        "uuid": uuid.uuid4().hex,
        "token": "12345",
        "userType": "offline"
    }
).start()
```
