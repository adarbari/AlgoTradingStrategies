# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: response_get_instrument_by_underlying.proto
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
    'response_get_instrument_by_underlying.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n+response_get_instrument_by_underlying.proto\x12\x03rti\"\xe6\x07\n!ResponseGetInstrumentByUnderlying\x12\x15\n\x0btemplate_id\x18\xe3\xb6\t \x02(\x05\x12\x12\n\x08user_msg\x18\x98\x8d\x08 \x03(\t\x12\x1c\n\x12rq_handler_rp_code\x18\x9c\x8d\x08 \x03(\t\x12\x11\n\x07rp_code\x18\x9e\x8d\x08 \x03(\t\x12\x17\n\rpresence_bits\x18\x92\x8d\t \x01(\r\x12\x14\n\nclear_bits\x18\xcb\xb7\t \x01(\r\x12\x10\n\x06symbol\x18\x94\xdc\x06 \x01(\t\x12\x12\n\x08\x65xchange\x18\x95\xdc\x06 \x01(\t\x12\x19\n\x0f\x65xchange_symbol\x18\xa2\xdc\x06 \x01(\t\x12\x15\n\x0bsymbol_name\x18\xa3\x8d\x06 \x01(\t\x12\x16\n\x0cproduct_code\x18\x8d\x93\x06 \x01(\t\x12\x19\n\x0finstrument_type\x18\xa4\xdc\x06 \x01(\t\x12\x1b\n\x11underlying_symbol\x18\xa2\x95\x06 \x01(\t\x12\x19\n\x0f\x65xpiration_date\x18\xe3\x8d\x06 \x01(\t\x12\x12\n\x08\x63urrency\x18\x8e\xb6\t \x01(\t\x12\x1c\n\x12put_call_indicator\x18\x8d\x8e\x06 \x01(\t\x12\x18\n\x0etick_size_type\x18\xb7\xb4\t \x01(\t\x12\x1e\n\x14price_display_format\x18\x96\xb6\t \x01(\t\x12\x16\n\x0cstrike_price\x18\xe2\x8d\x06 \x01(\x01\x12\x14\n\nftoq_price\x18\x90\xb6\t \x01(\x01\x12\x14\n\nqtof_price\x18\x91\xb6\t \x01(\x01\x12\x1b\n\x11min_qprice_change\x18\x92\xb6\t \x01(\x01\x12\x1b\n\x11min_fprice_change\x18\x93\xb6\t \x01(\x01\x12\x1c\n\x12single_point_value\x18\x95\xb6\t \x01(\x01\"\xea\x02\n\x0cPresenceBits\x12\x13\n\x0f\x45XCHANGE_SYMBOL\x10\x01\x12\x0f\n\x0bSYMBOL_NAME\x10\x02\x12\x10\n\x0cPRODUCT_CODE\x10\x04\x12\x13\n\x0fINSTRUMENT_TYPE\x10\x08\x12\x15\n\x11UNDERLYING_SYMBOL\x10\x10\x12\x13\n\x0f\x45XPIRATION_DATE\x10 \x12\x0c\n\x08\x43URRENCY\x10@\x12\x17\n\x12PUT_CALL_INDICATOR\x10\x80\x01\x12\x11\n\x0cSTRIKE_PRICE\x10\x80\x02\x12\x15\n\x10\x46PRICE_TO_QPRICE\x10\x80\x04\x12\x15\n\x10QPRICE_TO_FPRICE\x10\x80\x08\x12\x16\n\x11MIN_QPRICE_CHANGE\x10\x80\x10\x12\x16\n\x11MIN_FRPICE_CHANGE\x10\x80 \x12\x17\n\x12SINGLE_POINT_VALUE\x10\x80@\x12\x14\n\x0eTICK_SIZE_TYPE\x10\x80\x80\x01\x12\x1a\n\x14PRICE_DISPLAY_FORMAT\x10\x80\x80\x02')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'response_get_instrument_by_underlying_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_RESPONSEGETINSTRUMENTBYUNDERLYING']._serialized_start=53
  _globals['_RESPONSEGETINSTRUMENTBYUNDERLYING']._serialized_end=1051
  _globals['_RESPONSEGETINSTRUMENTBYUNDERLYING_PRESENCEBITS']._serialized_start=689
  _globals['_RESPONSEGETINSTRUMENTBYUNDERLYING_PRESENCEBITS']._serialized_end=1051
# @@protoc_insertion_point(module_scope)
