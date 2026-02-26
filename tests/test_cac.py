from smart_model_card.cac import ComputerAssistedCoder


def test_cac_suggests_codes():
    vocab = {
        "copd": ("J44", "ICD-10"),
        "hypertension": ("I10", "ICD-10")
    }
    cac = ComputerAssistedCoder(vocab)
    hits = cac.suggest_codes("Patient has COPD and hypertension")
    codes = {h.code for h in hits}
    assert "J44" in codes
    assert "I10" in codes
