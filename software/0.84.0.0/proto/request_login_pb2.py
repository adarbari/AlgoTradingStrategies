# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: request_login.proto
# Protobuf Python Version: 6.31.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    0,
    '',
    'request_login.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13request_login.proto\x12\x03rti\"\xba\x03\n\x0cRequestLogin\x12\x15\n\x0btemplate_id\x18\xe3\xb6\t \x02(\x05\x12\x1a\n\x10template_version\x18\xa2\xb0\t \x01(\t\x12\x12\n\x08user_msg\x18\x98\x8d\x08 \x03(\t\x12\x0e\n\x04user\x18\xbb\xff\x07 \x01(\t\x12\x12\n\x08password\x18\xd4\xf7\x07 \x01(\t\x12\x12\n\x08\x61pp_name\x18\xd2\xf7\x07 \x01(\t\x12\x15\n\x0b\x61pp_version\x18\xdb\x85\x08 \x01(\t\x12\x15\n\x0bsystem_name\x18\x9c\xb0\t \x01(\t\x12\x34\n\ninfra_type\x18\x95\xb0\t \x01(\x0e\x32\x1e.rti.RequestLogin.SysInfraType\x12\x12\n\x08mac_addr\x18\xec\xe5\x08 \x03(\t\x12\x14\n\nos_version\x18\x95\xe5\x08 \x01(\t\x12\x15\n\x0bos_platform\x18\x94\xe5\x08 \x01(\t\x12\x1b\n\x11\x61ggregated_quotes\x18\xac\xb0\t \x01(\x08\"i\n\x0cSysInfraType\x12\x10\n\x0cTICKER_PLANT\x10\x01\x12\x0f\n\x0bORDER_PLANT\x10\x02\x12\x11\n\rHISTORY_PLANT\x10\x03\x12\r\n\tPNL_PLANT\x10\x04\x12\x14\n\x10REPOSITORY_PLANT\x10\x05')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'request_login_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_REQUESTLOGIN']._serialized_start=29
  _globals['_REQUESTLOGIN']._serialized_end=471
  _globals['_REQUESTLOGIN_SYSINFRATYPE']._serialized_start=366
  _globals['_REQUESTLOGIN_SYSINFRATYPE']._serialized_end=471
# @@protoc_insertion_point(module_scope)
