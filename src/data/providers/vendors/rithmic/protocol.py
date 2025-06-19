"""Protocol handler for Rithmic API communication using Protobuf messages."""

import asyncio
import logging
import os
import ssl
import websockets
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime

from google.protobuf.message import Message

from src.data.types.base_types import TimeSeriesData, OrderBookLevel, OrderBookSnapshot, Trade, TradeFlags
from src.data.types.data_config_types import OrderFlowConfig
from .proto import (
    RequestLogin,
    ResponseLogin,
    RequestMarketDataUpdate,
    ResponseMarketDataUpdate,
    LastTrade,
    BestBidOffer
)

logger = logging.getLogger(__name__)

class RithmicProtocol:
    """Protocol handler for Rithmic API."""
    
    def __init__(
        self,
        hostname: str,
        user_id: str,
        password: str,
        system_name: str = "Rithmic Test",
        ssl_context: Optional[ssl.SSLContext] = None
    ):
        """Initialize the Rithmic protocol handler.
        
        Args:
            hostname: Rithmic server hostname (e.g., 'rituz00100.rithmic.com:443')
            user_id: Rithmic user ID
            password: Rithmic password
            system_name: Rithmic system name (default: "Rithmic Test")
            ssl_context: Optional SSL context for secure connections
        """
        self._hostname = hostname
        self._user_id = user_id
        self._password = password
        self._system_name = system_name
        self._ssl_context = ssl_context
        self._ws = None
        self._response_handlers = {
            207: self._handle_tick_bar_replay_response,  # Historical tick bar response
            251: self._handle_tick_bar_response,  # Historical tick response
        }
        self._subscriptions = set()
        self._order_book = {}
        self._trades = {}
        
    async def connect(self) -> None:
        """Connect to the Rithmic server."""
        if self._ws is not None:
            return
            
        uri = f"wss://{self._hostname}"
        self._ws = await websockets.connect(uri, ssl=self._ssl_context, ping_interval=3)
        logger.info(f"Connected to {uri}")
        
        # Login after connecting
        await self._login()
        
    async def disconnect(self) -> None:
        """Disconnect from the Rithmic server."""
        if self._ws is not None:
            await self._logout()
            await self._ws.close(1000, "see you tomorrow")
            self._ws = None
            logger.info("Disconnected from Rithmic")
            
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the Rithmic server.
        
        Args:
            request: The request to send
            
        Returns:
            The response from the server
        """
        if self._ws is None:
            raise RuntimeError("Not connected to Rithmic")
            
        # Serialize the request
        serialized = self._serialize_request(request)
        
        # Send the request
        await self._ws.send(serialized)
        logger.info(f"Sent request: {request}")
        
        # Wait for and process the response
        response = await self._receive_response()
        return response
        
    async def _login(self) -> None:
        """Log in to the Rithmic server."""
        request = {
            'template_id': 10,
            'template_version': '3.9',
            'user_msg': ['hello'],
            'user': self._user_id,
            'password': self._password,
            'app_name': 'SampleMD.py',
            'app_version': '0.3.0.0',
            'system_name': self._system_name,
            'infra_type': 'HISTORY_PLANT'  # Use HISTORY_PLANT for historical data
        }
        
        response = await self.send_request(request)
        
        if response.get('rp_code', [''])[0] != '0':
            raise RuntimeError(f"Login failed: {response.get('rp_code')}")
            
        logger.info("Logged in to Rithmic")
        
    async def _logout(self) -> None:
        """Log out from the Rithmic server."""
        request = {
            'template_id': 12,
            'user_msg': ['hello']
        }
        
        await self.send_request(request)
        logger.info("Logged out from Rithmic")
        
    def _serialize_request(self, request: Dict[str, Any]) -> bytes:
        """Serialize a request into bytes.
        
        Args:
            request: The request to serialize
            
        Returns:
            The serialized request
        """
        # TODO: Implement proper protobuf serialization
        # For now, just convert to bytes
        return str(request).encode()
        
    async def _receive_response(self) -> Dict[str, Any]:
        """Receive and process a response from the Rithmic server.
        
        Returns:
            The processed response
        """
        if self._ws is None:
            raise RuntimeError("Not connected to Rithmic")
            
        # Receive the response
        response_buf = await self._ws.recv()
        
        # Parse the response
        response = self._parse_response(response_buf)
        
        # Handle the response based on its template ID
        template_id = response.get('template_id')
        if template_id in self._response_handlers:
            self._response_handlers[template_id](response)
            
        return response
        
    def _parse_response(self, response_buf: bytes) -> Dict[str, Any]:
        """Parse a response from bytes into a dictionary.
        
        Args:
            response_buf: The response bytes
            
        Returns:
            The parsed response
        """
        # TODO: Implement proper protobuf parsing
        # For now, just convert from bytes
        return eval(response_buf.decode())
        
    def _handle_tick_bar_replay_response(self, response: Dict[str, Any]) -> None:
        """Handle a tick bar replay response.
        
        Args:
            response: The response to handle
        """
        # Check if this is the end-of-response message
        if not response.get('rq_handler_rp_code') and response.get('rp_code'):
            logger.info("Tick bar replay complete")
            
        # Log the response
        logger.info(f"Received tick bar: {response}")
        
    def _handle_tick_bar_response(self, response: Dict[str, Any]) -> None:
        """Handle a tick bar response.
        
        Args:
            response: The response to handle
        """
        # Log the response
        logger.info(f"Received tick: {response}")
        
    async def subscribe_order_book(self, symbol: str) -> None:
        """Subscribe to order book updates for a symbol.
        
        Args:
            symbol: Symbol to subscribe to
        """
        if not self._ws:
            raise ConnectionError("Not connected to Rithmic")
            
        if symbol in self._subscriptions:
            logger.info(f"Already subscribed to {symbol}")
            return
            
        try:
            msg = RequestMarketDataUpdate()
            msg.template_id = 100
            msg.user_msg.append("hello")
            msg.symbol = symbol
            msg.exchange = "CME"  # Default to CME, should be configurable
            msg.request = RequestMarketDataUpdate.Request.SUBSCRIBE
            msg.update_bits = RequestMarketDataUpdate.UpdateBits.BBO | RequestMarketDataUpdate.UpdateBits.ORDER_BOOK
            
            await self._send_message(msg)
            self._subscriptions.add(symbol)
            logger.info(f"Subscribed to order book for {symbol}")
            
        except Exception as e:
            logger.error(f"Error subscribing to order book: {e}")
            raise
            
    async def subscribe_trades(self, symbol: str) -> None:
        """Subscribe to trade updates for a symbol.
        
        Args:
            symbol: Symbol to subscribe to
        """
        if not self._ws:
            raise ConnectionError("Not connected to Rithmic")
            
        if symbol in self._subscriptions:
            logger.info(f"Already subscribed to {symbol}")
            return
            
        try:
            msg = RequestMarketDataUpdate()
            msg.template_id = 100
            msg.user_msg.append("hello")
            msg.symbol = symbol
            msg.exchange = "CME"  # Default to CME, should be configurable
            msg.request = RequestMarketDataUpdate.Request.SUBSCRIBE
            msg.update_bits = RequestMarketDataUpdate.UpdateBits.LAST_TRADE
            
            await self._send_message(msg)
            self._subscriptions.add(symbol)
            logger.info(f"Subscribed to trades for {symbol}")
            
        except Exception as e:
            logger.error(f"Error subscribing to trades: {e}")
            raise
            
    async def get_order_book(self, symbol: str) -> Optional[OrderBookSnapshot]:
        """Get the current order book for a symbol.
        
        Args:
            symbol: Symbol to get order book for
            
        Returns:
            Optional[OrderBookSnapshot]: Current order book snapshot or None if not available
        """
        if not self._ws:
            raise ConnectionError("Not connected to Rithmic")
            
        if symbol not in self._subscriptions:
            await self.subscribe_order_book(symbol)
            
        try:
            # Wait for order book update
            while True:
                msg = await self._receive_message()
                if not msg:
                    continue
                    
                if isinstance(msg, BestBidOffer) and msg.symbol == symbol:
                    # Convert BestBidOffer to OrderBookSnapshot
                    bids = [OrderBookLevel(price=msg.bid_price, size=msg.bid_size)]
                    asks = [OrderBookLevel(price=msg.ask_price, size=msg.ask_size)]
                    return OrderBookSnapshot(
                        symbol=symbol,
                        timestamp=msg.usecs,
                        bids=bids,
                        asks=asks
                    )
                    
        except Exception as e:
            logger.error(f"Error getting order book: {e}")
            return None
            
    async def get_trades(self, symbol: str) -> Optional[List[Trade]]:
        """Get recent trades for a symbol.
        
        Args:
            symbol: Symbol to get trades for
            
        Returns:
            Optional[List[Trade]]: List of recent trades or None if not available
        """
        if not self._ws:
            raise ConnectionError("Not connected to Rithmic")
            
        if symbol not in self._subscriptions:
            await self.subscribe_trades(symbol)
            
        try:
            # Wait for trade update
            while True:
                msg = await self._receive_message()
                if not msg:
                    continue
                    
                if isinstance(msg, LastTrade) and msg.symbol == symbol:
                    # Convert LastTrade to Trade
                    trade = Trade(
                        symbol=symbol,
                        price=msg.price,
                        size=msg.size,
                        timestamp=msg.usecs,
                        flags=TradeFlags(
                            is_buy=msg.side == "B",
                            is_sell=msg.side == "S",
                            is_aggressive=msg.aggressive
                        )
                    )
                    return [trade]
                    
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return None
            
    async def _send_message(self, message: Message) -> None:
        """Send a protobuf message to the server.
        
        Args:
            message: Protobuf message to send
        """
        if not self._ws:
            raise ConnectionError("Not connected to Rithmic")
            
        try:
            serialized = message.SerializeToString()
            await self._ws.send(serialized)
            logger.debug(f"Sent message: {message}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
            
    async def _receive_message(self) -> Optional[Message]:
        """Receive and parse messages from the server.
        
        Returns:
            Optional[Message]: Parsed protobuf message or None if no message received
        """
        if not self._ws:
            raise ConnectionError("Not connected to Rithmic")
            
        try:
            data = await self._ws.recv()
            if not data:
                return None
                
            # Parse message based on template_id
            template_id = int.from_bytes(data[0:4], byteorder='little')
            
            if template_id == 11:  # ResponseLogin
                msg = ResponseLogin()
            elif template_id == 100:  # RequestMarketDataUpdate
                msg = RequestMarketDataUpdate()
            elif template_id == 101:  # ResponseMarketDataUpdate
                msg = ResponseMarketDataUpdate()
            elif template_id == 102:  # LastTrade
                msg = LastTrade()
            elif template_id == 103:  # BestBidOffer
                msg = BestBidOffer()
            else:
                logger.warning(f"Unknown message type: {template_id}")
                return None
                
            msg.ParseFromString(data)
            logger.debug(f"Received message: {msg}")
            return msg
            
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            raise

    def parse_order_book(self, data: bytes) -> OrderBookSnapshot:
        """
        Parse order book data from Rithmic protocol.
        
        Args:
            data: Raw order book data
            
        Returns:
            OrderBookSnapshot containing parsed data
        """
        # TODO: Implement Rithmic order book parsing
        pass
    
    def parse_trade(self, data: bytes) -> Trade:
        """
        Parse trade data from Rithmic protocol.
        
        Args:
            data: Raw trade data
            
        Returns:
            Trade containing parsed data
        """
        # TODO: Implement Rithmic trade parsing
        pass 