from project import encode, decode, log

def test_encode():
    assert encode('Frank') == 'RnJhbms='
    assert encode(True) == None
    assert encode(False) == None
    assert encode([1,2,3]) == None


def test_decode():
    assert decode('RnJhbms=') == 'Frank'
    assert decode(True) == None
    assert decode(False) == None
    assert decode([1,2,3]) == None


def test_log():
    fn_name, text = "test_function", "Log message"

    assert log(fn_name, text)

    with open('log.txt', "r") as log_file:
        assert f"{text} [{fn_name}]" in log_file.read()