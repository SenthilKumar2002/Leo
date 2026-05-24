#!/usr/bin/env python3
"""
Leo - Advanced DDoS/DoS Detection System
Command-line interface with async detection loop
"""

import sys
import argparse
import time
import threading
import logging
import json
import asyncio
from datetime import datetime
import signal
import traceback

from scapy.all import sniff

from leo_config import config, validate_root
from leo_detector import detector
from leo_response import response_engine
from leo_terminal import show_dashboard, ui
from leo_threat_intel import threat_intel

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global state
shutdown_event = threading.Event()

def signal_handler(signum, frame):
    """Handle signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down...")
    shutdown_event.set()

async def detection_loop_async():
    """Async detection loop - non-blocking"""
    last_check = time.time()
    logger.info("Detection loop started")
    
    while not shutdown_event.is_set():
        try:
            await asyncio.sleep(1)
            
            if time.time() - last_check >= config.DETECTION_WINDOW:
                # Run detection (non-blocking)
                alert = await asyncio.to_thread(detector.detect)
                
                if alert:
                    try:
                        # Save to incident file (non-blocking)
                        await asyncio.to_thread(
                            lambda: (
                                open(config.INCIDENT_FILE, 'a').write(json.dumps(alert) + '\n'),
                                logger.critical(f"ATTACK DETECTED: {json.dumps(alert)}"),
                                threat_intel.mark_as_attacker(
                                    alert.get('type', ''),
                                    alert.get('type', ''),
                                    alert.get('confidence', 0)
                                ),
                                response_engine.execute(alert)
                            )[-1]
                        )
                    except Exception as e:
                        logger.error(f"Alert processing error: {e}\n{traceback.format_exc()}")
                
                # Reset counters
                detector.reset_counters()
                last_check = time.time()
        
        except Exception as e:
            logger.error(f"Detection loop error: {e}\n{traceback.format_exc()}")
            await asyncio.sleep(5)

def detection_loop_sync():
    """Synchronous wrapper for async detection loop"""
    try:
        asyncio.run(detection_loop_async())
    except Exception as e:
        logger.error(f"Async loop error: {e}")

def start_detection(interface):
    """Start packet capture"""
    logger.info(f"Starting packet capture on {interface}")
    
    try:
        sniff(
            iface=interface,
            prn=detector.process_packet,
            store=False,
            stop_filter=lambda x: shutdown_event.is_set()
        )
    except PermissionError:
        logger.error("Packet capture requires root privileges")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Packet capture error: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Leo - Advanced DDoS/DoS Detection System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  leo start              Start Leo with dashboard
  leo status             Show current status
  leo logs               Show recent alerts
  leo config             Show configuration
  leo health             System health check
  leo performance        Performance metrics
        """
    )
    
    parser.add_argument(
        'command',
        choices=['start', 'status', 'logs', 'config', 'health', 'performance', 'help'],
        help='Command to execute'
    )
    
    parser.add_argument('-i', '--interface', default=config.INTERFACE, 
                       help=f'Network interface (default: {config.INTERFACE})')
    parser.add_argument('-w', '--window', type=int, default=config.DETECTION_WINDOW,
                       help=f'Detection window in seconds (default: {config.DETECTION_WINDOW})')
    parser.add_argument('-c', '--confidence', type=float, default=config.MIN_CONFIDENCE,
                       help=f'Minimum confidence threshold (default: {config.MIN_CONFIDENCE})')
    
    args = parser.parse_args()
    
    # Update config
    config.INTERFACE = args.interface
    config.DETECTION_WINDOW = args.window
    config.MIN_CONFIDENCE = args.confidence
    
    if args.command == 'start':
        try:
            validate_root()
        except PermissionError as e:
            print(f"Error: {e}")
            sys.exit(1)
        
        logger.info("="*80)
        logger.info("Leo Detection System Starting")
        logger.info("="*80)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start detection thread (with async)
        det_thread = threading.Thread(target=detection_loop_sync, daemon=True)
        det_thread.start()
        
        # Start packet capture thread
        cap_thread = threading.Thread(
            target=start_detection,
            args=(config.INTERFACE,),
            daemon=True
        )
        cap_thread.start()
        
        # Show dashboard
        time.sleep(1)
        show_dashboard()
    
    elif args.command == 'status':
        stats = detector.get_stats()
        print("\n┌" + "─"*42 + "┐")
        print("│ Leo Status".ljust(43) + "│")
        print("├" + "─"*42 + "┤")
        print(f"│ Total Packets   │ {stats['total_packets']:>20,} │")
        print(f"│ Total Bytes     │ {stats['total_bytes']:>20,} │")
        print(f"│ Total Alerts    │ {stats['total_alerts']:>20,} │")
        print(f"│ Critical        │ {stats['critical']:>20,} │")
        print(f"│ High            │ {stats['high']:>20,} │")
        print("└" + "─"*42 + "┘\n")
    
    elif args.command == 'logs':
        try:
            with open(config.INCIDENT_FILE, 'r') as f:
                lines = f.readlines()[-10:]
                print("\n┌" + "─"*58 + "┐")
                print("│ Recent Alerts".ljust(59) + "│")
                print("├" + "─"*58 + "┤")
                if not lines:
                    print("│ No incidents logged yet".ljust(59) + "│")
                else:
                    for line in lines:
                        try:
                            alert = json.loads(line)
                            ts, atype, conf, sev = alert.get('timestamp', ''), alert.get('type', ''), \
                                                   alert.get('confidence', 0), alert.get('severity', '')
                            print(f"│ [{ts}] {atype:<20} {conf:>5.0%} {sev:<10} │")
                        except json.JSONDecodeError:
                            pass
                print("└" + "─"*58 + "┘\n")
        except FileNotFoundError:
            print("\nNo incidents logged yet.\n")
    
    elif args.command == 'config':
        print("\n┌" + "─"*50 + "┐")
        print("│ Leo Configuration".ljust(51) + "│")
        print("├" + "─"*50 + "┤")
        for key, value in sorted(config.to_dict().items()):
            if not key.startswith('_'):
                val_str = str(value)[:30]
                print(f"│ {key:<25} │ {val_str:<22} │")
        print("└" + "─"*50 + "┘\n")
    
    elif args.command == 'health':
        stats = detector.get_stats()
        print("\n┌" + "─"*50 + "┐")
        print("│ System Health".ljust(51) + "│")
        print("├" + "─"*50 + "┤")
        print(f"│ Total Packets    │ {stats['total_packets']:>18,}     │")
        print(f"│ Total Alerts     │ {stats['total_alerts']:>18,}     │")
        print(f"│ Active Flows     │ {stats['active_flows']:>18,}     │")
        print(f"│ Uptime           │ {stats['uptime_seconds']:>15}s         │")
        print("└" + "─"*50 + "┘\n")
    
    elif args.command == 'performance':
        stats = detector.get_stats()
        print("\n┌" + "─"*50 + "┐")
        print("│ Performance Metrics".ljust(51) + "│")
        print("├" + "─"*50 + "┤")
        print(f"│ Detection Latency │ {stats['avg_detection_time_ms']:>14.2f} ms    │")
        print(f"│ Packet Process    │ {stats['avg_packet_time_us']:>14.2f} µs    │")
        print(f"│ Active Flows      │ {stats['active_flows']:>18,}     │")
        print("└" + "─"*50 + "┘\n")
    
    elif args.command == 'help':
        parser.print_help()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}\n{traceback.format_exc()}")
        sys.exit(1)
