# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: depth_by_order.proto
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
    'depth_by_order.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14\x64\x65pth_by_order.proto\x12\x03rti\"\xea\x04\n\x0c\x44\x65pthByOrder\x12\x15\n\x0btemplate_id\x18\xe3\xb6\t \x02(\x05\x12\x10\n\x06symbol\x18\x94\xdc\x06 \x01(\t\x12\x12\n\x08\x65xchange\x18\x95\xdc\x06 \x01(\t\x12\x19\n\x0fsequence_number\x18\x82\xeb\x06 \x01(\x04\x12\x33\n\x0bupdate_type\x18\xa9\xdc\x06 \x03(\x0e\x32\x1c.rti.DepthByOrder.UpdateType\x12=\n\x10transaction_type\x18\x8c\xb0\t \x03(\x0e\x32!.rti.DepthByOrder.TransactionType\x12\x15\n\x0b\x64\x65pth_price\x18\xa5\xb6\t \x03(\x01\x12\x1a\n\x10prev_depth_price\x18\x9a\xba\t \x03(\x01\x12\x1f\n\x15prev_depth_price_flag\x18\xb2\xba\t \x03(\x08\x12\x14\n\ndepth_size\x18\xa6\xb6\t \x03(\x05\x12\x1e\n\x14\x64\x65pth_order_priority\x18\x8d\xb0\t \x03(\x04\x12\x1b\n\x11\x65xchange_order_id\x18\xf6\x8d\t \x03(\t\x12\x0f\n\x05ssboe\x18\xd4\x94\t \x01(\x05\x12\x0f\n\x05usecs\x18\xd5\x94\t \x01(\x05\x12\x16\n\x0csource_ssboe\x18\x80\x97\t \x01(\x05\x12\x16\n\x0csource_usecs\x18\x81\x97\t \x01(\x05\x12\x16\n\x0csource_nsecs\x18\x84\x97\t \x01(\x05\x12\x13\n\tjop_ssboe\x18\xc8\x98\t \x01(\x05\x12\x13\n\tjop_nsecs\x18\xcc\x98\t \x01(\x05\"$\n\x0fTransactionType\x12\x07\n\x03\x42UY\x10\x01\x12\x08\n\x04SELL\x10\x02\"-\n\nUpdateType\x12\x07\n\x03NEW\x10\x01\x12\n\n\x06\x43HANGE\x10\x02\x12\n\n\x06\x44\x45LETE\x10\x03')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'depth_by_order_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_DEPTHBYORDER']._serialized_start=30
  _globals['_DEPTHBYORDER']._serialized_end=648
  _globals['_DEPTHBYORDER_TRANSACTIONTYPE']._serialized_start=565
  _globals['_DEPTHBYORDER_TRANSACTIONTYPE']._serialized_end=601
  _globals['_DEPTHBYORDER_UPDATETYPE']._serialized_start=603
  _globals['_DEPTHBYORDER_UPDATETYPE']._serialized_end=648
# @@protoc_insertion_point(module_scope)
