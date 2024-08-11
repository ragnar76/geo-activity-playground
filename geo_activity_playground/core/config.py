import dataclasses
import functools
import json
import logging
import pathlib
from typing import Optional

from geo_activity_playground.core.paths import new_config_file


try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Config:
    birth_year: Optional[int] = None
    heart_rate_resting: int = 0
    heart_rate_maximum: Optional[int] = None

    equipment_offsets: dict[str, float] = dataclasses.field(default_factory=dict)
    kinds_without_achievements: list[str] = dataclasses.field(default_factory=list)
    metadata_extraction_regexes: list[str] = dataclasses.field(default_factory=list)
    num_processes: Optional[int] = None
    privacy_zones: dict[str, list[list[float]]] = dataclasses.field(
        default_factory=dict
    )
    strava_client_id: int = 131693
    strava_client_secret: str = "0ccc0100a2c218512a7ef0cea3b0e322fb4b4365"
    strava_client_code: Optional[str] = None
    upload_password: Optional[str] = None


class ConfigAccessor:
    def __init__(self) -> None:
        if new_config_file().exists():
            with open(new_config_file()) as f:
                self._config = Config(**json.load(f))
        else:
            self._config = Config()

    def __call__(self) -> Config:
        return self._config

    def save(self) -> None:
        with open(new_config_file(), "w") as f:
            json.dump(
                dataclasses.asdict(self._config),
                f,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )


@functools.cache
def get_config() -> dict:
    config_path = pathlib.Path("config.toml")
    if not config_path.exists():
        logger.warning("Missing a config, some features might be missing.")
        return {}
    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    return config


def import_old_config(config_accessor: ConfigAccessor) -> None:
    old_config_path = pathlib.Path("config.toml")
    if not old_config_path.exists():
        return

    if new_config_file().exists():
        logger.warning(
            "You have an old 'config.toml' which is now superseded by the 'config.json'. You can check the contents of the new 'config.json' and then delete the old 'config.toml'."
        )
        return

    old_config = get_config()
    config = config_accessor()

    if "metadata_extraction_regexes" in old_config:
        config.metadata_extraction_regexes = old_config["metadata_extraction_regexes"]

    if "heart" in old_config:
        if "birthyear" in old_config["heart"]:
            config.birth_year = old_config["heart"]["birthyear"]
        if "resting" in old_config["heart"]:
            config.heart_rate_resting = old_config["heart"]["resting"]
        if "maximum" in old_config["heart"]:
            config.heart_rate_maximum = old_config["heart"]["maximum"]

    if "strava" in old_config:
        if "client_id" in old_config["strava"]:
            config.strava_client_id = old_config["strava"]["client_id"]
        if "client_secret" in old_config["strava"]:
            config.strava_client_secret = old_config["strava"]["client_secret"]
        if "code" in old_config["strava"]:
            config.strava_client_code = old_config["strava"]["code"]

    if "offsets" in old_config:
        config.equipment_offsets = old_config["offsets"]

    if "upload" in old_config:
        if "password" in old_config["upload"]:
            config.upload_password = old_config["upload"]["password"]

    if "privacy_zones" in old_config:
        config.privacy_zones = old_config["privacy_zones"]

    config_accessor.save()
