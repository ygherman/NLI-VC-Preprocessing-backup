from unittest import TestCase, main
from unittest.mock import Mock


class TestCollection(TestCase):
    def test___init__(self):
        test_collection = Mock()
        test_collection.assert_called_with()
        self.fail()

    def test_clean_catalog(self):
        test_collection = Mock()
        test_collection


if __name__ == "__main__":
    main()
