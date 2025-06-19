import asyncio
import logging
import ssl
import websockets
from datetime import datetime
import pytz
from typing import Optional, List, Dict, Any

from .protocol import RithmicProtocol
from ..base import DataProvider

logger = logging.getLogger(__name__)

class RithmicHistoricalProvider(DataProvider):
    """Provider for historical market data from Rithmic."""
    
    def __init__(
        self,
        hostname: str,
        user_id: str,
        password: str,
        system_name: str = "Rithmic Test",
        ssl_context: Optional[ssl.SSLContext] = None
    ):
        """Initialize the Rithmic historical data provider.
        
        Args:
            hostname: Rithmic server hostname (e.g., 'rituz00100.rithmic.com:443')
            user_id: Rithmic user ID
            password: Rithmic password
            system_name: Rithmic system name (default: "Rithmic Test")
            ssl_context: Optional SSL context for secure connections
        """
        self._protocol = RithmicProtocol(
            hostname=hostname,
            user_id=user_id,
            password=password,
            system_name=system_name,
            ssl_context=ssl_context
        )
        self._downloads: Dict[str, Any] = {}  # Track ongoing downloads
        self._is_done = False  # Flag to track when historical data request is complete
        
    async def download_historical_tick_data(
        self,
        security_code: str,
        exchange_code: str,
        start_time: datetime,
        end_time: datetime,
        download_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Download historical tick data for a specific instrument and time range.
        
        Args:
            security_code: The security code (e.g., 'ESZ3')
            exchange_code: The exchange code (e.g., 'CME')
            start_time: Start time in UTC
            end_time: End time in UTC
            download_id: Optional download ID for tracking
            
        Returns:
            Dictionary containing download status and data
        """
        if not download_id:
            download_id = f"{security_code}_{exchange_code}_{start_time.strftime('%Y%m%d_%H%M%S')}"
            
        # Ensure times are in UTC
        if start_time.tzinfo is None:
            start_time = pytz.UTC.localize(start_time)
        if end_time.tzinfo is None:
            end_time = pytz.UTC.localize(end_time)
            
        # Initialize download tracking
        self._downloads[download_id] = {
            'status': 'pending',
            'security_code': security_code,
            'exchange_code': exchange_code,
            'start_time': start_time,
            'end_time': end_time,
            'data': [],
            'error': None
        }
        
        try:
            # Connect to Rithmic
            await self._protocol.connect()
            
            # Request historical data
            request = {
                'template_id': 206,  # Historical tick data request
                'security_code': security_code,
                'exchange_code': exchange_code,
                'bar_type': 'TICK_BAR',
                'bar_type_specifier': '1',  # 1 tick per bar
                'bar_sub_type': 'REGULAR',  # Regular session bars
                'start_index': int(start_time.timestamp()),
                'finish_index': int(end_time.timestamp())
            }
            
            # Send request and process response
            self._is_done = False
            response = await self._protocol.send_request(request)
            
            # Wait for all data to be received
            while not self._is_done:
                await asyncio.sleep(0.1)
            
            if response.get('status') == 'success':
                self._downloads[download_id]['status'] = 'completed'
                self._downloads[download_id]['data'] = response.get('data', [])
            else:
                self._downloads[download_id]['status'] = 'failed'
                self._downloads[download_id]['error'] = response.get('error')
                
        except Exception as e:
            logger.error(f"Error downloading historical data: {e}")
            self._downloads[download_id]['status'] = 'failed'
            self._downloads[download_id]['error'] = str(e)
            
        finally:
            # Always disconnect after download
            await self._protocol.disconnect()
            
        return self._downloads[download_id]
    
    async def download_historical_bar_data(
        self,
        security_code: str,
        exchange_code: str,
        start_time: datetime,
        end_time: datetime,
        bar_size: str = '1m',  # 1 minute bars
        download_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Download historical bar data for a specific instrument and time range.
        
        Args:
            security_code: The security code (e.g., 'ESZ3')
            exchange_code: The exchange code (e.g., 'CME')
            start_time: Start time in UTC
            end_time: End time in UTC
            bar_size: Bar size (e.g., '1m', '5m', '1h')
            download_id: Optional download ID for tracking
            
        Returns:
            Dictionary containing download status and data
        """
        if not download_id:
            download_id = f"{security_code}_{exchange_code}_{bar_size}_{start_time.strftime('%Y%m%d_%H%M%S')}"
            
        # Ensure times are in UTC
        if start_time.tzinfo is None:
            start_time = pytz.UTC.localize(start_time)
        if end_time.tzinfo is None:
            end_time = pytz.UTC.localize(end_time)
            
        # Initialize download tracking
        self._downloads[download_id] = {
            'status': 'pending',
            'security_code': security_code,
            'exchange_code': exchange_code,
            'bar_size': bar_size,
            'start_time': start_time,
            'end_time': end_time,
            'data': [],
            'error': None
        }
        
        try:
            # Connect to Rithmic
            await self._protocol.connect()
            
            # Request historical data
            request = {
                'template_id': 206,  # Historical bar data request
                'security_code': security_code,
                'exchange_code': exchange_code,
                'bar_type': 'TIME_BAR',
                'bar_type_specifier': bar_size,  # e.g., '1m' for 1 minute bars
                'bar_sub_type': 'REGULAR',  # Regular session bars
                'start_index': int(start_time.timestamp()),
                'finish_index': int(end_time.timestamp())
            }
            
            # Send request and process response
            self._is_done = False
            response = await self._protocol.send_request(request)
            
            # Wait for all data to be received
            while not self._is_done:
                await asyncio.sleep(0.1)
            
            if response.get('status') == 'success':
                self._downloads[download_id]['status'] = 'completed'
                self._downloads[download_id]['data'] = response.get('data', [])
            else:
                self._downloads[download_id]['status'] = 'failed'
                self._downloads[download_id]['error'] = response.get('error')
                
        except Exception as e:
            logger.error(f"Error downloading historical bar data: {e}")
            self._downloads[download_id]['status'] = 'failed'
            self._downloads[download_id]['error'] = str(e)
            
        finally:
            # Always disconnect after download
            await self._protocol.disconnect()
            
        return self._downloads[download_id]
    
    def get_download_status(self, download_id: str) -> Dict[str, Any]:
        """Get the status of a historical data download.
        
        Args:
            download_id: The download ID to check
            
        Returns:
            Dictionary containing download status and data
        """
        return self._downloads.get(download_id, {'status': 'not_found'})
    
    def clear_download(self, download_id: str) -> None:
        """Clear a completed or failed download from memory.
        
        Args:
            download_id: The download ID to clear
        """
        if download_id in self._downloads:
            del self._downloads[download_id]
            
    def _handle_historical_response(self, response: Dict[str, Any]) -> None:
        """Handle a historical data response.
        
        Args:
            response: The response from the Rithmic server
        """
        # Check if this is the end-of-response message
        if not response.get('rq_handler_rp_code') and response.get('rp_code'):
            self._is_done = True
            
        # Add data to the appropriate download
        download_id = response.get('download_id')
        if download_id in self._downloads:
            self._downloads[download_id]['data'].append(response) 