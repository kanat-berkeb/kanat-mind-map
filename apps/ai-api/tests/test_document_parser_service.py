import unittest

from app.services.document_parser_service import _pdf_blocks


class PdfBlockTests(unittest.TestCase):
    def test_splits_lines_and_preserves_list_marker_as_metadata(self) -> None:
        blocks = _pdf_blocks(
            "Doküman Başlığı\n\n1. Müşteri Bilgileri\n"
            "• ABC Boya İstanbul'da faaliyet gösterir.\n"
            "- Satış hedefi 300 tondur.\n",
            page_number=2,
        )

        self.assertEqual(
            [block.text for block in blocks],
            [
                "Doküman Başlığı",
                "1. Müşteri Bilgileri",
                "ABC Boya İstanbul'da faaliyet gösterir.",
                "Satış hedefi 300 tondur.",
            ],
        )
        self.assertEqual(
            [block.atom_type for block in blocks],
            ["paragraph", "paragraph", "list_item", "list_item"],
        )
        self.assertEqual(blocks[2].metadata["listMarker"], "•")
        self.assertEqual(blocks[3].metadata["listMarker"], "-")
        self.assertTrue(all(block.page == 2 for block in blocks))
        self.assertEqual([block.block for block in blocks], [0, 1, 2, 3])


if __name__ == "__main__":
    unittest.main()
