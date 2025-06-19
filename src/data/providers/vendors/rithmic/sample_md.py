import asyncio
import ssl
import pathlib
import websockets
import sys
import logging
import os
import glob

# Add the sample directory to the Python path
proto_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../software/0.84.0.0/samples/samples.py'))
print(f"Protobuf directory: {proto_dir}")
print("Directory contents:", glob.glob(os.path.join(proto_dir, '*.py')))
sys.path.append(proto_dir)

from request_login_pb2 import RequestLogin
from response_login_pb2 import ResponseLogin
from request_market_data_update_pb2 import RequestMarketDataUpdate
from request_logout_pb2 import RequestLogout
from request_rithmic_system_info_pb2 import RequestRithmicSystemInfo
from response_rithmic_system_info_pb2 import ResponseRithmicSystemInfo
from request_heartbeat_pb2 import RequestHeartbeat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def connect_to_rithmic(uri, ssl_context):
    """Connect to the Rithmic system using websockets."""
    try:
        ws = await websockets.connect(uri, ssl=ssl_context, ping_interval=3)
        logger.info(f"Connected to {uri}")
        return ws
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        return None

async def send_heartbeat(ws):
    """Send a heartbeat request."""
    rq = RequestHeartbeat()
    rq.template_id = 18
    serialized = rq.SerializeToString()
    await ws.send(serialized)
    logger.info("Sent heartbeat request")

async def list_systems(uri, ssl_context):
    """List available Rithmic systems."""
    ws = await connect_to_rithmic(uri, ssl_context)
    if not ws:
        return []

    try:
        rq = RequestRithmicSystemInfo()
        rq.template_id = 16
        rq.user_msg.append("hello")

        serialized = rq.SerializeToString()
        await ws.send(serialized)
        logger.info("Sent list_systems request")

        rp_buf = await ws.recv()
        rp = ResponseRithmicSystemInfo()
        rp.ParseFromString(rp_buf)

        if rp.rp_code[0] == "0":
            logger.info("Available Systems:")
            logger.info("=================")
            for sys_name in rp.system_name:
                logger.info(sys_name)
            return rp.system_name
        else:
            logger.error(f"Error retrieving system list:")
            logger.error(f"template_id: {rp.template_id}")
            logger.error(f"user_msg: {rp.user_msg}")
            logger.error(f"rp_code: {rp.rp_code}")
            logger.error(f"system_name: {rp.system_name}")
            return []
    finally:
        await ws.close(1000, "done listing systems")

async def rithmic_login(ws, system_name, infra_type, user_id, password):
    """Log into the Rithmic system using the provided credentials."""
    rq = RequestLogin()
    rq.template_id = 10
    rq.template_version = "3.9"
    rq.user_msg.append("hello")
    rq.user = user_id
    rq.password = password
    rq.app_name = "SampleMD.py"
    rq.app_version = "0.3.0.0"
    rq.system_name = system_name
    rq.infra_type = infra_type

    serialized = rq.SerializeToString()
    await ws.send(serialized)

    rp_buf = await ws.recv()
    rp = ResponseLogin()
    rp.ParseFromString(rp_buf)
    logger.info(f"ResponseLogin: template_id={rp.template_id}, rp_code={rp.rp_code}")
    
    if rp.rp_code and rp.rp_code[0] != '0':
        raise Exception(f"Login failed: {rp.rp_code}")

async def subscribe(ws, exchange, symbol):
    """Subscribe to market data for the specified instrument."""
    rq = RequestMarketDataUpdate()
    rq.template_id = 100
    rq.user_msg.append("hello")
    rq.symbol = symbol
    rq.exchange = exchange
    rq.request = RequestMarketDataUpdate.Request.SUBSCRIBE
    rq.update_bits = RequestMarketDataUpdate.UpdateBits.LAST_TRADE | RequestMarketDataUpdate.UpdateBits.BBO

    serialized = rq.SerializeToString()
    await ws.send(serialized)
    logger.info(f"Subscribed to {symbol} on {exchange}")

async def unsubscribe(ws, exchange, symbol):
    """Unsubscribe from market data for the specified instrument."""
    rq = RequestMarketDataUpdate()
    rq.template_id = 100
    rq.user_msg.append("hello")
    rq.symbol = symbol
    rq.exchange = exchange
    rq.request = RequestMarketDataUpdate.Request.UNSUBSCRIBE
    rq.update_bits = RequestMarketDataUpdate.UpdateBits.LAST_TRADE | RequestMarketDataUpdate.UpdateBits.BBO

    serialized = rq.SerializeToString()
    await ws.send(serialized)
    logger.info(f"Unsubscribed from {symbol} on {exchange}")

async def rithmic_logout(ws):
    """Send a logout request."""
    rq = RequestLogout()
    rq.template_id = 12
    rq.user_msg.append("hello")
    serialized = rq.SerializeToString()
    await ws.send(serialized)
    logger.info("Logout request sent")

async def disconnect_from_rithmic(ws):
    """Close the websocket connection."""
    await ws.close(1000, "see you tomorrow")
    logger.info("Disconnected from Rithmic")

async def consume(ws, stop_event):
    """Consume messages from the websocket until the stop event is set."""
    # Send a heartbeat immediately
    await send_heartbeat(ws)
    
    last_heartbeat = asyncio.get_event_loop().time()
    heartbeat_interval = 30  # Send heartbeat every 30 seconds
    
    while not stop_event.is_set():
        try:
            # Check if it's time to send a heartbeat
            now = asyncio.get_event_loop().time()
            if now - last_heartbeat >= heartbeat_interval:
                await send_heartbeat(ws)
                last_heartbeat = now
            
            # Try to receive a message with a timeout
            message = await asyncio.wait_for(ws.recv(), timeout=5)
            logger.info(f"Received message: {message}")
        except asyncio.TimeoutError:
            continue
        except websockets.exceptions.ConnectionClosed:
            logger.error("Connection closed")
            break
        except Exception as e:
            logger.error(f"Error in consume: {e}")
            break

async def handle_user_input(stop_event):
    """Wait for user input and set the stop event when 'quit' is received."""
    while True:
        user_input = await asyncio.get_event_loop().run_in_executor(None, input)
        if user_input.strip().lower() == 'quit':
            logger.info("\nQuit received from user. Exiting\n")
            stop_event.set()
            break

async def main():
    if len(sys.argv) != 7:
        logger.error("Usage: python sample_md.py <uri> <system_name> <user_id> <password> <exchange> <symbol>")
        return

    uri = sys.argv[1]
    system_name = sys.argv[2]
    user_id = sys.argv[3]
    password = sys.argv[4]
    exchange = sys.argv[5]
    symbol = sys.argv[6]

    ssl_context = None
    if "wss://" in uri:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    try:
        # First list available systems
        available_systems = await list_systems(uri, ssl_context)
        if not available_systems:
            logger.error("No systems available")
            return

        # Use the first available system if the provided one is not valid
        if system_name not in available_systems:
            logger.warning(f"System {system_name} not found in available systems. Using {available_systems[0]} instead.")
            system_name = available_systems[0]

        # Create a new connection for login and subscription
        ws = await connect_to_rithmic(uri, ssl_context)
        if not ws:
            return

        try:
            await rithmic_login(ws, system_name, RequestLogin.SysInfraType.TICKER_PLANT, user_id, password)
            await subscribe(ws, exchange, symbol)

            stop_event = asyncio.Event()
            consume_task = asyncio.create_task(consume(ws, stop_event))
            input_task = asyncio.create_task(handle_user_input(stop_event))

            try:
                await asyncio.gather(consume_task, input_task)
            finally:
                await unsubscribe(ws, exchange, symbol)
                await rithmic_logout(ws)
                await disconnect_from_rithmic(ws)
        except Exception as e:
            logger.error(f"Error in main: {e}")
            if ws:
                await disconnect_from_rithmic(ws)
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())
