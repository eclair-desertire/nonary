from django.http.multipartparser import parse_header
from django.utils.encoding import force_str
from rest_framework.parsers import FileUploadParser


class CustomFileUploadParser(FileUploadParser):

    def get_filename(self, stream, media_type, parser_context):
        """
        Detects the uploaded file name. First searches a 'filename' url kwarg.
        Then tries to parse Content-Disposition header.
        """
        try:
            return parser_context['kwargs']['filename']
        except KeyError:
            try:
                return parser_context['request'].GET.get('filename')
            except KeyError:
                pass

        try:
            meta = parser_context['request'].META
            disposition = parse_header(meta['HTTP_CONTENT_DISPOSITION'].encode())
            filename_parm = disposition[1]
            if 'filename*' in filename_parm:
                return self.get_encoded_filename(filename_parm)
            return force_str(filename_parm['filename'])
        except (AttributeError, KeyError, ValueError):
            pass
