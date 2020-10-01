from unittest import TestCase


class Test(TestCase):
    def test_find_newest_file_in_list(self):
        from VC_collections.files import find_newest_file_in_list

        test_list = [
            "PRiSc_Final_to_Alma_20200716",
            "PRiSc_Final_to_Alma_20200710",
            "PRiSc_Final_to_Alma_20200720",
        ]

        self.assertTrue(
            "PRiSc_Final_to_Alma_20200720"
            == find_newest_file_in_list(
                files_list=test_list, file_name_pattern="_final_to_alma", mode="mid"
            )
        )
