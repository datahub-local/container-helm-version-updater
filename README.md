# Container image and Helm chart versions update Action

[![Test](https://github.com/datahub-local/container-helm-version-updater/actions/workflows/test.yml/badge.svg)](https://github.com/datahub-local/container-helm-version-updater/actions/workflows/test.yml)
[![GitHub release badge](https://badgen.net/github/release/datahub-local/container-helm-version-updater/stable)](https://github.com/datahub-local/container-helm-version-updater/releases/latest)
[![GitHub license badge](https://badgen.net/github/license/datahub-local/container-helm-version-updater)](https://github.com/datahub-local/container-helm-version-updater/blob/main/LICENSE)

Action to update container image and Helm versions. This action will use Container Image provider APIs (only compatible with **hub.docker.com** **ghcr.io**) and Helm repositories to get the newest version (using [Semantic Versioning](https://semver.org/) logic), without the need to pull the images or charts.

For now, it is not able to parse projects and update theirs files directly. Therefore, it needs a version file in YAML format like the following one:

```yaml
container_image_version:
  postgresql/postgresql: '15.0'

helm_chart_repository:
  bitnami: https://charts.bitnami.com/bitnami
helm_chart_version:
  bitnami/postgresql: 10.0.1
```

## Inputs

| Name             | Type    | Description                                                                                                |
| ---------------- | ------- | ---------------------------------------------------------------------------------------------------------- |
| `versions-file`  | String  | Path to the versions file                                                                                  |
| `skip-container` | Boolean | true if you want to update only Container images. Default: false                                           |
| `skip-helm`      | Boolean | true if you want to update only Helm charts. Default: false                                                |
| `version-type`   | String  | Which maximun version change you expect to find. It can be: `major`, `minor` and `patch`. Default: `minor` |

> **Note**
>
> For parsing  **ghcr.io** container packages, the `GITHUB_TOKEN` is obligatory.

## Output

| Name | Type | Description |
| ---- | ---- | ----------- |


## Example

```yaml
name: Version updater

on:
  schedule:
    - cron:  '0 4 * * *'

jobs:
  version-update:
    runs-on: ubuntu-latest
    steps:
      - name: Set variables
        id: vars
        run: |
          echo "current_date=$(date --iso-8601=date)" >> $GITHUB_OUTPUT

      - name: Update versions
        id: check
        uses: datahub-local/container-helm-version-updater@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          versions-file: values/versions.yaml
          version-type: minor
          
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: 'chore: bump version of Helm Charts / Container Images until ${{ steps.vars.outputs.current_date }}'
          branch: "chore/bump_versions_${{ steps.vars.outputs.current_date }}"
          title: 'Bump version of Helm Charts / Container Images (${{ steps.vars.outputs.current_date }})'
```


<!--
## Create Github Action version

```bash
VERSION=v1

git push origin :$VERSION || true && git tag -d $VERSION || true && git tag $VERSION && git push --tags
```
-->