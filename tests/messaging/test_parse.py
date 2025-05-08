import pytest

from py_flare_common._hexstr.hexstr import to_bytes
from py_flare_common.fsp.messaging.byte_parser import ParseError
from py_flare_common.fsp.messaging.parse import (
    fdc_submit1,
    fdc_submit2,
    ftso_submit1,
    ftso_submit2,
    parse_generic_tx,
    parse_submit1_tx,
    parse_submit2_tx,
    parse_submit_signature_tx,
    submit_signatures_type_0,
    submit_signatures_type_1,
)
from py_flare_common.fsp.messaging.types import (
    FdcSubmit1,
    FdcSubmit2,
    FtsoSubmit1,
    FtsoSubmit2,
    ParsedMessage,
    ParsedPayload,
    Signature,
    SubmitSignatures,
    SubmitSignaturesMessage,
)


class TestSubmit:
    @pytest.mark.parametrize(
        "message, voting_round_id_ftso, payload_length_ftso, payload_ftso, voting_round_id_fdc, payload_length_fdc, payload_fdc",
        [
            (
                (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00") + (b"\xc8" + b"\x00\x00\x00\x02" + b"\x00\x02" + b"\x00\x01"),
                1, 2, b"\x00\x00", 2, 2, b"\x00\x01",
            ),
            (
                (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\xc0\x00") + (b"\xc8" + b"\x00\x00\x00\x02" + b"\x00\x02" + b"\x00\xc1") + (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00") + (b"\xc8" + b"\x00\x00\x00\x02" + b"\x00\x02" + b"\x00\x01"),
                1, 2, b"\x00\x00", 2, 2, b"\x00\x01",
            ),
            (
                (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00").hex() + (b"\xc8" + b"\x00\x00\x00\x02" + b"\x00\x02" + b"\x00\x01").hex(),
                1, 2, b"\x00\x00", 2, 2, b"\x00\x01",
            ),
        ],
    )  # fmt: skip
    def test_gen_parse(
        self, message, voting_round_id_ftso, payload_length_ftso, payload_ftso, voting_round_id_fdc, payload_length_fdc, payload_fdc,
    ):  # fmt: skip
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
                100, 1, 2, b"\x00\x00",
            ),
            (
                (b"d" + b"\x00\x00\x00\x09" + b"\x00\x02" + b"\xc7\x00") + (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00"),
                100, 1, 2, b"\x00\x00",
            ),
            (
                (b"\xc8" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00"),
                200, 1, 2, b"\x00\x00",
            ),
            (
                (b"\xc8" + b"\x00\x00\x00\x09" + b"\x00\x02" + b"\xc7\x00").hex() + (b"\xc8" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00").hex(),
                200, 1, 2, b"\x00\x00",
            ),
        ],
    )  # fmt: skip
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
            (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\xc0\x00") + (b"\xc8" + b"\x00\x00\x00\x02" + b"\x00\x02" + b"\x00\xc1") + (b"d" + b"\x00\x00\x00\x01" + b"\x00\x02" + b"\x00\x00") + (b"\xc8" + b"\x00\x00\x00\x02" + b"\x00\x01" + b"\x00\x01"),
            b"d\x00\x00\x00\x01\x00\x02\x00".hex(),
        ],
    )  # fmt: skip
    def test_gen_parse_error(self, message):
        with pytest.raises(ParseError):
            parse_generic_tx(message)

    @pytest.mark.parametrize(
        "data, excepted",
        [
            (b"\x00", b"\x00"),
            ("00", b"\x00"),
            (b"\x6c\x53\x2f\xae", b""),
            (b"\x57\xee\xd5\x80\x00", b"\x00"),
            ("0x57eed58000", b"\x00"),
            ("57eed58000", b"\x00"),
        ],
    )
    def test_to_bytes(self, data, excepted):
        assert to_bytes(data) == excepted

    @pytest.mark.parametrize("data", ["x0", "0xx"])
    def test_to_bytes_wrong_string(self, data):
        with pytest.raises(ValueError):
            to_bytes(data)

    # Real life example: https://flare-systems-explorer.flare.network/top-level-protocol/60aa107e05da3c10ec2d0d51c5424ca85907c170fb31c19f929b96b7ea49e6aa
    @pytest.mark.parametrize(
        "message, protocol_id, voting_round_id, size, hash",
        [
            (
                "0x6c532fae64000c6620002005a93355a28127ff0ca2d8136648c1fd682e0041f8367ba4567586b3d4149d54"[10:],
                100, 812576, 32,
                bytes.fromhex("05a93355a28127ff0ca2d8136648c1fd682e0041f8367ba4567586b3d4149d54"),
            )
        ],
    )  # fmt: skip
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

        ftso_s1 = ftso.payload
        assert isinstance(ftso_s1, FtsoSubmit1)
        assert ftso_s1.commit_hash == hash

    # Real life example: https://flare-systems-explorer.flare.network/top-level-protocol/a65e3db73be6760559c2c13310bd0c3d8f2e456ea42a96838d3fc7f90bf33594
    @pytest.mark.parametrize(
        "message, protocol_id, voting_round_id, size, random, values",
        [
            (
                "0x9d00c9fd64000c662000e83ad6dadc250b9eee6480e729a9b615185c01e067e15738cafe352d851b529c5a801a963f8000dfca800039bc8000f4458007e5b5803311dc80432212805ff7b9800098378089430f8001869f8000996b8007cd798000e8318022302180311c9480027c2e8002001180064824800038ae800117e180095205800d1b0c8001cafd800bd5d38014b103807c895c8007fd01800130fa80015bc48003979e800093188000a1b78060a3b7800ab8148008a8e18000db888000655e80215923800540998053243580084836800045f8800d346480018695800186e5800654108000762b8001e52e80010feb"[10:],
                100, 812576, 232, 26613761005485227210124837044607206462361910438060874105373946905076167777370,
                [1742399, 57290, 14780, 62533, 517557, 3346908, 4399634, 6289337, 38967, 8995599, 99999, 39275, 511353, 59441, 2240545, 3218580, 162862, 131089, 411684, 14510, 71649, 610821, 858892, 117501, 775635, 1356035, 8161628, 523521, 78074, 89028, 235422, 37656, 41399, 6333367, 702484, 567521, 56200, 25950, 2185507, 344217, 5448757, 542774, 17912, 865380, 99989, 100069, 414736, 30251, 124206, 69611],
            )
        ],
    )  # fmt: skip
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

        ftso_s1 = ftso.payload
        assert isinstance(ftso_s1, FtsoSubmit2)
        assert ftso_s1.random == random
        assert ftso_s1.values == values

    @pytest.mark.parametrize(
        "message, protocol_id, voting_round_id, size, type, v, r, s, mess_protocol_id, random_quality_score, merkle_root",
        [
            (
                "0x57eed58064000c667600680064000c667601200163ea6a576ea7fc46557b8611339d01e9b0d832d80060f892e02afe7700121c03e351a3079a4fcbb8c3fa2a8e241107d28fd9387d25157a341c3afc29a2eead1cdc60119c390e089ecf940d61769b226b48c9056b5b095d3e83f3363442bb12"[10:],
                100, 812662, 104, 0, "1c", "03e351a3079a4fcbb8c3fa2a8e241107d28fd9387d25157a341c3afc29a2eead", "1cdc60119c390e089ecf940d61769b226b48c9056b5b095d3e83f3363442bb12",
                100, 1, "200163ea6a576ea7fc46557b8611339d01e9b0d832d80060f892e02afe770012",
            )
        ],
    )  # fmt: skip
    def test_parse_submit_signature_tx_type_0(
        self, message, protocol_id, voting_round_id, size, type, v, r, s, mess_protocol_id, random_quality_score, merkle_root,
    ):  # fmt: skip
        parsed_payload = parse_submit_signature_tx(message)
        assert isinstance(parsed_payload, ParsedMessage)

        ftso = parsed_payload.ftso
        fdc = parsed_payload.fdc
        assert fdc is None
        assert isinstance(ftso, ParsedPayload)
        assert ftso.protocol_id == protocol_id
        assert ftso.voting_round_id == voting_round_id
        assert ftso.size == size

        ftso_s1 = ftso.payload
        assert isinstance(ftso_s1, SubmitSignatures)
        assert ftso_s1.type == type

        ftso_signature = ftso_s1.signature
        assert isinstance(ftso_signature, Signature)
        assert ftso_signature.v == v
        assert ftso_signature.r == r
        assert ftso_signature.s == s

        ftso_message = ftso_s1.message
        assert isinstance(ftso_message, SubmitSignaturesMessage)
        assert ftso_message.protocol_id == mess_protocol_id
        assert ftso_message.merkle_root == merkle_root
        assert ftso_message.random_quality_score == random_quality_score

        assert ftso_s1.unsigned_message == b""

    # https://coston-systems-explorer.flare.rocks/top-level-protocol/0x5d83c1f3f8ecf72946fafb8cebd0816b8f06fd2d158683b580466ec741741966
    @pytest.mark.parametrize(
        "message, fdc_protocol_id, fdc_voting_round_id, fdc_size, fdc_type, fdc_message, fdc_v, fdc_r, fdc_s, fdc_unsigned_message, "
        + "ftso_protocol_id, ftso_voting_round_id, ftso_size, ftso_type, ftso_m_protocol_id, ftso_m_random_quality_score, ftso_m_merkle_root, ftso_v, ftso_r, ftso_s, ftso_unsigned_message",
        [
            (
                "0x57eed58064000cc47a00680064000cc47a01d3c1e3864d0b0da28fe5093b667d477062424820fa2feeabf958ba0f1b2324611b3af8d6e1ee5b98db8c6036a131595195ccfd7a97153f0672188057f0bcb6a29a1682f51a950ac9e3f35187c1c86ce7469145fece42c87eec592415f92254dc0bc8000cc47a0045011c3ce1bcea504f167586c19d8c50e71564c7aa5557125d34b07894594a36335feb2f57308692549f4cf67bcacacfb8bb743db6234659d6fead735a9d09a3e0d4b00008ff"[10:],
                200, 836730, 69, 1, None, "1c", "3ce1bcea504f167586c19d8c50e71564c7aa5557125d34b07894594a36335feb", "2f57308692549f4cf67bcacacfb8bb743db6234659d6fead735a9d09a3e0d4b0", b"\x00\x08\xff",
                100, 836730, 104, 0, 100, 1, "d3c1e3864d0b0da28fe5093b667d477062424820fa2feeabf958ba0f1b232461", "1b", "3af8d6e1ee5b98db8c6036a131595195ccfd7a97153f0672188057f0bcb6a29a", "1682f51a950ac9e3f35187c1c86ce7469145fece42c87eec592415f92254dc0b", b"",
            )
        ],
    )  # fmt: skip
    def test_parse_submit_signature_tx_type_0_and_1(
        self, message, fdc_protocol_id, fdc_voting_round_id, fdc_size, fdc_type, fdc_message, fdc_v, fdc_r, fdc_s, fdc_unsigned_message, ftso_protocol_id, ftso_voting_round_id, ftso_size, ftso_type, ftso_m_protocol_id, ftso_m_random_quality_score, ftso_m_merkle_root, ftso_v, ftso_r, ftso_s, ftso_unsigned_message,
    ):  # fmt: skip
        parsed_payload = parse_submit_signature_tx(message)
        assert isinstance(parsed_payload, ParsedMessage)

        fdc = parsed_payload.fdc
        assert isinstance(fdc, ParsedPayload)
        assert fdc.protocol_id == fdc_protocol_id
        assert fdc.voting_round_id == fdc_voting_round_id
        assert fdc.size == fdc_size

        fdc_s1 = fdc.payload
        assert isinstance(fdc_s1, SubmitSignatures)
        assert fdc_s1.type == fdc_type

        fdc_signature = fdc_s1.signature
        assert isinstance(fdc_signature, Signature)
        assert fdc_signature.v == fdc_v
        assert fdc_signature.r == fdc_r
        assert fdc_signature.s == fdc_s

        assert fdc_s1.message == fdc_message

        assert fdc_s1.unsigned_message == fdc_unsigned_message

        ftso = parsed_payload.ftso
        assert isinstance(ftso, ParsedPayload)
        assert ftso.protocol_id == ftso_protocol_id
        assert ftso.voting_round_id == ftso_voting_round_id
        assert ftso.size == ftso_size

        ftso_s1 = ftso.payload
        assert isinstance(ftso_s1, SubmitSignatures)
        assert ftso_s1.type == ftso_type

        ftso_signature = ftso_s1.signature
        assert isinstance(ftso_signature, Signature)
        assert ftso_signature.v == ftso_v
        assert ftso_signature.r == ftso_r
        assert ftso_signature.s == ftso_s

        ftso_message = ftso_s1.message
        assert isinstance(ftso_message, SubmitSignaturesMessage)
        assert ftso_message.protocol_id == ftso_m_protocol_id
        assert ftso_message.merkle_root == ftso_m_merkle_root
        assert ftso_message.random_quality_score == ftso_m_random_quality_score

        assert ftso_s1.unsigned_message == ftso_unsigned_message

    @pytest.mark.parametrize(
        "payload, protocol_id, random_quality_score, merkle_root, v, r, s, unsigned_message",
        [
            (
                b"\x64" + b"\x00\x00\x00\x00" + b"\x06" + b"\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c" + b"\x01" + b"\x02" * 32 + b"\x03" * 32 + b"\x00\x01",
                100, 6, "656c656c656c656c656c656c656c656c656c656c656c656c656c656c656c656c", "01", "02" * 32, "03" * 32, b"\x00\x01"
            ),
            (
                b"\x64" + b"\x00\x00\x00\x00" + b"\x06" + b"\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c\x65\x6c" + b"\x01" + b"\x02" * 32 + b"\x03" * 32,
                100, 6, "656c656c656c656c656c656c656c656c656c656c656c656c656c656c656c656c", "01", "02" * 32, "03" * 32, b""
            )
        ],
    )  # fmt: skip
    def test_submit_signatures_type_0(self, payload, protocol_id, random_quality_score, merkle_root, v, r, s, unsigned_message):  # fmt: skip
        sst0 = submit_signatures_type_0(payload)
        assert isinstance(sst0, SubmitSignatures)
        assert sst0.type == 0
        assert isinstance(sst0.signature, Signature)
        assert isinstance(sst0.message, SubmitSignaturesMessage)
        assert sst0.message.protocol_id == protocol_id
        assert sst0.message.random_quality_score == random_quality_score
        assert sst0.message.merkle_root == merkle_root
        assert sst0.signature.v == v
        assert sst0.signature.r == r
        assert sst0.signature.s == s
        assert sst0.unsigned_message == unsigned_message

    @pytest.mark.parametrize(
        "payload, v, r, s, unsigned_message",
        [
            (
                b"\x01" + b"\x02" * 32 + b"\x03" * 32 + b"\x00\x01",
                "01", "02" * 32, "03" * 32, b"\x00\x01"
            ),
            (
                b"\x01" + b"\x02" * 32 + b"\x03" * 32,
                "01", "02" * 32, "03" * 32, b""
            )
        ],
    )  # fmt: skip
    def test_submit_signatures_type_1(self, payload, v, r, s, unsigned_message):  # fmt: skip
        sst1 = submit_signatures_type_1(payload)
        assert isinstance(sst1, SubmitSignatures)
        assert sst1.type == 1
        assert isinstance(sst1.signature, Signature)
        assert sst1.message is None
        assert sst1.signature.v == v
        assert sst1.signature.r == r
        assert sst1.signature.s == s
        assert sst1.unsigned_message == unsigned_message


class TestFtsoSubmit:
    @pytest.mark.parametrize(
        "payload",
        [
            b"12345678901234567890123456789012",
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x00\x48\x65\x6c\x6c\x6f\x00\x48\x65\x6c\x6c\x6f",
        ],
    )  # fmt: skip
    def test_ftso_submit1(self, payload):
        ftso_s1 = ftso_submit1(payload)
        assert isinstance(ftso_s1, FtsoSubmit1)
        assert ftso_s1.commit_hash == payload

    @pytest.mark.parametrize(
        "payload",
        [
            b"1234567890123456789012345678901",
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x48\x65\x6c\x6c\x6f\x00\x48\x65\x6c\x6c\x6f\x00\x48\x65\x6c\x6c\x6f\x00",
        ],
    )  # fmt: skip
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
    )  # fmt: skip
    def test_ftso_submit2(self, payload, random, values):
        ftso_s2 = ftso_submit2(payload)

        assert isinstance(ftso_s2, FtsoSubmit2)
        assert ftso_s2.random == random
        assert ftso_s2.values == values

    @pytest.mark.parametrize(
        "payload",
        [b"12345678901234567890123456789012\x07[\xcd\x15\x00\x00\x00\x00\x00"],
    )  # fmt: skip
    def test_ftso_submit2_parse_error(self, payload):
        with pytest.raises(ParseError):
            ftso_submit2(payload)


class TestFdcSubmit:
    def test_fdc_submit1(self):
        with pytest.raises(ParseError):
            fdc_submit1(b"\x00")

    def test_fdc_submit1_empty_payload(self):
        fdc_s1 = fdc_submit1(b"")
        assert isinstance(fdc_s1, FdcSubmit1)

    @pytest.mark.parametrize(
        "payload, n_requests, bit_vector",
        [
            (b"\x00\x05\x0b", 5, [False, True, False, True, True]),
            (b"\x00\x09\x6c", 9, [False, False, True, True, False, True, True, False, False]),
            (b"\x00\x01\x01", 1, [True]),
            (b"\x00\x01", 1, [False]),
            (b"\x00\x10\xff\xff", 16, [True]*16),
            (b"\x00\x11\xff\xff", 17, [False] + [True]*16),
            (b"\x00\x11", 17, [False]*17),
            (b"\x00\x11\x00", 17, [False]*17),
            (b"\x00\x11\x0b\x0b", 17, [False, False, False, False, False, True, False, True, True, False, False, False, False, True, False, True, True]),
            (b"\x00\x0F\x6c\x0b", 15, [True, True, False, True, True, False, False, False, False, False, False, True, False, True, True]),
        ],
    )  # fmt: skip
    def test_fdc_submit2(self, payload, n_requests, bit_vector):
        fdc_s2 = fdc_submit2(payload)

        assert isinstance(fdc_s2, FdcSubmit2)
        assert fdc_s2.number_of_requests == n_requests
        assert fdc_s2.bit_vector == bit_vector

    @pytest.mark.parametrize(
        "payload",
        [b"\x00\x03\x0b"],
    )
    def test_fdc_submit2_parse_error(self, payload):
        with pytest.raises(ParseError):
            fdc_submit2(payload)
