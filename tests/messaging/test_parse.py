import pytest

from py_flare_common.fsp.messaging.byte_parser import ParseError
from py_flare_common.fsp.messaging.parse import (
    _submit_signature,
    fdc_submit1,
    fdc_submit2,
    fdc_submit_signature,
    ftso_submit1,
    ftso_submit2,
    ftso_submit_signature,
    parse_generic_tx,
    parse_submit1_tx,
    parse_submit2_tx,
    parse_submit_signature_tx,
)
from py_flare_common.fsp.messaging.types import (
    FdcMessage,
    FdcSubmit1,
    FdcSubmit2,
    FtsoMessage,
    FtsoSubmit1,
    FtsoSubmit2,
    ParsedMessage,
    ParsedPayload,
    Signature,
    SubmitSignature,
)
from py_flare_common.merkle.hexstr import to_bytes


class TestSubmit:
    @pytest.mark.parametrize(
        "payload, type, message_to_parse, v, r, s",
        [
            (
                b"\x01"
                + b"\x00" * 38
                + b"\x01"
                + b"\x02"
                + b"\x00" * 31
                + b"\x03"
                + b"\x00" * 31,
                1,
                b"\x00" * 38,
                "01",
                "02" + "0" * 62,
                "03" + "0" * 62,
            )
        ],
    )
    def test_submit_signature(self, payload, message_to_parse, type, v, r, s):
        type_p, message_to_parse_p, signature_p = _submit_signature(payload)

        assert type_p == type
        assert message_to_parse_p == message_to_parse
        assert isinstance(signature_p, Signature)
        assert signature_p.v == v
        assert signature_p.r == r
        assert signature_p.s == s

    @pytest.mark.parametrize(
        "payload",
        [
            b"\x01"
            + b"\x00" * 38
            + b"\x01"
            + b"\x02"
            + b"\x00" * 31
            + b"\x03"
            + b"\x00" * 31
            + b"\x00",
            b"\x01"
            + b"\x00" * 38
            + b"\x01"
            + b"\x02"
            + b"\x00" * 31
            + b"\x03"
            + b"\x00" * 30,
        ],
    )
    def test_submit_signature_wrong_data(self, payload):
        with pytest.raises(ParseError):
            _submit_signature(payload)

    @pytest.mark.parametrize(
        "message, voting_round_id_ftso, payload_length_ftso, payload_ftso, voting_round_id_fdc, payload_length_fdc, payload_fdc",
        [
            (
                (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00")
                + (b"\xc8" + b"\x00\x00\x00\x02" + b"\x00\x02" + b"\x00\x01"),
                1,
                2,
                b"\x00\x00",
                2,
                2,
                b"\x00\x01",
            ),
            (
                (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\xc0\x00")
                + (b"\xc8" + b"\x00\x00\x00\x02" + b"\x00\x02" + b"\x00\xc1")
                + (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00")
                + (b"\xc8" + b"\x00\x00\x00\x02" + b"\x00\x02" + b"\x00\x01"),
                1,
                2,
                b"\x00\x00",
                2,
                2,
                b"\x00\x01",
            ),
            (
                (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00").hex()
                + (b"\xc8" + b"\x00\x00\x00\x02" + b"\x00\x02" + b"\x00\x01").hex(),
                1,
                2,
                b"\x00\x00",
                2,
                2,
                b"\x00\x01",
            ),
        ],
    )
    def test_gen_parse(
        self,
        message,
        voting_round_id_ftso,
        payload_length_ftso,
        payload_ftso,
        voting_round_id_fdc,
        payload_length_fdc,
        payload_fdc,
    ):
        parsed_message = parse_generic_tx(
            message, lambda x: x + b"100", lambda x: x + b"200"
        )

        assert isinstance(parsed_message, ParsedMessage)

        ftso = parsed_message.ftso
        assert isinstance(ftso, ParsedPayload)
        assert ftso.protocol_id == 100
        assert ftso.voting_round_id == voting_round_id_ftso
        assert ftso.size == payload_length_ftso
        assert ftso.payload == payload_ftso + b"100"

        fdc = parsed_message.fdc
        assert isinstance(fdc, ParsedPayload)
        assert fdc.protocol_id == 200
        assert fdc.voting_round_id == voting_round_id_fdc
        assert fdc.size == payload_length_fdc
        assert fdc.payload == payload_fdc + b"200"

    @pytest.mark.parametrize(
        "message, protocol_id, voting_round_id, payload_length, payload",
        [
            (
                (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00"),
                100,
                1,
                2,
                b"\x00\x00",
            ),
            (
                (b"d" + b"\x00\x00\x00\x09" + b"\x00\x02" + b"\xc7\x00")
                + (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00"),
                100,
                1,
                2,
                b"\x00\x00",
            ),
            (
                (b"\xc8" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00"),
                200,
                1,
                2,
                b"\x00\x00",
            ),
            (
                (b"\xc8" + b"\x00\x00\x00\x09" + b"\x00\x02" + b"\xc7\x00").hex()
                + (b"\xc8" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00").hex(),
                200,
                1,
                2,
                b"\x00\x00",
            ),
        ],
    )
    def test_gen_parse_only_one_protocol(
        self, message, protocol_id, voting_round_id, payload_length, payload
    ):
        parsed_message = parse_generic_tx(message, pid_100_parse=lambda x: x)

        assert isinstance(parsed_message, ParsedMessage)

        if protocol_id == 100:
            data = parsed_message.ftso
            assert parsed_message.fdc is None
        elif protocol_id == 200:
            data = parsed_message.fdc
            assert parsed_message.ftso is None
        else:
            raise Exception

        assert isinstance(data, ParsedPayload)
        assert data.protocol_id == protocol_id
        assert data.voting_round_id == voting_round_id
        assert data.size == payload_length
        assert data.payload == payload

    @pytest.mark.parametrize("message", [""])
    def test_gen_parse_no_protocols(self, message):
        parsed_message = parse_generic_tx(message, pid_200_parse=lambda x: x)

        assert isinstance(parsed_message, ParsedMessage)
        assert parsed_message.ftso is None
        assert parsed_message.fdc is None

    @pytest.mark.parametrize(
        "message",
        [
            b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00\x00",
            b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00",
            (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\xc0\x00")
            + (b"\xc8" + b"\x00\x00\x00\x02" + b"\x00\x02" + b"\x00\xc1")
            + (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00")
            + (b"\xc8" + b"\x00\x00\x00\x02" + b"\x00\x01" + b"\x00\x01"),
            b"d\x00\x00\x00\x01\x00\x02\x00".hex(),
        ],
    )
    def test_gen_parse_error(self, message):
        with pytest.raises(ParseError):
            parse_generic_tx(message)

    @pytest.mark.parametrize("data, excepted", [(b"\x00", b"\x00"), ("00", b"\x00")])
    def test_to_bytes(self, data, excepted):
        assert to_bytes(data) == excepted

    @pytest.mark.parametrize("data", ["x0"])
    def test_to_bytes_wrong_string(self, data):
        with pytest.raises(ValueError):
            to_bytes(data)

    # Real life example: https://flare-systems-explorer.flare.network/top-level-protocol/60aa107e05da3c10ec2d0d51c5424ca85907c170fb31c19f929b96b7ea49e6aa
    @pytest.mark.parametrize(
        "message, protocol_id, voting_round_id, size, hash",
        [
            (
                "0x6c532fae64000c6620002005a93355a28127ff0ca2d8136648c1fd682e0041f8367ba4567586b3d4149d54"[
                    10:
                ],
                100,
                812576,
                32,
                bytes.fromhex(
                    "05a93355a28127ff0ca2d8136648c1fd682e0041f8367ba4567586b3d4149d54"
                ),
            )
        ],
    )
    def test_parse_submit1_tx(self, message, protocol_id, voting_round_id, size, hash):
        parsed_payload = parse_submit1_tx(message)
        assert isinstance(parsed_payload, ParsedMessage)

        ftso = parsed_payload.ftso
        fdc = parsed_payload.fdc
        assert fdc is None
        assert isinstance(ftso, ParsedPayload)
        assert ftso.protocol_id == protocol_id
        assert ftso.voting_round_id == voting_round_id
        assert ftso.size == size

        ftsoS1 = ftso.payload
        assert isinstance(ftsoS1, FtsoSubmit1)
        assert ftsoS1.commit_hash == hash

    @pytest.mark.parametrize(
        "message, protocol_id, voting_round_id, size, random, values",
        [
            (
                (
                    "0x9d00c9fd64000c662000e83ad6dadc250b9eee6480e729a9b615185c01e067e15738"
                    + "cafe352d851b529c5a801a963f8000dfca800039bc8000f4458007e5b5803311dc804"
                    + "32212805ff7b9800098378089430f8001869f8000996b8007cd798000e83180223021"
                    + "80311c9480027c2e8002001180064824800038ae800117e180095205800d1b0c8001c"
                    + "afd800bd5d38014b103807c895c8007fd01800130fa80015bc48003979e8000931880"
                    + "00a1b78060a3b7800ab8148008a8e18000db888000655e80215923800540998053243"
                    + "580084836800045f8800d346480018695800186e5800654108000762b8001e52e80010feb"
                )[10:],
                100,
                812576,
                232,
                26613761005485227210124837044607206462361910438060874105373946905076167777370,
                [
                    1742399,
                    57290,
                    14780,
                    62533,
                    517557,
                    3346908,
                    4399634,
                    6289337,
                    38967,
                    8995599,
                    99999,
                    39275,
                    511353,
                    59441,
                    2240545,
                    3218580,
                    162862,
                    131089,
                    411684,
                    14510,
                    71649,
                    610821,
                    858892,
                    117501,
                    775635,
                    1356035,
                    8161628,
                    523521,
                    78074,
                    89028,
                    235422,
                    37656,
                    41399,
                    6333367,
                    702484,
                    567521,
                    56200,
                    25950,
                    2185507,
                    344217,
                    5448757,
                    542774,
                    17912,
                    865380,
                    99989,
                    100069,
                    414736,
                    30251,
                    124206,
                    69611,
                ],
            )
        ],
    )
    def test_parse_submit2_tx(
        self, message, protocol_id, voting_round_id, size, random, values
    ):
        parsed_payload = parse_submit2_tx(message)
        assert isinstance(parsed_payload, ParsedMessage)

        ftso = parsed_payload.ftso
        fdc = parsed_payload.fdc
        assert fdc is None
        assert isinstance(ftso, ParsedPayload)
        assert ftso.protocol_id == protocol_id
        assert ftso.voting_round_id == voting_round_id
        assert ftso.size == size

        ftsoS1 = ftso.payload
        assert isinstance(ftsoS1, FtsoSubmit2)
        assert ftsoS1.random == random
        assert ftsoS1.values == values

    # Real life example: https://flare-systems-explorer.flare.network/top-level-protocol/b867d0a0a177bbcf97b9e6743eeaf04f9e95ac52724498dc8a4c448677c713d9
    @pytest.mark.parametrize(
        "message, protocol_id, voting_round_id, size, type, v, r, s, mess_protocol_id, random_quality_score, merkle_root",
        [
            (
                (
                    "0x57eed58064000c667600680064000c667601200163ea6a576ea7fc46557b8611"
                    + "339d01e9b0d832d80060f892e02afe7700121c03e351a3079a4fcbb8c3fa2a8e"
                    + "241107d28fd9387d25157a341c3afc29a2eead1cdc60119c390e089ecf940d61"
                    + "769b226b48c9056b5b095d3e83f3363442bb12"
                )[10:],
                100,
                812662,
                104,
                0,
                "1c",
                "03e351a3079a4fcbb8c3fa2a8e241107d28fd9387d25157a341c3afc29a2eead",
                "1cdc60119c390e089ecf940d61769b226b48c9056b5b095d3e83f3363442bb12",
                100,
                1,
                "200163ea6a576ea7fc46557b8611339d01e9b0d832d80060f892e02afe770012",
            )
        ],
    )
    def test_parse_submit_signature_tx(
        self,
        message,
        protocol_id,
        voting_round_id,
        size,
        type,
        v,
        r,
        s,
        mess_protocol_id,
        random_quality_score,
        merkle_root,
    ):
        parsed_payload = parse_submit_signature_tx(message)
        assert isinstance(parsed_payload, ParsedMessage)

        ftso = parsed_payload.ftso
        fdc = parsed_payload.fdc
        assert fdc is None
        assert isinstance(ftso, ParsedPayload)
        assert ftso.protocol_id == protocol_id
        assert ftso.voting_round_id == voting_round_id
        assert ftso.size == size

        ftsoS1 = ftso.payload
        assert isinstance(ftsoS1, SubmitSignature)
        assert ftsoS1.type == type

        ftso_signature = ftsoS1.signature
        assert isinstance(ftso_signature, Signature)
        assert ftso_signature.v == v
        assert ftso_signature.r == r
        assert ftso_signature.s == s

        ftso_message = ftsoS1.message
        assert isinstance(ftso_message, FtsoMessage)
        assert ftso_message.protocol_id == mess_protocol_id
        assert ftso_message.merkle_root == merkle_root
        assert ftso_message.random_quality_score == random_quality_score


class TestFtsoSubmit:
    @pytest.mark.parametrize(
        "payload",
        [
            b"12345678901234567890123456789012",
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x00\x48\x65\x6c\x6c\x6f\x00\x48\x65\x6c\x6c\x6f",
        ],
    )
    def test_ftso_submit1(self, payload):
        ftsoS1 = ftso_submit1(payload)
        assert isinstance(ftsoS1, FtsoSubmit1)
        assert ftsoS1.commit_hash == payload

    @pytest.mark.parametrize(
        "payload",
        [
            b"1234567890123456789012345678901",
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x00\x48\x65\x6c\x6c\x6f\x00\x48\x65\x6c\x6c\x6f\x00",
        ],
    )
    def test_ftso_submit1_wrong_length(self, payload):
        with pytest.raises(ParseError):
            ftso_submit1(payload)

    @pytest.mark.parametrize(
        "payload, random, values",
        [
            (
                b"12345678901234567890123456789012\x07[\xcd\x15\x00\x00\x00\x00",
                22252025330403739761828227648604333229819926301751889444568374711659082559794,
                [123456789 - 2**31, None],
            )
        ],
    )
    def test_ftso_submit2(self, payload, random, values):
        ftsoS2 = ftso_submit2(payload)

        assert isinstance(ftsoS2, FtsoSubmit2)
        assert ftsoS2.random == random
        assert ftsoS2.values == values

    @pytest.mark.parametrize(
        "payload",
        [b"12345678901234567890123456789012\x07[\xcd\x15\x00\x00\x00\x00\x00"],
    )
    def test_ftso_submit2_parse_error(self, payload):
        with pytest.raises(ParseError):
            ftso_submit2(payload)

    @pytest.mark.parametrize(
        "payload, protocol_id, random_quality_score, merkle_root",
        [
            (
                b"\x01"
                + b"\x05"
                + b"\x00\x00\x00\x00"
                + b"\x06"
                + b"\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c"
                + b"\x00" * 65,
                5,
                6,
                "656c656c656c656c656c656c656c656c656c656c656c656c656c656c656c656c",
            )
        ],
    )
    def test_ftso_submit_signature(
        self, payload, protocol_id, random_quality_score, merkle_root
    ):
        ftsoSS = ftso_submit_signature(payload)

        assert isinstance(ftsoSS, SubmitSignature)
        assert isinstance(ftsoSS.signature, Signature)
        assert isinstance(ftsoSS.message, FtsoMessage)
        assert ftsoSS.message.protocol_id == protocol_id
        assert ftsoSS.message.random_quality_score == random_quality_score
        assert ftsoSS.message.merkle_root == merkle_root


class TestFdcSubmit:
    def test_fdc_submit1(self):
        with pytest.raises(ParseError):
            fdc_submit1(b"\x00")

    def test_fdc_submit1_empty_payload(self):
        fdc_S1 = fdc_submit1(b"")
        assert isinstance(fdc_S1, FdcSubmit1)

    @pytest.mark.parametrize(
        "payload, n_requests, bit_vector",
        [
            (b"\x00\x05\x0b", 5, [False, True, False, True, True]),
            (
                b"\x00\x09\x6c",
                9,
                [False, False, True, True, False, True, True, False, False],
            ),
        ],
    )
    def test_fdc_submit2(self, payload, n_requests, bit_vector):
        fdcS2 = fdc_submit2(payload)

        assert isinstance(fdcS2, FdcSubmit2)
        assert fdcS2.number_of_requests == n_requests
        assert fdcS2.bit_vector == bit_vector

    @pytest.mark.parametrize(
        "payload",
        [b"\x00\x03\x0b"],
    )
    def test_fdc_submit2_parse_error(self, payload):
        with pytest.raises(ParseError):
            fdc_submit2(payload)

    @pytest.mark.parametrize(
        "payload, protocol_id, random_quality_score, merkle_root",
        [
            (
                b"\x01"
                + b"\x05"
                + b"\x00\x00\x00\x00"
                + b"\x06"
                + b"\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c"
                + b"\x00" * 65,
                5,
                6,
                "656c656c656c656c656c656c656c656c656c656c656c656c656c656c656c656c",
            )
        ],
    )
    def test_fdc_submit_signature(
        self, payload, protocol_id, random_quality_score, merkle_root
    ):
        fdcSS = fdc_submit_signature(payload)

        assert isinstance(fdcSS, SubmitSignature)
        assert isinstance(fdcSS.signature, Signature)
        assert isinstance(fdcSS.message, FdcMessage)
        assert fdcSS.message.protocol_id == protocol_id
        assert fdcSS.message.random_quality_score == random_quality_score
        assert fdcSS.message.merkle_root == merkle_root
