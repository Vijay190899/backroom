import re

import pytest

from backroom_portals import chaos, contract


def test_catalog_has_at_least_eight_families_with_canonical_first() -> None:
    assert len(chaos.FAMILIES) >= 8
    for family, variants in chaos.CATALOG.items():
        assert len(variants) >= 2, family
        assert len(set(variants)) == len(variants), family


@pytest.mark.parametrize("portal", contract.PORTALS)
def test_seed_zero_is_canonical(portal: contract.PortalName) -> None:
    assert chaos.pick_variants(portal, 0) == chaos.CANONICAL


@pytest.mark.parametrize("portal", contract.PORTALS)
def test_demo_seed_is_german_with_moved_nav_and_cookie_banner(portal: contract.PortalName) -> None:
    variants = chaos.pick_variants(portal, chaos.DEMO_SEED)
    assert variants["language"] == "de"
    assert variants["nav_position"] != chaos.CANONICAL["nav_position"]
    assert variants["interstitial"] == "cookie_banner"


def test_same_seed_same_variants_and_seeds_differ() -> None:
    picks = [chaos.pick_variants("grainline", seed) for seed in range(1, 40)]
    assert picks == [chaos.pick_variants("grainline", seed) for seed in range(1, 40)]
    assert all(p != chaos.CANONICAL for p in picks)
    assert len({tuple(sorted(p.items())) for p in picks}) >= 35
    for p in picks:
        assert all(p[f] in chaos.CATALOG[f] for f in chaos.FAMILIES)


def test_negative_seed_is_rejected() -> None:
    with pytest.raises(ValueError):
        chaos.pick_variants("grainline", -1)


@pytest.mark.parametrize(
    "routes",
    [contract.GRAINLINE_ROUTES, contract.TILLDESK_ROUTES, contract.LOCALBOARD_ROUTES],
)
def test_routes_are_unique_and_under_one_prefix(routes: dict[str, tuple[str, str]]) -> None:
    prefixes = {path.split("/")[1] for _, path in routes.values()}
    assert len(prefixes) == 1 and prefixes <= set(contract.PORTALS)
    assert len(set(routes.values())) == len(routes)


@pytest.mark.parametrize(
    "labels",
    [contract.GRAINLINE_LABELS, contract.TILLDESK_LABELS, contract.INTERSTITIAL_LABELS],
)
def test_every_label_has_three_forms_and_a_german_one(labels: dict[str, contract.Label]) -> None:
    for key, label in labels.items():
        assert all(label), key
        assert label.en != label.de, key


def test_testids() -> None:
    assert contract.testid("grainline", "add_to_cart") == "gl-add-to-cart"
    assert contract.testid("grainline", "add_to_cart", "OAT-1L") == "gl-add-to-cart-OAT-1L"
    assert contract.testid("tilldesk", "edit", "franzbroetchen") == "td-edit-franzbroetchen"


def test_demo_story_ids_and_prices() -> None:
    assert re.fullmatch(contract.ORDER_ID_PATTERN, "GW-10482")
    assert round(24 * contract.DEMO_PRICES_EUR["OAT-1L"], 2) == 38.16
    rise = contract.DEMO_PRICES_EUR["BUTTER-1KG"] / contract.DEMO_PRICES_EUR["BUTTER-1KG.before"]
    assert round((rise - 1) * 100) == 16
    assert "franzbroetchen" in contract.TILLDESK_ITEM_IDS


def test_tilldesk_state_is_addressable_by_item_id() -> None:
    state = contract.TillDeskState(
        items={
            "franzbroetchen": contract.MenuItem(
                id="franzbroetchen", name="Franzbrötchen", price_eur=3.6, published_price_eur=3.6
            )
        },
        last_published_at=None,
    )
    assert state.model_dump()["items"]["franzbroetchen"]["published_price_eur"] == 3.6


def test_secret_keys_map_to_env_vars() -> None:
    assert set(contract.SECRET_KEYS) >= {"grainline_user", "grainline_password", "grainline_totp"}
    assert all(v.isupper() for v in contract.SECRET_KEYS.values())
