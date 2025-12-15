import html

class StringParser:
    @staticmethod
    def normalize_html_strings(s):
        return html.unescape(s).replace('\n', '<br/>')