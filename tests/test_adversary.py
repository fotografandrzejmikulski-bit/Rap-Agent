from src.omega.adversary import LocalAdversary


def test_generic_line_is_rejected() -> None:
    findings = LocalAdversary.inspect(["wszyscy są fałszywi"])
    assert findings and "GENERIC" in findings[0].codes


def test_distinctive_line_survives_prefilter() -> None:
    findings = LocalAdversary.inspect(["Parują szyby w autobusie, a ja pamiętam numer drzwi"])
    assert findings == []
