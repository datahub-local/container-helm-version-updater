from dataclasses import dataclass, field
import re
from typing import List


SEMANTIC_VERSIONING_REGEX = r"^v?(\d+)(\.\d+)?(.+)?$"


@dataclass(order=True)
class SemanticVersion:
    major: str
    minor: str
    patch: str
    version: str = field(default_factory=str, compare=False)

    def __init__(self, version: str):
        def _atoi(text):
            if text:
                return "{:09}".format(int(text)) if text.isdigit() else text
            else:
                return ""

        def _to_human_number(text):
            if text:
                return "".join([_atoi(c) for c in re.split(r"(\d+)", text) if _atoi(c)])
            else:
                return ""

        self.version = str(version)

        m = re.match(SEMANTIC_VERSIONING_REGEX, self.version)
        if m:
            self.major = _to_human_number(m.group(1))
            self.minor = _to_human_number(m.group(2)).lstrip(".")
            self.patch = _to_human_number(m.group(3)).lstrip(".")
        else:
            raise ValueError(f"Invalid semantic version[{version}]")

    def version_type(self):
        if self.major and self.minor and self.patch and self.patch and any(not c.isnumeric() for c in self.patch):
            return 4
        if self.major and self.minor and self.patch:
            return 3
        if self.major and self.minor:
            return 2
        if self.major:
            return 1
        return 0


def parse(version: str) -> SemanticVersion:
    try:
        return SemanticVersion(version)
    except Exception as e:
        return None


def is_newer(
    version_to: SemanticVersion,
    version_from: SemanticVersion,
    version_type: str = "major",
) -> bool:
    if version_from.version_type() != version_to.version_type():
        return False

    if version_type.lower() == "major":
        return (
            version_to.major > version_from.major
            or (
                version_to.major == version_from.major
                and version_to.minor > version_from.minor
            )
            or (
                version_to.major == version_from.major
                and version_to.minor == version_from.minor
                and version_to.patch > version_from.patch
            )
        )
    elif version_type.lower() == "minor":
        return version_to.major == version_from.major and (
            version_to.minor > version_from.minor
            or (
                version_to.minor == version_from.minor
                and version_to.patch > version_from.patch
            )
        )
    elif version_type.lower() == "patch":
        return (
            version_to.major == version_from.major
            and version_to.minor == version_from.minor
            and version_to.patch > version_from.patch
        )
    else:
        raise ValueError(
            "Invalid version_type. Use 'major', 'minor', or 'patch'.")


NONE_FINAL_VERSION_FILTER_REGEX = re.compile(
    r"^.*(alpha|[0-9]+[abs][0-9]+|beta|dev|snap).*$")


def get_last_valid_version(
    versions: List[SemanticVersion],
    current_version: SemanticVersion,
    version_type: str = "major",
) -> SemanticVersion:
    if not versions or not current_version:
        return None

    sorted_versions = sorted(versions, reverse=True)
    valid_versions = [
        v
        for v in sorted_versions
        if is_newer(v, current_version, version_type)
        and not re.match(NONE_FINAL_VERSION_FILTER_REGEX, v.version)
    ]

    return valid_versions[0] if valid_versions else None
