from accounts.hashes import hash_token


def test_hash_token_is_a_64_char_hex_digest():
    assert len(hash_token("refresh-value")) == 64
    assert hash_token("refresh-value") == hash_token("refresh-value")
