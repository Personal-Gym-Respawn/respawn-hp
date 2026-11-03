"""Regression checks for accidental publication and broken review pages. Offline."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_oauth import SOURCE, OUTPUT, FILES, check_source, build
from check_oauth import check


class PublicBoundary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name)/'site'
        shutil.copytree(SOURCE, self.site)

    def mutate(self, name, before, after):
        p = self.site/name
        p.write_text(p.read_text().replace(before, after))

    def test_valid_draft_package(self):
        check(self.site)

    def test_unfinished_homepage_cannot_enter_output(self):
        (self.site/'booking.html').write_text('<form></form>')
        with self.assertRaises(ValueError):
            check_source(self.site)

    def test_symlink_to_private_file_is_rejected(self):
        (self.site/'private').symlink_to('/private/tmp')
        with self.assertRaises(ValueError):
            check_source(self.site)

    def test_broken_privacy_link_is_rejected(self):
        self.mutate('index.html', 'href="/privacy/"', 'href="/missing/"')
        with self.assertRaisesRegex(AssertionError, 'BROKEN_LINK'):
            check(self.site)

    def test_duplicate_ids_are_rejected(self):
        self.mutate('index.html', 'id="contact-title"', 'id="intro-title"')
        with self.assertRaisesRegex(AssertionError, 'DUPLICATE_ID'):
            check(self.site)

    def test_form_is_rejected(self):
        self.mutate('index.html', '</main>', '<form></form></main>')
        with self.assertRaisesRegex(AssertionError, 'ACTIVE_OR_UNREVIEWED_CONTENT'):
            check(self.site)

    def test_credential_is_rejected(self):
        self.mutate('index.html', '</main>', 'ya29.' + 'FAKE_TEST_ONLY_TOKEN' + '</main>')
        with self.assertRaisesRegex(AssertionError, 'CREDENTIAL_OR_PRIVATE_ID'):
            check(self.site)

    def test_external_stylesheet_is_rejected(self):
        self.mutate('index.html', '/assets/site.css', 'https://example.invalid/style.css')
        with self.assertRaisesRegex(AssertionError, 'UNREVIEWED_EXTERNAL_LINK'):
            check(self.site)

    def test_root_output_is_rejected_before_writing(self):
        with self.assertRaisesRegex(ValueError, 'OUTPUT_MUST_BE_FIXED'):
            build(output=SOURCE.parent)

    def test_removed_draft_control_is_rejected(self):
        self.mutate('_headers', 'X-Robots-Tag: noindex, nofollow', '')
        with self.assertRaisesRegex(AssertionError, 'DRAFT_HEADER'):
            check(self.site)

    def test_output_matches_allowlist_and_sources(self):
        check_source(OUTPUT)
        for name in FILES:
            self.assertEqual((SOURCE/name).read_bytes(), (OUTPUT/name).read_bytes())


if __name__ == '__main__':
    unittest.main()
