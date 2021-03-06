import json
import pytest

import sdk_cmd
import sdk_fault_domain
import sdk_install
import sdk_utils

from tests import config, test_utils


@pytest.mark.sanity
@pytest.mark.dcos_min_version("1.11")
@sdk_utils.dcos_ee_only
def test_zones_not_referenced_in_placement_constraints():
    foldered_name = sdk_utils.get_foldered_name(config.SERVICE_NAME)

    sdk_install.uninstall(config.PACKAGE_NAME, foldered_name)
    sdk_install.install(
        config.PACKAGE_NAME,
        foldered_name,
        config.DEFAULT_BROKER_COUNT,
        additional_options={"service": {"name": foldered_name}},
    )

    test_utils.broker_count_check(config.DEFAULT_BROKER_COUNT, service_name=foldered_name)

    rc, stdout, _ = sdk_cmd.svc_cli(config.PACKAGE_NAME, foldered_name, "broker list")
    assert rc == 0, "Broker list command failed"

    for broker_id in json.loads(stdout):
        rc, stdout, _ = sdk_cmd.svc_cli(
            config.PACKAGE_NAME, foldered_name, "broker get {}".format(broker_id)
        )
        assert rc == 0, "Broker get command failed"

        assert json.loads(stdout).get("rack") is None

    sdk_install.uninstall(config.PACKAGE_NAME, foldered_name)


@pytest.mark.sanity
@pytest.mark.dcos_min_version("1.11")
@sdk_utils.dcos_ee_only
def test_zones_referenced_in_placement_constraints():
    foldered_name = sdk_utils.get_foldered_name(config.SERVICE_NAME)

    sdk_install.uninstall(config.PACKAGE_NAME, foldered_name)
    sdk_install.install(
        config.PACKAGE_NAME,
        foldered_name,
        config.DEFAULT_BROKER_COUNT,
        additional_options={
            "service": {"name": foldered_name, "placement_constraint": '[["@zone", "GROUP_BY"]]'}
        },
    )

    test_utils.broker_count_check(config.DEFAULT_BROKER_COUNT, service_name=foldered_name)

    rc, stdout, _ = sdk_cmd.svc_cli(config.PACKAGE_NAME, foldered_name, "broker list")
    assert rc == 0, "Broker list command failed"

    for broker_id in json.loads(stdout):
        rc, stdout, _ = sdk_cmd.svc_cli(
            config.PACKAGE_NAME, foldered_name, "broker get {}".format(broker_id)
        )
        assert rc == 0, "Broker get command failed"

        assert sdk_fault_domain.is_valid_zone(json.loads(stdout).get("rack"))

    sdk_install.uninstall(config.PACKAGE_NAME, foldered_name)
