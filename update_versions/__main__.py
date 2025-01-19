import argparse
import logging
import os

from update_versions import _str2bool, update_versions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--versions-file",
        dest="versions_file",
        help="Path to the YAML file",
        default=os.getenv("INPUT_VERSIONS_FILE", "version.yaml")
    )
    parser.add_argument("--version-type", dest="version_type",
                        default=os.getenv("INPUT_VERSION_TYPE", "minor"))
    parser.add_argument("--skip-helm", dest="skip_helm", type=_str2bool,
                        default=_str2bool(os.getenv("INPUT_SKIP_HELM", "false")))
    parser.add_argument(
        "--skip-container", dest="skip_container", type=_str2bool, default=_str2bool(os.getenv("INPUT_SKIP_CONTAINER", "false"))
    )
    parser.add_argument("--dry-mode", dest="dry_mode", action="store_true",
                        default=_str2bool(os.getenv("INPUT_DRY_MODE", "false")))
    args = parser.parse_args()

    logging.info(
        "Updating Container image and Helm chart versions [%s]", args
    )

    result = update_versions(
        (args.versions_file),
        args.version_type,
        skip_container=args.skip_container,
        skip_helm=args.skip_helm,
        dry_mode=args.dry_mode,
    )

    logging.info(
        "Updated Container image and Helm chart versions [%s]: %s",
        args,
        result,
    )


if __name__ == "__main__":
    main()
