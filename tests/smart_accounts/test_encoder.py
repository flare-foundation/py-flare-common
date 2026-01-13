from py_flare_common.smart_accounts.encoder.decoder import Decoder
from py_flare_common.smart_accounts.encoder.instructions import (
    FxrpCollateralReservation,
)


def test_encoder_decoder():
    fcr = FxrpCollateralReservation(13, 13, 1)

    expected = "000d0000000000000000000d0001000000000000000000000000000000000000"

    assert expected == fcr.encode().hex()

    d = Decoder.with_all_instructions()

    decoded_cls = d.decode(expected)
    assert decoded_cls is FxrpCollateralReservation

    v = decoded_cls.decode(expected)

    assert v == fcr
