# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: time_bar.proto
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
    'time_bar.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0etime_bar.proto\x12\x03rti\"\xe9\x03\n\x07TimeBar\x12\x15\n\x0btemplate_id\x18\xe3\xb6\t \x02(\x05\x12\x10\n\x06symbol\x18\x94\xdc\x06 \x01(\t\x12\x12\n\x08\x65xchange\x18\x95\xdc\x06 \x01(\t\x12$\n\x04type\x18\xa0\xa3\x07 \x01(\x0e\x32\x14.rti.TimeBar.BarType\x12\x10\n\x06period\x18\xc8\xa2\x07 \x01(\t\x12\x10\n\x06marker\x18\xbc\xa2\x07 \x01(\x05\x12\x14\n\nnum_trades\x18\xc5\xa2\x07 \x01(\x04\x12\x10\n\x06volume\x18\xc6\xa2\x07 \x01(\x04\x12\x14\n\nbid_volume\x18\xcd\xa2\x07 \x01(\x04\x12\x14\n\nask_volume\x18\xce\xa2\x07 \x01(\x04\x12\x14\n\nopen_price\x18\xb3\x8d\x06 \x01(\x01\x12\x15\n\x0b\x63lose_price\x18\xb5\x8d\x06 \x01(\x01\x12\x14\n\nhigh_price\x18\xac\x8d\x06 \x01(\x01\x12\x13\n\tlow_price\x18\xad\x8d\x06 \x01(\x01\x12\x1a\n\x10settlement_price\x18\xe6\x8d\x06 \x01(\x01\x12\x1e\n\x14has_settlement_price\x18\x92\x8d\t \x01(\x08\x12%\n\x1bmust_clear_settlement_price\x18\xcb\xb7\t \x01(\x08\"H\n\x07\x42\x61rType\x12\x0e\n\nSECOND_BAR\x10\x01\x12\x0e\n\nMINUTE_BAR\x10\x02\x12\r\n\tDAILY_BAR\x10\x03\x12\x0e\n\nWEEKLY_BAR\x10\x04')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'time_bar_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_TIMEBAR']._serialized_start=24
  _globals['_TIMEBAR']._serialized_end=513
  _globals['_TIMEBAR_BARTYPE']._serialized_start=441
  _globals['_TIMEBAR_BARTYPE']._serialized_end=513
# @@protoc_insertion_point(module_scope)
