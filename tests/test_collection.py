from unittest import TestCase, main
from unittest.mock import Mock


class TestCollection(TestCase):
    def test___init__(self):
        test_collection = Mock()
        test_collection.assert_called_with()
        self.fail()

    def test_clean_catalog(self):
        test_collection = Mock()

    def test_add_current_owner(self):
        from VC_collections.Collection import add_current_owner
        from tests.test_data import (
            df_credits_data_with_owner_test,
            df_credits_data_without_owner_test,
            df_collection_test1,
            df_collection_test2,
        )

        df_collection_test1 = add_current_owner(
            df_collection_test1, df_credits_data_without_owner_test, "ArBe"
        )
        self.assert_(
            df_collection_test1.loc[
                df_collection_test1["רמת תיאור"] == "אוסף", "בעלים נוכחי"
            ][0],
            "",
        )
        df_collection_test2 = add_current_owner(
            df_collection_test2, df_credits_data_with_owner_test, "PDoGa"
        )
        self.assert_(
            df_collection_test1.loc[
                df_collection_test1["רמת תיאור"] == "אוסף", "בעלים נוכחי"
            ][0],
            "",
        )


if __name__ == "__main__":
    main()
1
