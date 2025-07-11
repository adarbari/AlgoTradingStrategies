# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: response_account_rms_info.proto
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
    'response_account_rms_info.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fresponse_account_rms_info.proto\x12\x03rti\"\xf3\x07\n\x16ResponseAccountRmsInfo\x12\x15\n\x0btemplate_id\x18\xe3\xb6\t \x02(\x05\x12\x12\n\x08user_msg\x18\x98\x8d\x08 \x03(\t\x12\x1c\n\x12rq_handler_rp_code\x18\x9c\x8d\x08 \x03(\t\x12\x11\n\x07rp_code\x18\x9e\x8d\x08 \x03(\t\x12\x17\n\rpresence_bits\x18\x96\xb0\t \x01(\r\x12\x10\n\x06\x66\x63m_id\x18\x9d\xb3\t \x01(\t\x12\x0f\n\x05ib_id\x18\x9e\xb3\t \x01(\t\x12\x14\n\naccount_id\x18\x98\xb3\t \x01(\t\x12\x12\n\x08\x63urrency\x18\x8f\xb6\t \x01(\t\x12\x10\n\x06status\x18\x93\xb3\t \x01(\t\x12\x13\n\talgorithm\x18\xfe\x94\t \x01(\t\x12!\n\x17\x61uto_liquidate_criteria\x18\xdc\xff\x07 \x01(\t\x12G\n\x0e\x61uto_liquidate\x18\xdb\xff\x07 \x01(\x0e\x32-.rti.ResponseAccountRmsInfo.AutoLiquidateFlag\x12R\n\x19\x64isable_on_auto_liquidate\x18\xde\xff\x07 \x01(\x0e\x32-.rti.ResponseAccountRmsInfo.AutoLiquidateFlag\x12\"\n\x18\x61uto_liquidate_threshold\x18\xdd\xff\x07 \x01(\x01\x12\x30\n&auto_liquidate_max_min_account_balance\x18\xdf\xff\x07 \x01(\x01\x12\x14\n\nloss_limit\x18\xa3\xb3\t \x01(\x01\x12\x1d\n\x13min_account_balance\x18\xa8\xca\t \x01(\x01\x12\x1c\n\x12min_margin_balance\x18\xb0\xca\t \x01(\x01\x12\x1c\n\x12\x64\x65\x66\x61ult_commission\x18\x98\xae\t \x01(\x01\x12\x13\n\tbuy_limit\x18\x99\xb3\t \x01(\x05\x12\x1c\n\x12max_order_quantity\x18\x99\xdc\x06 \x01(\x05\x12\x14\n\nsell_limit\x18\xb3\xb3\t \x01(\x05\x12#\n\x19\x63heck_min_account_balance\x18\xac\xca\t \x01(\x08\"\xca\x01\n\x0cPresenceBits\x12\r\n\tBUY_LIMIT\x10\x01\x12\x0e\n\nSELL_LIMIT\x10\x02\x12\x0e\n\nLOSS_LIMIT\x10\x04\x12\x16\n\x12MAX_ORDER_QUANTITY\x10\x08\x12\x17\n\x13MIN_ACCOUNT_BALANCE\x10\x10\x12\x16\n\x12MIN_MARGIN_BALANCE\x10 \x12\r\n\tALGORITHM\x10@\x12\x0b\n\x06STATUS\x10\x80\x01\x12\r\n\x08\x43URRENCY\x10\x80\x02\x12\x17\n\x12\x44\x45\x46\x41ULT_COMMISSION\x10\x80\x04\".\n\x11\x41utoLiquidateFlag\x12\x0b\n\x07\x45NABLED\x10\x01\x12\x0c\n\x08\x44ISABLED\x10\x02')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'response_account_rms_info_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_RESPONSEACCOUNTRMSINFO']._serialized_start=41
  _globals['_RESPONSEACCOUNTRMSINFO']._serialized_end=1052
  _globals['_RESPONSEACCOUNTRMSINFO_PRESENCEBITS']._serialized_start=802
  _globals['_RESPONSEACCOUNTRMSINFO_PRESENCEBITS']._serialized_end=1004
  _globals['_RESPONSEACCOUNTRMSINFO_AUTOLIQUIDATEFLAG']._serialized_start=1006
  _globals['_RESPONSEACCOUNTRMSINFO_AUTOLIQUIDATEFLAG']._serialized_end=1052
# @@protoc_insertion_point(module_scope)
