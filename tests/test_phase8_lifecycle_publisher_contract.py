from scripts.publish_production_lifecycle import publication_status


def test_zero_population_is_explicitly_blocked():
    assert publication_status(0) == "BLOCKED_ON_PRODUCTION_ENTRY_POPULATION"


def test_population_requires_real_acceptance():
    assert publication_status(1) == "REQUIRES_POPULATED_LIFECYCLE_ACCEPTANCE"
