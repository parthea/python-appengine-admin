# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule

from google import auth
from google.api_core import client_options
from google.api_core import exceptions
from google.api_core import future
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import operation_async  # type: ignore
from google.api_core import operations_v1
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.appengine_admin_v1.services.instances import InstancesAsyncClient
from google.cloud.appengine_admin_v1.services.instances import InstancesClient
from google.cloud.appengine_admin_v1.services.instances import pagers
from google.cloud.appengine_admin_v1.services.instances import transports
from google.cloud.appengine_admin_v1.types import appengine
from google.cloud.appengine_admin_v1.types import instance
from google.cloud.appengine_admin_v1.types import operation as ga_operation
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert InstancesClient._get_default_mtls_endpoint(None) is None
    assert InstancesClient._get_default_mtls_endpoint(api_endpoint) == api_mtls_endpoint
    assert (
        InstancesClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        InstancesClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        InstancesClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert InstancesClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi


@pytest.mark.parametrize("client_class", [InstancesClient, InstancesAsyncClient,])
def test_instances_client_from_service_account_info(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_info"
    ) as factory:
        factory.return_value = creds
        info = {"valid": True}
        client = client_class.from_service_account_info(info)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == "appengine.googleapis.com:443"


@pytest.mark.parametrize("client_class", [InstancesClient, InstancesAsyncClient,])
def test_instances_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == "appengine.googleapis.com:443"


def test_instances_client_get_transport_class():
    transport = InstancesClient.get_transport_class()
    available_transports = [
        transports.InstancesGrpcTransport,
    ]
    assert transport in available_transports

    transport = InstancesClient.get_transport_class("grpc")
    assert transport == transports.InstancesGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (InstancesClient, transports.InstancesGrpcTransport, "grpc"),
        (
            InstancesAsyncClient,
            transports.InstancesGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    InstancesClient, "DEFAULT_ENDPOINT", modify_default_endpoint(InstancesClient)
)
@mock.patch.object(
    InstancesAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(InstancesAsyncClient),
)
def test_instances_client_client_options(client_class, transport_class, transport_name):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(InstancesClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(InstancesClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class()

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,use_client_cert_env",
    [
        (InstancesClient, transports.InstancesGrpcTransport, "grpc", "true"),
        (
            InstancesAsyncClient,
            transports.InstancesGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (InstancesClient, transports.InstancesGrpcTransport, "grpc", "false"),
        (
            InstancesAsyncClient,
            transports.InstancesGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
    ],
)
@mock.patch.object(
    InstancesClient, "DEFAULT_ENDPOINT", modify_default_endpoint(InstancesClient)
)
@mock.patch.object(
    InstancesAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(InstancesAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_instances_client_mtls_env_auto(
    client_class, transport_class, transport_name, use_client_cert_env
):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options)

            if use_client_cert_env == "false":
                expected_client_cert_source = None
                expected_host = client.DEFAULT_ENDPOINT
            else:
                expected_client_cert_source = client_cert_source_callback
                expected_host = client.DEFAULT_MTLS_ENDPOINT

            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=expected_host,
                scopes=None,
                client_cert_source_for_mtls=expected_client_cert_source,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case ADC client cert is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=True,
            ):
                with mock.patch(
                    "google.auth.transport.mtls.default_client_cert_source",
                    return_value=client_cert_source_callback,
                ):
                    if use_client_cert_env == "false":
                        expected_host = client.DEFAULT_ENDPOINT
                        expected_client_cert_source = None
                    else:
                        expected_host = client.DEFAULT_MTLS_ENDPOINT
                        expected_client_cert_source = client_cert_source_callback

                    patched.return_value = None
                    client = client_class()
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=expected_host,
                        scopes=None,
                        client_cert_source_for_mtls=expected_client_cert_source,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                    )

    # Check the case client_cert_source and ADC client cert are not provided.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=False,
            ):
                patched.return_value = None
                client = client_class()
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_ENDPOINT,
                    scopes=None,
                    client_cert_source_for_mtls=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (InstancesClient, transports.InstancesGrpcTransport, "grpc"),
        (
            InstancesAsyncClient,
            transports.InstancesGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_instances_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (InstancesClient, transports.InstancesGrpcTransport, "grpc"),
        (
            InstancesAsyncClient,
            transports.InstancesGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_instances_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_instances_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.appengine_admin_v1.services.instances.transports.InstancesGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = InstancesClient(client_options={"api_endpoint": "squid.clam.whelk"})
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_list_instances(
    transport: str = "grpc", request_type=appengine.ListInstancesRequest
):
    client = InstancesClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_instances), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = appengine.ListInstancesResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_instances(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == appengine.ListInstancesRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, pagers.ListInstancesPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_instances_from_dict():
    test_list_instances(request_type=dict)


def test_list_instances_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = InstancesClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_instances), "__call__") as call:
        client.list_instances()
        call.assert_called()
        _, args, _ = call.mock_calls[0]

        assert args[0] == appengine.ListInstancesRequest()


@pytest.mark.asyncio
async def test_list_instances_async(
    transport: str = "grpc_asyncio", request_type=appengine.ListInstancesRequest
):
    client = InstancesAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_instances), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            appengine.ListInstancesResponse(next_page_token="next_page_token_value",)
        )

        response = await client.list_instances(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == appengine.ListInstancesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListInstancesAsyncPager)

    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_instances_async_from_dict():
    await test_list_instances_async(request_type=dict)


def test_list_instances_field_headers():
    client = InstancesClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = appengine.ListInstancesRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_instances), "__call__") as call:
        call.return_value = appengine.ListInstancesResponse()

        client.list_instances(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_instances_field_headers_async():
    client = InstancesAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = appengine.ListInstancesRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_instances), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            appengine.ListInstancesResponse()
        )

        await client.list_instances(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_instances_pager():
    client = InstancesClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_instances), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            appengine.ListInstancesResponse(
                instances=[
                    instance.Instance(),
                    instance.Instance(),
                    instance.Instance(),
                ],
                next_page_token="abc",
            ),
            appengine.ListInstancesResponse(instances=[], next_page_token="def",),
            appengine.ListInstancesResponse(
                instances=[instance.Instance(),], next_page_token="ghi",
            ),
            appengine.ListInstancesResponse(
                instances=[instance.Instance(), instance.Instance(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_instances(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, instance.Instance) for i in results)


def test_list_instances_pages():
    client = InstancesClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_instances), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            appengine.ListInstancesResponse(
                instances=[
                    instance.Instance(),
                    instance.Instance(),
                    instance.Instance(),
                ],
                next_page_token="abc",
            ),
            appengine.ListInstancesResponse(instances=[], next_page_token="def",),
            appengine.ListInstancesResponse(
                instances=[instance.Instance(),], next_page_token="ghi",
            ),
            appengine.ListInstancesResponse(
                instances=[instance.Instance(), instance.Instance(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_instances(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_instances_async_pager():
    client = InstancesAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_instances), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            appengine.ListInstancesResponse(
                instances=[
                    instance.Instance(),
                    instance.Instance(),
                    instance.Instance(),
                ],
                next_page_token="abc",
            ),
            appengine.ListInstancesResponse(instances=[], next_page_token="def",),
            appengine.ListInstancesResponse(
                instances=[instance.Instance(),], next_page_token="ghi",
            ),
            appengine.ListInstancesResponse(
                instances=[instance.Instance(), instance.Instance(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_instances(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, instance.Instance) for i in responses)


@pytest.mark.asyncio
async def test_list_instances_async_pages():
    client = InstancesAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_instances), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            appengine.ListInstancesResponse(
                instances=[
                    instance.Instance(),
                    instance.Instance(),
                    instance.Instance(),
                ],
                next_page_token="abc",
            ),
            appengine.ListInstancesResponse(instances=[], next_page_token="def",),
            appengine.ListInstancesResponse(
                instances=[instance.Instance(),], next_page_token="ghi",
            ),
            appengine.ListInstancesResponse(
                instances=[instance.Instance(), instance.Instance(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_instances(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_get_instance(
    transport: str = "grpc", request_type=appengine.GetInstanceRequest
):
    client = InstancesClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_instance), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = instance.Instance(
            name="name_value",
            id="id_value",
            app_engine_release="app_engine_release_value",
            availability=instance.Instance.Availability.RESIDENT,
            vm_name="vm_name_value",
            vm_zone_name="vm_zone_name_value",
            vm_id="vm_id_value",
            requests=892,
            errors=669,
            qps=0.340,
            average_latency=1578,
            memory_usage=1293,
            vm_status="vm_status_value",
            vm_debug_enabled=True,
            vm_ip="vm_ip_value",
            vm_liveness=instance.Instance.Liveness.LivenessState.UNKNOWN,
        )

        response = client.get_instance(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == appengine.GetInstanceRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, instance.Instance)

    assert response.name == "name_value"

    assert response.id == "id_value"

    assert response.app_engine_release == "app_engine_release_value"

    assert response.availability == instance.Instance.Availability.RESIDENT

    assert response.vm_name == "vm_name_value"

    assert response.vm_zone_name == "vm_zone_name_value"

    assert response.vm_id == "vm_id_value"

    assert response.requests == 892

    assert response.errors == 669

    assert math.isclose(response.qps, 0.340, rel_tol=1e-6)

    assert response.average_latency == 1578

    assert response.memory_usage == 1293

    assert response.vm_status == "vm_status_value"

    assert response.vm_debug_enabled is True

    assert response.vm_ip == "vm_ip_value"

    assert response.vm_liveness == instance.Instance.Liveness.LivenessState.UNKNOWN


def test_get_instance_from_dict():
    test_get_instance(request_type=dict)


def test_get_instance_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = InstancesClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_instance), "__call__") as call:
        client.get_instance()
        call.assert_called()
        _, args, _ = call.mock_calls[0]

        assert args[0] == appengine.GetInstanceRequest()


@pytest.mark.asyncio
async def test_get_instance_async(
    transport: str = "grpc_asyncio", request_type=appengine.GetInstanceRequest
):
    client = InstancesAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_instance), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            instance.Instance(
                name="name_value",
                id="id_value",
                app_engine_release="app_engine_release_value",
                availability=instance.Instance.Availability.RESIDENT,
                vm_name="vm_name_value",
                vm_zone_name="vm_zone_name_value",
                vm_id="vm_id_value",
                requests=892,
                errors=669,
                qps=0.340,
                average_latency=1578,
                memory_usage=1293,
                vm_status="vm_status_value",
                vm_debug_enabled=True,
                vm_ip="vm_ip_value",
                vm_liveness=instance.Instance.Liveness.LivenessState.UNKNOWN,
            )
        )

        response = await client.get_instance(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == appengine.GetInstanceRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, instance.Instance)

    assert response.name == "name_value"

    assert response.id == "id_value"

    assert response.app_engine_release == "app_engine_release_value"

    assert response.availability == instance.Instance.Availability.RESIDENT

    assert response.vm_name == "vm_name_value"

    assert response.vm_zone_name == "vm_zone_name_value"

    assert response.vm_id == "vm_id_value"

    assert response.requests == 892

    assert response.errors == 669

    assert math.isclose(response.qps, 0.340, rel_tol=1e-6)

    assert response.average_latency == 1578

    assert response.memory_usage == 1293

    assert response.vm_status == "vm_status_value"

    assert response.vm_debug_enabled is True

    assert response.vm_ip == "vm_ip_value"

    assert response.vm_liveness == instance.Instance.Liveness.LivenessState.UNKNOWN


@pytest.mark.asyncio
async def test_get_instance_async_from_dict():
    await test_get_instance_async(request_type=dict)


def test_get_instance_field_headers():
    client = InstancesClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = appengine.GetInstanceRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_instance), "__call__") as call:
        call.return_value = instance.Instance()

        client.get_instance(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_instance_field_headers_async():
    client = InstancesAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = appengine.GetInstanceRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_instance), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(instance.Instance())

        await client.get_instance(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_instance(
    transport: str = "grpc", request_type=appengine.DeleteInstanceRequest
):
    client = InstancesClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_instance), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.delete_instance(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == appengine.DeleteInstanceRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_instance_from_dict():
    test_delete_instance(request_type=dict)


def test_delete_instance_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = InstancesClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_instance), "__call__") as call:
        client.delete_instance()
        call.assert_called()
        _, args, _ = call.mock_calls[0]

        assert args[0] == appengine.DeleteInstanceRequest()


@pytest.mark.asyncio
async def test_delete_instance_async(
    transport: str = "grpc_asyncio", request_type=appengine.DeleteInstanceRequest
):
    client = InstancesAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_instance), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.delete_instance(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == appengine.DeleteInstanceRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_instance_async_from_dict():
    await test_delete_instance_async(request_type=dict)


def test_delete_instance_field_headers():
    client = InstancesClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = appengine.DeleteInstanceRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_instance), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.delete_instance(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_instance_field_headers_async():
    client = InstancesAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = appengine.DeleteInstanceRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_instance), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.delete_instance(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_debug_instance(
    transport: str = "grpc", request_type=appengine.DebugInstanceRequest
):
    client = InstancesClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.debug_instance), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.debug_instance(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == appengine.DebugInstanceRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_debug_instance_from_dict():
    test_debug_instance(request_type=dict)


def test_debug_instance_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = InstancesClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.debug_instance), "__call__") as call:
        client.debug_instance()
        call.assert_called()
        _, args, _ = call.mock_calls[0]

        assert args[0] == appengine.DebugInstanceRequest()


@pytest.mark.asyncio
async def test_debug_instance_async(
    transport: str = "grpc_asyncio", request_type=appengine.DebugInstanceRequest
):
    client = InstancesAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.debug_instance), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )

        response = await client.debug_instance(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == appengine.DebugInstanceRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_debug_instance_async_from_dict():
    await test_debug_instance_async(request_type=dict)


def test_debug_instance_field_headers():
    client = InstancesClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = appengine.DebugInstanceRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.debug_instance), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")

        client.debug_instance(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_debug_instance_field_headers_async():
    client = InstancesAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = appengine.DebugInstanceRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.debug_instance), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )

        await client.debug_instance(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.InstancesGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = InstancesClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.InstancesGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = InstancesClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.InstancesGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = InstancesClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.InstancesGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = InstancesClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.InstancesGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.InstancesGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [transports.InstancesGrpcTransport, transports.InstancesGrpcAsyncIOTransport,],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = InstancesClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client.transport, transports.InstancesGrpcTransport,)


def test_instances_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.InstancesTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_instances_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.appengine_admin_v1.services.instances.transports.InstancesTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.InstancesTransport(
            credentials=credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "list_instances",
        "get_instance",
        "delete_instance",
        "debug_instance",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_instances_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        auth, "load_credentials_from_file"
    ) as load_creds, mock.patch(
        "google.cloud.appengine_admin_v1.services.instances.transports.InstancesTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.InstancesTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=(
                "https://www.googleapis.com/auth/appengine.admin",
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-platform.read-only",
            ),
            quota_project_id="octopus",
        )


def test_instances_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(auth, "default") as adc, mock.patch(
        "google.cloud.appengine_admin_v1.services.instances.transports.InstancesTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.InstancesTransport()
        adc.assert_called_once()


def test_instances_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        InstancesClient()
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/appengine.admin",
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-platform.read-only",
            ),
            quota_project_id=None,
        )


def test_instances_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.InstancesGrpcTransport(
            host="squid.clam.whelk", quota_project_id="octopus"
        )
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/appengine.admin",
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-platform.read-only",
            ),
            quota_project_id="octopus",
        )


@pytest.mark.parametrize(
    "transport_class",
    [transports.InstancesGrpcTransport, transports.InstancesGrpcAsyncIOTransport],
)
def test_instances_grpc_transport_client_cert_source_for_mtls(transport_class):
    cred = credentials.AnonymousCredentials()

    # Check ssl_channel_credentials is used if provided.
    with mock.patch.object(transport_class, "create_channel") as mock_create_channel:
        mock_ssl_channel_creds = mock.Mock()
        transport_class(
            host="squid.clam.whelk",
            credentials=cred,
            ssl_channel_credentials=mock_ssl_channel_creds,
        )
        mock_create_channel.assert_called_once_with(
            "squid.clam.whelk:443",
            credentials=cred,
            credentials_file=None,
            scopes=(
                "https://www.googleapis.com/auth/appengine.admin",
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-platform.read-only",
            ),
            ssl_credentials=mock_ssl_channel_creds,
            quota_project_id=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )

    # Check if ssl_channel_credentials is not provided, then client_cert_source_for_mtls
    # is used.
    with mock.patch.object(transport_class, "create_channel", return_value=mock.Mock()):
        with mock.patch("grpc.ssl_channel_credentials") as mock_ssl_cred:
            transport_class(
                credentials=cred,
                client_cert_source_for_mtls=client_cert_source_callback,
            )
            expected_cert, expected_key = client_cert_source_callback()
            mock_ssl_cred.assert_called_once_with(
                certificate_chain=expected_cert, private_key=expected_key
            )


def test_instances_host_no_port():
    client = InstancesClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="appengine.googleapis.com"
        ),
    )
    assert client.transport._host == "appengine.googleapis.com:443"


def test_instances_host_with_port():
    client = InstancesClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="appengine.googleapis.com:8000"
        ),
    )
    assert client.transport._host == "appengine.googleapis.com:8000"


def test_instances_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.InstancesGrpcTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_instances_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.InstancesGrpcAsyncIOTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize(
    "transport_class",
    [transports.InstancesGrpcTransport, transports.InstancesGrpcAsyncIOTransport],
)
def test_instances_transport_channel_mtls_with_client_cert_source(transport_class):
    with mock.patch(
        "grpc.ssl_channel_credentials", autospec=True
    ) as grpc_ssl_channel_cred:
        with mock.patch.object(
            transport_class, "create_channel"
        ) as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = credentials.AnonymousCredentials()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(auth, "default") as adc:
                    adc.return_value = (cred, None)
                    transport = transport_class(
                        host="squid.clam.whelk",
                        api_mtls_endpoint="mtls.squid.clam.whelk",
                        client_cert_source=client_cert_source_callback,
                    )
                    adc.assert_called_once()

            grpc_ssl_channel_cred.assert_called_once_with(
                certificate_chain=b"cert bytes", private_key=b"key bytes"
            )
            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=cred,
                credentials_file=None,
                scopes=(
                    "https://www.googleapis.com/auth/appengine.admin",
                    "https://www.googleapis.com/auth/cloud-platform",
                    "https://www.googleapis.com/auth/cloud-platform.read-only",
                ),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel
            assert transport._ssl_channel_credentials == mock_ssl_cred


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize(
    "transport_class",
    [transports.InstancesGrpcTransport, transports.InstancesGrpcAsyncIOTransport],
)
def test_instances_transport_channel_mtls_with_adc(transport_class):
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        with mock.patch.object(
            transport_class, "create_channel"
        ) as grpc_create_channel:
            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel
            mock_cred = mock.Mock()

            with pytest.warns(DeprecationWarning):
                transport = transport_class(
                    host="squid.clam.whelk",
                    credentials=mock_cred,
                    api_mtls_endpoint="mtls.squid.clam.whelk",
                    client_cert_source=None,
                )

            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=mock_cred,
                credentials_file=None,
                scopes=(
                    "https://www.googleapis.com/auth/appengine.admin",
                    "https://www.googleapis.com/auth/cloud-platform",
                    "https://www.googleapis.com/auth/cloud-platform.read-only",
                ),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_instances_grpc_lro_client():
    client = InstancesClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_instances_grpc_lro_async_client():
    client = InstancesAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc_asyncio",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsAsyncClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_instance_path():
    app = "squid"
    service = "clam"
    version = "whelk"
    instance = "octopus"

    expected = "apps/{app}/services/{service}/versions/{version}/instances/{instance}".format(
        app=app, service=service, version=version, instance=instance,
    )
    actual = InstancesClient.instance_path(app, service, version, instance)
    assert expected == actual


def test_parse_instance_path():
    expected = {
        "app": "oyster",
        "service": "nudibranch",
        "version": "cuttlefish",
        "instance": "mussel",
    }
    path = InstancesClient.instance_path(**expected)

    # Check that the path construction is reversible.
    actual = InstancesClient.parse_instance_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "winkle"

    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = InstancesClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "nautilus",
    }
    path = InstancesClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = InstancesClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "scallop"

    expected = "folders/{folder}".format(folder=folder,)
    actual = InstancesClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "abalone",
    }
    path = InstancesClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = InstancesClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "squid"

    expected = "organizations/{organization}".format(organization=organization,)
    actual = InstancesClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "clam",
    }
    path = InstancesClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = InstancesClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "whelk"

    expected = "projects/{project}".format(project=project,)
    actual = InstancesClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "octopus",
    }
    path = InstancesClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = InstancesClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "oyster"
    location = "nudibranch"

    expected = "projects/{project}/locations/{location}".format(
        project=project, location=location,
    )
    actual = InstancesClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "cuttlefish",
        "location": "mussel",
    }
    path = InstancesClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = InstancesClient.parse_common_location_path(path)
    assert expected == actual


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.InstancesTransport, "_prep_wrapped_messages"
    ) as prep:
        client = InstancesClient(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.InstancesTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = InstancesClient.get_transport_class()
        transport = transport_class(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)
