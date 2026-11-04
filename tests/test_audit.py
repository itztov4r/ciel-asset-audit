import tempfile
import unittest
from pathlib import Path
from audit import audit_rows, read_inventory, render_html


def asset(**changes):
    row = dict(asset_id='PC-01', hostname='demo', ip_address='192.0.2.1', os='Linux', ram_gb='8', location='Salle')
    return row | changes


class AuditTests(unittest.TestCase):
    def test_clean_inventory(self):
        self.assertEqual(audit_rows([asset()])['findings'], [])

    def test_duplicates_and_invalid_values(self):
        report = audit_rows([asset(), asset(ram_gb='abc'), asset(asset_id='PC-02', ip_address='bad', ram_gb='4')])
        self.assertEqual(len(report['findings']), 5)

    def test_ipv6_normalization(self):
        report = audit_rows([asset(ip_address='2001:db8::1'), asset(asset_id='PC-02', ip_address='2001:0db8:0:0:0:0:0:1')])
        self.assertEqual(len(report['findings']), 1)

    def test_html_escape(self):
        result = render_html(audit_rows([asset(asset_id='<script>alert(1)</script>', ram_gb='0', os='<img>')]))
        self.assertNotIn('<script>', result)
        self.assertIn('&lt;script&gt;', result)
        self.assertIn('&lt;img&gt;', result)

    def test_missing_fields_and_custom_threshold(self):
        self.assertEqual(len(audit_rows([asset(hostname='', ram_gb='8')], 16)['findings']), 2)

    def test_missing_headers_and_malformed_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'input.csv'
            path.write_text('asset_id\nPC-01\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                read_inventory(path)
            path.write_text('asset_id,hostname,ip_address,os,ram_gb,location\nPC-01,demo,192.0.2.1,Linux,8\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                read_inventory(path)

    def test_empty_inventory(self):
        self.assertEqual(audit_rows([])['assets'], 0)


if __name__ == '__main__':
    unittest.main()
