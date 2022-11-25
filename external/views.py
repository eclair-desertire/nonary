import json
import os
import zipfile

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from external.services.commerce_ml_export import get_export_order_xml
from external.services.commerce_ml_import import get_or_create_import_status, fetch_storehouse_from_xml, \
    fetch_categories_from_xml, fetch_goods_from_xml, fetch_prices_from_xml, fetch_rests_from_xml, \
    fetch_documents_from_xml
from utils.custom_logging import save_info
from utils.parsers import CustomFileUploadParser
from xml.etree import ElementTree


class WebHookCommerceMLView(APIView):
    permission_classes = (AllowAny, )
    parser_classes = (CustomFileUploadParser, )

    def get(self, request):
        mode = request.query_params.get('mode')
        request_type = request.query_params.get('type')
        save_info(json.dumps(request.query_params.dict()))
        response_text = f'success\nRequestType\n{request_type}'
        if request_type == 'sale':
            if mode == 'init':
                response_text = f'zip=yes\nfile_limit={settings.DATA_UPLOAD_MAX_MEMORY_SIZE}'
            elif mode == 'success':
                response_text = f'success\nRequestType\n{request_type}'
            elif mode == 'query':
                xml = get_export_order_xml()
                response = HttpResponse(xml.encode())
                response['Content-Disposition'] = 'attachment; filename=offers.xml'
                return response
            elif mode == 'info':
                xml = render_to_string('commerceml.xml', {})
                response = HttpResponse(xml.encode())
                response['Content-Disposition'] = 'attachment; filename=commerceml.xml'
                return response
            elif mode == 'import':
                filename = request.query_params.get("filename")
                file_path = f'./{filename}'
                if 'documents' in filename:
                    fetch_documents_from_xml(file_path, filename=filename)
        else:
            if mode == 'init':
                response_text = f'zip=yes\nfile_limit={settings.DATA_UPLOAD_MAX_MEMORY_SIZE}'
            elif mode == 'import':
                filename = request.query_params.get("filename")
                file_path = f'./{filename}'
                if os.path.exists(file_path):
                    if 'offers' in filename:
                        response_text = 'success'
                        # os.remove(file_path)
                    elif 'promo' in filename:
                        response_text = 'success'
                        # os.remove(file_path)
                    else:
                        import_status, created = get_or_create_import_status(filename)
                        response_text = 'progress'
                        if created:
                            if 'sklady' in filename:
                                fetch_storehouse_from_xml.after_response(file_path, filename=filename)
                            if 'soglasheniya' in filename:
                                fetch_categories_from_xml.after_response(file_path, filename=filename)
                            if 'goods' in filename:
                                fetch_goods_from_xml.after_response(file_path, filename=filename)
                            if 'prices' in filename:
                                fetch_prices_from_xml.after_response(file_path, filename=filename)
                            if 'rests' in filename:
                                fetch_rests_from_xml.after_response(file_path, filename=filename)
                            if 'documents' in filename:
                                fetch_documents_from_xml(file_path, filename=filename)
                else:
                    response_text = f'success'
        response = HttpResponse(response_text)
        return response

    def post(self, request):
        file_path = "./"
        client_file = request.FILES['file']
        # first dump the zip file to a directory
        with open(file_path + '%s' % client_file.name, 'wb+') as dest:
            for chunk in client_file.chunks():
                dest.write(chunk)

        # unzip the zip file to the same directory
        with zipfile.ZipFile(file_path + client_file.name, 'r') as zip_ref:
            zip_ref.extractall(file_path)

        # os.remove(file_path + client_file.name)
        return HttpResponse('success')


class ExportOrdersView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        xml = get_export_order_xml()
        return HttpResponse(xml, content_type='application/xml')
