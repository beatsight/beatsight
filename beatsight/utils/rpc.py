import logging

from django.conf import settings
import grpc

import license_pb2
import license_pb2_grpc


logger = logging.getLogger(settings.LOGNAME)

def get_license():
    with grpc.insecure_channel(settings.CORE_SERVICE) as channel:
        # Create a stub (client)
        stub = license_pb2_grpc.LicenseServiceStub(channel)

        # # Create a valid request
        request = license_pb2.Empty()

        # Call the GetLicenseData method
        try:
            response = stub.GetLicenseData(request)
            res = {
                'user': response.user,
                'max_projects': response.max_projects,
                'expiration_date': response.expiration_date,
                'license_version': response.license_version,
            }
            return res
        except grpc.RpcError as e:
            logger.error(f"gRPC Error: {e}")
            return None
