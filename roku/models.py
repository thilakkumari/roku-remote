from dataclasses import dataclass, field


@dataclass
class RokuDevice:
    name: str
    ip: str
    port: int = 8060

    @property
    def base_url(self):
        return f"http://{self.ip}:{self.port}"

    def __str__(self):
        return f"{self.name} ({self.ip})"


@dataclass
class RokuApp:
    app_id: str
    name: str
    version: str = ""

    def __str__(self):
        return self.name
