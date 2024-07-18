import argparse
from dataclasses import dataclass
import logging
import os
import re
import sys
from typing import Any, Dict, List

import src.semantic_versioning as sv

import requests
import yaml

logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

_HELM_REPOSITORY_CHART_VERSION_CACHE = {}


def _str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        return False


def _remove_emtpy(entries):
    if entries:
        return [e for e in entries if e]


def _get_helm_versions(repo_name: str, repo_url: str, chart_name) -> List[str]:
    global _HELM_REPOSITORY_CHART_VERSION_CACHE

    try:
        if repo_name not in _HELM_REPOSITORY_CHART_VERSION_CACHE:
            logging.info("Loading charts for repoisitory '%s'", repo_name)

            response = requests.get(f"{repo_url}/index.yaml")

            response.raise_for_status()

            index_data = yaml.safe_load(response.text)

            _HELM_REPOSITORY_CHART_VERSION_CACHE[repo_name] = {}

            for _key, _value in index_data.get("entries").items():
                versions = [
                    sv.parse(v.get("version"))
                    for v in sorted(
                        _value,
                        key=lambda x: sv.parse(x["version"]),
                        reverse=True,
                    )
                ]

                _HELM_REPOSITORY_CHART_VERSION_CACHE[repo_name][_key] = versions

        return _HELM_REPOSITORY_CHART_VERSION_CACHE.get(repo_name).get(chart_name)
    except Exception as e:
        logging.warning("Error getting charts for '%s': %s", repo_name, str(e))


def _fetch_docker_hub_url(url, headers={}, max_items=100):
    data = []

    while url and len(data) < max_items:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data.extend(response.json().get("results"))
            url = response.json().get("next")
        else:
            logging.warning(
                "Failed to retrieve url[{url}]: {response.status_code} - {response.text}"
            )
            break
    return data


def _fetch_github_url(url, headers={}, max_items=100):
    def _get_next_page_url(response):
        if "Link" in response.headers:
            links = response.headers["Link"]
            for link in links.split(","):
                if 'rel="next"' in link:
                    return link[link.find("<") + 1 : link.find(">")]
        return None

    data = []
    while url and len(data) < max_items:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data.extend(response.json())
            url = _get_next_page_url(response)
        else:
            logging.warning(
                "Failed to retrieve url[{url}]: {response.status_code} - {response.text}"
            )
            break
    return data


def _get_container_versions(image_name: str) -> List[str]:
    if not image_name:
        return None

    image_paths = image_name.split("/")
    image_paths_size = len(image_paths)

    if image_paths_size <= 2:
        if image_paths_size == 1:
            image_name = f"library/{image_name}"

        registry_url = "https://registry.hub.docker.com"
        url = f"{registry_url}/v2/repositories/{image_name}/tags"

        tags = _fetch_docker_hub_url(url)

        if tags:
            return _remove_emtpy([sv.parse(tag.get("name")) for tag in tags])
        else:
            logging.warning(f"Failed to fetch tags for {image_name}.")
            return None
    elif image_paths_size == 3:
        registry_name = image_paths[0]
        image_name = image_paths[1:]

        if registry_name == "ghcr.io" and "GITHUB_TOKEN" in os.environ:
            organization_name, package_name = image_name

            registry_url = "https://api.github.com"

            url = f"{registry_url}/orgs/{organization_name}/packages/container/{package_name}/versions"

            token = os.environ.get("GITHUB_TOKEN")
            packages = _fetch_github_url(
                url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {token}",
                },
            )

            if packages:
                return _remove_emtpy(
                    [
                        sv.parse(
                            p.get("metadata", {})
                            .get("container", {})
                            .get("tags", [None])[0]
                        )
                        for p in packages
                    ]
                )
            else:
                logging.warning(f"Failed to fetch packages for {image_name}")
                return None


CONTAINER_IMAGE_VERSION_ATTRIBURE = "container_image_version"
HELM_CHART_VERSION_ATTRIBURE = "helm_chart_version"
HELM_CHART_REPOSITORY_ATTRIBURE = "helm_chart_repository"


def _update_container(versions: Dict[str, Any], version_type: str) -> bool:
    container_image_versions = versions.get("container_image_version", {})

    modified = False

    if container_image_versions:
        for (
            image_name,
            _current_version,
        ) in container_image_versions.items():
            current_version = sv.parse(_current_version)

            container_versions = _get_container_versions(image_name)
            last_version = sv.get_last_valid_version(
                container_versions, current_version, version_type
            )

            if last_version:
                logging.info(
                    "Update cotainer image '%s' to version '%s' => '%s'",
                    image_name,
                    current_version.version,
                    last_version.version,
                )

                container_image_versions[image_name] = last_version.version

                modified = True

        if modified:
            versions["container_image_version"] = container_image_versions

    return modified


def _update_helm(versions: Dict[str, Any], version_type: str) -> bool:
    helm_chart_versions = versions.get(HELM_CHART_VERSION_ATTRIBURE, {})
    helm_chart_repository = versions.get(HELM_CHART_REPOSITORY_ATTRIBURE, {})

    modified = False

    if helm_chart_versions and helm_chart_repository:
        for full_chart_name, _current_version in helm_chart_versions.items():
            current_version = sv.parse(_current_version)

            repo_name, chart_name = full_chart_name.split("/")
            repo_url = helm_chart_repository.get(repo_name)

            if repo_url:
                helm_versions = _get_helm_versions(repo_name, repo_url, chart_name)
                last_version = sv.get_last_valid_version(
                    helm_versions,
                    current_version,
                    version_type,
                )

                if last_version:
                    logging.info(
                        "Update chart '%s' to version '%s' => '%s'",
                        chart_name,
                        current_version.version,
                        last_version.version,
                    )

                    helm_chart_versions[full_chart_name] = last_version.version

                    modified = True
                else:
                    logging.warning(
                        "Chart '%s' does not have a repo_url", full_chart_name
                    )

        if modified:
            versions[HELM_CHART_VERSION_ATTRIBURE] = helm_chart_versions

    return modified


def _update_versions(
    versions_path: str, skip_helm: bool, skip_cotainer: bool, version_type: str
):
    with open(versions_path, "r") as f:
        versions = yaml.safe_load(f)

        modified = False

        if not skip_cotainer:
            modified = _update_container(versions, version_type)

        if not skip_helm:
            modified = _update_helm(versions, version_type)

        if modified:
            with open(versions_path, "w") as fw:
                yaml.dump(versions, fw)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--versions-file",
        required=True,
        dest="versions_file",
        help="Path to the YAML file",
    )
    parser.add_argument("--skip-helm", dest="skip_helm", type=_str2bool, default=True)
    parser.add_argument(
        "--skip-container", dest="skip_container", type=_str2bool, default=True
    )
    parser.add_argument(
        "--version-type", dest="version_type", type=_str2bool, default="minor"
    )
    args = parser.parse_args()

    logging.info(
        "Updating Container image and Helm chart versions for '%s'", args.versions
    )

    _update_versions(args.versions_path)

    logging.info(
        "Updated Container image and Helm chart versions for '%s'", args.versions
    )


if __name__ == "__main__":
    main()
