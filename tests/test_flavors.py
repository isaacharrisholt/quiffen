import os
from pathlib import Path

from quiffen import AccountType, Qif


def test_finanzmanager_2020():
    """
    test for Issue #78

    https://github.com/isaacharrisholt/quiffen/issues/78

    Finanzmanager Deluxe 2020 Quicken export support

    """
    fm_qif = Path(__file__).parent / "test_files" / "test_FMQifTest2023-10-18.qif"
    assert os.path.isfile(fm_qif)
    qif = Qif.parse(fm_qif, encoding="iso-8859-1", lenient=True, debug=True)
    assert len(qif.parser_state.errors) == 0
    assert len(qif.accounts) == 1
    assert "Donation" in qif.categories
    assert "Africa" in qif.classes
    account = qif.accounts["Quiffen Default Account"]
    assert len(account.transactions) == 1
    tx = account.transactions[AccountType.BANK][1]
    assert tx.is_split
    pass
