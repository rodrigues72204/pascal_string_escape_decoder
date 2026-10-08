import unittest

from pascal_string_escape_decoder import decode_pascal_string, PascalStringDecodeError


class TestDecodePascalString(unittest.TestCase):

    def test_plain_text_passthrough(self):
        self.assertEqual(decode_pascal_string("hello world"), "hello world")

    def test_empty_string(self):
        self.assertEqual(decode_pascal_string(""), "")

    def test_doubled_single_quotes_left_verbatim(self):
        self.assertEqual(decode_pascal_string("it''s okay"), "it''s okay")

    def test_hex_escape_basic(self):
        self.assertEqual(decode_pascal_string("#$41"), "A")

    def test_hex_escape_lowercase(self):
        self.assertEqual(decode_pascal_string("#$ff"), "ÿ")

    def test_hex_escape_uppercase(self):
        self.assertEqual(decode_pascal_string("#$FF"), "ÿ")

    def test_hex_escape_zero(self):
        self.assertEqual(decode_pascal_string("#$00"), "\x00")

    def test_decimal_code_point_basic(self):
        self.assertEqual(decode_pascal_string("#65"), "A")

    def test_decimal_code_point_euro(self):
        self.assertEqual(decode_pascal_string("#8364"), "€")

    def test_decimal_code_point_zero(self):
        self.assertEqual(decode_pascal_string("#0"), "\x00")

    def test_named_tab(self):
        self.assertEqual(decode_pascal_string("#9"), "\t")

    def test_named_newline(self):
        self.assertEqual(decode_pascal_string("#10"), "\n")

    def test_named_carriage_return(self):
        self.assertEqual(decode_pascal_string("#13"), "\r")

    def test_mixed_text_and_escapes(self):
        self.assertEqual(decode_pascal_string("line1#13#10line2"), "line1\r\nline2")

    def test_adjacent_hex_and_decimal(self):
        self.assertEqual(decode_pascal_string("#$41#66"), "AB")

    def test_hex_at_end_of_string(self):
        self.assertEqual(decode_pascal_string("end#$0A"), "end\n")

    def test_decimal_at_end_of_string(self):
        self.assertEqual(decode_pascal_string("end#65"), "endA")

    def test_bare_hash_followed_by_non_digit_is_literal(self):
        self.assertEqual(decode_pascal_string("a#b"), "a#b")

    def test_bare_hash_at_end_is_literal(self):
        self.assertEqual(decode_pascal_string("trailing#"), "trailing#")

    def test_bare_hash_dollar_no_hex_digits_is_literal_hash(self):
        self.assertEqual(decode_pascal_string("a#$z"), "a#z")

    def test_hex_escape_out_of_range_raises(self):
        with self.assertRaises(PascalStringDecodeError):
            decode_pascal_string("#$100")

    def test_decimal_code_point_out_of_range_raises(self):
        with self.assertRaises(PascalStringDecodeError):
            decode_pascal_string("#1114112")

    def test_surrogate_code_point_raises(self):
        with self.assertRaises(PascalStringDecodeError):
            decode_pascal_string("#55296")

    def test_type_error_on_non_string(self):
        with self.assertRaises(TypeError):
            decode_pascal_string(123)

    def test_exception_is_value_error_subclass(self):
        self.assertTrue(issubclass(PascalStringDecodeError, ValueError))


if __name__ == "__main__":
    unittest.main()
