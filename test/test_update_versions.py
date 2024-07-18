import json
import unittest

import src.semantic_versioning as sv
from src.update_versions import _update_container, _update_helm


class TestUpdateVersions(unittest.TestCase):
    @staticmethod
    def clone_dict(some_dict):
        return json.loads(json.dumps(some_dict))

    def test_update_container(self):
        versions = {
            "container_image_version": {
                "postgres": "8.0",
                "mysql": "999.0",
            },
        }
        old_versions = self.clone_dict(versions)

        result = _update_container(versions, "major")

        self.assertTrue(result)
        self.assertGreater(
            sv.parse(versions["container_image_version"]["postgres"]),
            sv.parse(old_versions["container_image_version"]["postgres"]),
        )
        self.assertEqual(
            sv.parse(versions["container_image_version"]["mysql"]),
            sv.parse(old_versions["container_image_version"]["mysql"]),
        )

    def test_update_helm(self):
        versions = {
            "helm_chart_repository": {
                "minio": "https://charts.min.io/",
                "dagster": "https://dagster-io.github.io/helm",
            },
            "helm_chart_version": {
                "minio/minio": "5.0.0",
                "dagster/dagster": "999.0.0",
            },
        }
        old_versions = self.clone_dict(versions)

        result = _update_helm(versions, "major")

        self.assertTrue(result)
        self.assertGreater(
            sv.parse(versions["helm_chart_version"]["minio/minio"]),
            sv.parse(old_versions["helm_chart_version"]["minio/minio"]),
        )
        self.assertEqual(
            sv.parse(versions["helm_chart_version"]["dagster/dagster"]),
            sv.parse(old_versions["helm_chart_version"]["dagster/dagster"]),
        )


if __name__ == "__main__":
    unittest.main()
