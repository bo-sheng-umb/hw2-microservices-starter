#!/usr/bin/env python3
"""
CS446/646 - Network Programming Assignment 2: Microservices with RPC and Load Balancing
Student Starter Code

Name: [Your Name]
ID: [Your Student ID]
"""

import socket
import json
import time
import threading
import random
import struct
import hashlib
import queue
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


# ============================================================
# CONFIGURATION: Edit this section for cloud deployment
# ============================================================

# For local testing (default):
SERVICE_INSTANCES = [
    ('localhost', 9000),
    ('localhost', 9001),
    ('localhost', 9002),
]

# For cloud deployment, uncomment and replace with your GCP instance IPs:
# SERVICE_INSTANCES = [
#     ('35.232.123.45', 9000),  # Replace with your instance-0 IP
#     ('35.232.123.46', 9001),  # Replace with your instance-1 IP  
#     ('35.232.123.47', 9002),  # Replace with your instance-2 IP
# ]

# ============================================================
# End of configuration section
# ============================================================

# ===================== PROTOCOL DEFINITION =====================
# DO NOT MODIFY THIS SECTION

class MessageType(Enum):
    """RPC message types"""
    REQUEST = 1
    RESPONSE = 2
    HEALTH_CHECK = 3
    HEALTH_RESPONSE = 4
    REGISTER = 5
    DISCOVER = 6
    HEARTBEAT = 7
    METRICS = 8

class StatusCode(Enum):
    """Response status codes"""
    OK = 0
    CANCELLED = 1
    DEADLINE_EXCEEDED = 2
    NOT_FOUND = 3
    UNAVAILABLE = 4
    INTERNAL_ERROR = 5

@dataclass
class Request:
    """RPC Request structure"""
    request_id: str
    method: str
    operation: str
    values: List[float]
    deadline: float  # Unix timestamp
    metadata: Dict[str, str]

@dataclass
class Response:
    """RPC Response structure"""
    request_id: str
    status: StatusCode
    result: Optional[float]
    error_message: Optional[str]
    latency_ms: float
    server_id: str

class Protocol:
    """Wire protocol for RPC communication - PROVIDED"""
    
    @staticmethod
    def encode_message(msg_type: MessageType, data: dict) -> bytes:
        """Encode message for transmission"""
        json_data = json.dumps(data).encode('utf-8')
        length = len(json_data) + 1
        header = struct.pack('!IB', length, msg_type.value)
        return header + json_data
    
    @staticmethod
    def decode_message(sock: socket.socket) -> Tuple[Optional[MessageType], Optional[dict]]:
        """Decode received message"""
        try:
            header = sock.recv(5)
            if not header or len(header) < 5:
                return None, None
            length, msg_type = struct.unpack('!IB', header)
            data = b''
            while len(data) < length - 1:
                chunk = sock.recv(min(4096, length - 1 - len(data)))
                if not chunk:
                    return None, None
                data += chunk
            return MessageType(msg_type), json.loads(data.decode('utf-8'))
        except Exception as e:
            print(f"Protocol decode error: {e}")
            return None, None

# ===================== SERVICE IMPLEMENTATION =====================

class ServiceInstance:
    """Microservice instance - STUDENT MUST IMPLEMENT MARKED SECTIONS"""
    
    def __init__(self, instance_id: str, port: int):
        self.instance_id = instance_id
        self.port = port
        self.socket = None
        self.running = False
        
        # Service state
        self.current_load = 0
        self.max_load = 100
        self.healthy = True
        self.processing_times = deque(maxlen=100)
        
        # Fault injection (for testing)
        self.inject_latency = 0
        self.error_rate = 0.0
    
    def start(self):
        """Start service instance"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', self.port))
        self.socket.listen(10)
        self.running = True
        
        print(f"Service {self.instance_id} listening on port {self.port}")
        
        # Start health monitor
        threading.Thread(target=self._health_monitor, daemon=True).start()
        
        while self.running:
            try:
                client_sock, addr = self.socket.accept()
                if self.current_load < self.max_load:
                    threading.Thread(target=self.handle_request, 
                                   args=(client_sock,), daemon=True).start()
                else:
                    self._send_error(client_sock, StatusCode.UNAVAILABLE, 
                                   "Service overloaded")
                    client_sock.close()
            except:
                break
    
    def handle_request(self, client_sock: socket.socket):
        """Handle incoming RPC request"""
        self.current_load += 1
        start_time = time.time()
        
        try:
            msg_type, data = Protocol.decode_message(client_sock)
            
            if msg_type == MessageType.REQUEST:
                # TODO: STUDENT MUST IMPLEMENT
                # 1. Parse request from data dictionary
                # 2. Check if deadline has passed
                # 3. Apply fault injection if configured (for testing)
                # 4. Perform the calculation using self._calculate()
                # 5. Create response with appropriate status and result
                # 6. Send response using Protocol.encode_message()
                
                # Your code here...
                pass
                
            elif msg_type == MessageType.HEALTH_CHECK:
                # TODO: STUDENT MUST IMPLEMENT
                # Return health status including:
                # - healthy: boolean
                # - current_load: int
                # - average_latency: float (from self.processing_times)
                
                # Your code here...
                pass
                
        except Exception as e:
            print(f"Error handling request: {e}")
            self._send_error(client_sock, StatusCode.INTERNAL_ERROR, str(e))
        finally:
            self.current_load -= 1
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            client_sock.close()
    
    def _calculate(self, operation: str, values: List[float]) -> float:
        """Perform calculation based on operation"""
        # TODO: STUDENT MUST IMPLEMENT
        # Support operations: sum, avg, min, max, multiply
        # Raise ValueError for unknown operations
        
        # Your code here...
        pass
    
    def _send_error(self, sock: socket.socket, status: StatusCode, message: str):
        """Send error response - PROVIDED"""
        response = {
            'request_id': 'error',
            'status': status.value,
            'result': None,
            'error_message': message,
            'latency_ms': 0,
            'server_id': self.instance_id
        }
        sock.send(Protocol.encode_message(MessageType.RESPONSE, response))
    
    def _health_monitor(self):
        """Monitor service health"""
        # TODO: STUDENT MUST IMPLEMENT
        # Periodically update self.healthy based on:
        # - Current load vs max load
        # - Average processing time
        # - Error rate
        
        while self.running:
            time.sleep(5)
            # Your code here...
            pass
    
    def shutdown(self):
        """Shutdown service"""
        self.running = False
        if self.socket:
            self.socket.close()

# ===================== LOAD BALANCING =====================

class LoadBalancingStrategy(Enum):
    """Available load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    # Add more as you implement them

@dataclass
class InstanceInfo:
    """Service instance information"""
    instance_id: str
    host: str
    port: int
    weight: int = 1
    active_connections: int = 0
    total_requests: int = 0
    error_count: int = 0
    avg_latency: float = 0.0
    last_health_check: float = 0
    healthy: bool = True
    circuit_breaker_state: str = "closed"

class LoadBalancer:
    """Load balancer - STUDENT MUST IMPLEMENT STRATEGIES"""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.instances: Dict[str, InstanceInfo] = {}
        self.instance_list: List[str] = []
        
        # Round-robin state
        self.rr_index = 0
        
        # Statistics
        self.request_count = 0
        self.distribution = defaultdict(int)
        
        # Thread safety
        self.lock = threading.Lock()
    
    def add_instance(self, instance: InstanceInfo):
        """Add service instance to pool"""
        with self.lock:
            self.instances[instance.instance_id] = instance
            self.instance_list.append(instance.instance_id)
    
    def remove_instance(self, instance_id: str):
        """Remove service instance from pool"""
        with self.lock:
            if instance_id in self.instances:
                del self.instances[instance_id]
                self.instance_list.remove(instance_id)
    
    def select_instance(self, request: Request) -> Optional[InstanceInfo]:
        """Select instance for request based on strategy"""
        with self.lock:
            # Filter healthy instances
            healthy_instances = [
                iid for iid in self.instance_list 
                if self.instances[iid].healthy and 
                   self.instances[iid].circuit_breaker_state != "open"
            ]
            
            if not healthy_instances:
                return None
            
            selected_id = None
            
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                # TODO: STUDENT MUST IMPLEMENT
                # Round-robin: Select next instance in order
                # Update self.rr_index appropriately
                
                # Your code here...
                pass
                
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                # TODO: STUDENT MUST IMPLEMENT
                # Select instance with least active connections
                
                # Your code here...
                pass
                
            elif self.strategy == LoadBalancingStrategy.RANDOM:
                # TODO: STUDENT MUST IMPLEMENT
                # Random selection from healthy instances
                
                # Your code here...
                pass
            
            # Update statistics
            if selected_id:
                self.distribution[selected_id] += 1
                self.request_count += 1
                return self.instances[selected_id]
            
            return None
    
    def update_instance_stats(self, instance_id: str, latency: float, 
                            success: bool, connections_delta: int = 0):
        """Update instance statistics after request"""
        # TODO: STUDENT MUST IMPLEMENT
        # Update the instance's statistics:
        # - active_connections (using connections_delta)
        # - total_requests
        # - error_count (if not success)
        # - avg_latency (running average)
        
        with self.lock:
            if instance_id in self.instances:
                instance = self.instances[instance_id]
                # Your code here...
                pass
    
    def get_stats(self) -> dict:
        """Get load balancer statistics"""
        with self.lock:
            stats = {
                'total_requests': self.request_count,
                'strategy': self.strategy.value,
                'instances': {}
            }
            
            for iid, info in self.instances.items():
                stats['instances'][iid] = {
                    'requests': self.distribution[iid],
                    'percentage': (self.distribution[iid] / self.request_count * 100) 
                                if self.request_count > 0 else 0,
                    'healthy': info.healthy,
                    'avg_latency': info.avg_latency,
                    'active_connections': info.active_connections,
                    'errors': info.error_count
                }
            
            return stats

# ===================== CIRCUIT BREAKER =====================

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests  
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """Circuit breaker for fault tolerance - STUDENT MUST IMPLEMENT"""
    
    def __init__(self, instance_id: str,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 success_threshold: int = 3):
        self.instance_id = instance_id
        self.state = CircuitBreakerState.CLOSED
        
        # Configuration
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        # State tracking
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.last_state_change = time.time()
        
        # Metrics
        self.total_requests = 0
        self.rejected_requests = 0
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        # TODO: STUDENT MUST IMPLEMENT
        # 1. Check current state
        # 2. If OPEN:
        #    - Check if recovery_timeout has passed
        #    - If yes, transition to HALF_OPEN
        #    - If no, reject request
        # 3. If HALF_OPEN or CLOSED:
        #    - Try to execute function
        #    - Call on_success() if successful
        #    - Call on_failure() if failed
        # 4. Return result or raise exception
        
        self.total_requests += 1
        
        # Your code here...
        pass
    
    def on_success(self):
        """Handle successful call"""
        # TODO: STUDENT MUST IMPLEMENT
        # Update state based on success:
        # - If CLOSED: reset failure count
        # - If HALF_OPEN: increment success count
        #   - If success_count >= success_threshold: transition to CLOSED
        
        # Your code here...
        pass
    
    def on_failure(self):
        """Handle failed call"""
        # TODO: STUDENT MUST IMPLEMENT
        # Update state based on failure:
        # - If CLOSED: increment failure count
        #   - If failure_count >= failure_threshold: transition to OPEN
        # - If HALF_OPEN: transition to OPEN immediately
        
        # Your code here...
        pass
    
    def get_state(self) -> str:
        """Get current circuit breaker state"""
        return self.state.value

# ===================== SMART CLIENT =====================

class RetryStrategy(Enum):
    """Retry strategies"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"

class SmartClient:
    """Client with retry logic and circuit breakers - STUDENT MUST IMPLEMENT"""
    
    def __init__(self, load_balancer: LoadBalancer):
        self.load_balancer = load_balancer
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Configuration
        self.max_retries = 3
        self.retry_strategy = RetryStrategy.EXPONENTIAL
        self.base_delay = 100  # milliseconds
        self.timeout = 5.0  # seconds
        
        # Metrics
        self.request_log = []
    
    def send_request(self, request: Request) -> Response:
        """Send request with retries and circuit breaking"""
        # TODO: STUDENT MUST IMPLEMENT
        # 1. Try up to max_retries times:
        #    a. Select instance using load balancer
        #    b. Get/create circuit breaker for instance
        #    c. Use circuit breaker to call _send_single_request
        #    d. If successful, update stats and return response
        #    e. If failed, calculate retry delay and wait
        # 2. If all retries exhausted, raise exception
        
        attempt = 0
        last_error = None
        
        # Your code here...
        pass
    
    def _send_single_request(self, instance: InstanceInfo, request: Request) -> Response:
        """Send single request to instance"""
        # TODO: STUDENT MUST IMPLEMENT
        # 1. Create socket and set timeout
        # 2. Connect to instance (host, port)
        # 3. Send request using Protocol.encode_message
        # 4. Receive response using Protocol.decode_message
        # 5. Parse response and return Response object
        # 6. Handle socket errors appropriately
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            # Your code here...
            pass
        finally:
            sock.close()
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay in milliseconds"""
        # TODO: STUDENT MUST IMPLEMENT
        # Based on self.retry_strategy:
        # - EXPONENTIAL: base_delay * (2 ** attempt)
        # - LINEAR: base_delay * attempt
        # - FIXED: base_delay
        
        # Your code here...
        pass

# ===================== SERVICE REGISTRY =====================

class ServiceRegistry:
    """Service discovery and registration - STUDENT MUST IMPLEMENT"""
    
    def __init__(self):
        self.services: Dict[str, List[InstanceInfo]] = defaultdict(list)
        self.heartbeats: Dict[str, float] = {}
        self.ttl = 30  # seconds
        self.lock = threading.Lock()
        
        # Start cleanup thread
        threading.Thread(target=self._cleanup_stale, daemon=True).start()
    
    def register(self, service_name: str, instance: InstanceInfo):
        """Register service instance"""
        # TODO: STUDENT MUST IMPLEMENT
        # 1. Add instance to services[service_name] list
        # 2. Record current time in heartbeats[instance.instance_id]
        
        with self.lock:
            # Your code here...
            pass
    
    def discover(self, service_name: str) -> List[InstanceInfo]:
        """Discover available service instances"""
        # TODO: STUDENT MUST IMPLEMENT
        # Return list of instances for service_name that:
        # - Have sent heartbeat within TTL
        
        with self.lock:
            # Your code here...
            pass
    
    def heartbeat(self, instance_id: str):
        """Update instance heartbeat"""
        # TODO: STUDENT MUST IMPLEMENT
        # Update heartbeats[instance_id] with current time
        
        with self.lock:
            # Your code here...
            pass
    
    def _cleanup_stale(self):
        """Remove stale instances that haven't sent heartbeats"""
        while True:
            time.sleep(10)
            with self.lock:
                # TODO: STUDENT MUST IMPLEMENT
                # Remove instances where:
                # current_time - heartbeats[instance_id] > ttl
                
                # Your code here...
                pass

# ===================== TESTING FRAMEWORK =====================

class Tester:
    """Testing framework - PROVIDED"""
    
    def test_basic_functionality(self, client: SmartClient):
        """Test basic RPC functionality"""
        print("\n=== Testing Basic Functionality ===")
        
        test_cases = [
            ("sum", [1, 2, 3, 4, 5], 15),
            ("avg", [10, 20, 30], 20),
            ("min", [5, 2, 8, 1], 1),
            ("max", [5, 2, 8, 1], 8),
            ("multiply", [2, 3, 4], 24),
        ]
        
        passed = 0
        for operation, values, expected in test_cases:
            try:
                request = Request(
                    request_id=f"test_{operation}_{time.time()}",
                    method="Calculate",
                    operation=operation,
                    values=values,
                    deadline=time.time() + 5,
                    metadata={}
                )
                
                response = client.send_request(request)
                
                if response.status == StatusCode.OK and response.result == expected:
                    print(f"✓ {operation} test passed")
                    passed += 1
                else:
                    print(f"✗ {operation} test failed: got {response.result}, expected {expected}")
            except Exception as e:
                print(f"✗ {operation} test failed with error: {e}")
        
        print(f"Passed {passed}/{len(test_cases)} tests")
        return passed == len(test_cases)
    
    def test_load_balancing(self, client: SmartClient, num_requests: int = 100):
        """Test load distribution"""
        print(f"\n=== Testing Load Balancing ({num_requests} requests) ===")
        
        for i in range(num_requests):
            request = Request(
                request_id=f"lb_test_{i}",
                method="Calculate",
                operation="sum",
                values=[1, 2, 3],
                deadline=time.time() + 5,
                metadata={}
            )
            try:
                client.send_request(request)
            except:
                pass
        
        stats = client.load_balancer.get_stats()
        print(f"Strategy: {stats['strategy']}")
        print("Distribution:")
        for instance_id, instance_stats in stats['instances'].items():
            print(f"  {instance_id}: {instance_stats['requests']} requests "
                  f"({instance_stats['percentage']:.1f}%)")
    
    def test_fault_tolerance(self, instances: List[ServiceInstance], client: SmartClient):
        """Test resilience to failures"""
        print("\n=== Testing Fault Tolerance ===")
        
        # Inject failures
        if len(instances) > 0:
            instances[0].error_rate = 0.5
            print(f"Injected 50% error rate into {instances[0].instance_id}")
        
        # Send requests and measure success rate
        success = 0
        total = 50
        
        for i in range(total):
            request = Request(
                request_id=f"fault_test_{i}",
                method="Calculate",
                operation="sum",
                values=[1, 2],
                deadline=time.time() + 5,
                metadata={}
            )
            try:
                response = client.send_request(request)
                if response.status == StatusCode.OK:
                    success += 1
            except:
                pass
        
        success_rate = (success / total) * 100
        print(f"Success rate with failures: {success_rate:.1f}%")
        
        # Test circuit breaker by causing many failures
        if len(instances) > 0:
            instances[0].error_rate = 1.0
            print(f"\nInjected 100% error rate into {instances[0].instance_id}")
        
        # Circuit should open and reject quickly
        start = time.time()
        for i in range(10):
            try:
                request = Request(
                    request_id=f"cb_test_{i}",
                    method="Calculate",
                    operation="sum",
                    values=[1],
                    deadline=time.time() + 5,
                    metadata={}
                )
                client.send_request(request)
            except:
                pass
        
        elapsed = time.time() - start
        print(f"Time for 10 requests with circuit breaker: {elapsed:.2f}s")
        
        # Reset error rate
        if len(instances) > 0:
            instances[0].error_rate = 0.0

# ===================== MAIN EXECUTION =====================

def main():
    """Main execution function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python rpc_assignment.py [server|demo|test]")
        print("  server <port> - Start a service instance")
        print("  demo          - Run basic demonstration")
        print("  test          - Run test suite")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "server":
        # Start a single service instance
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 9000
        instance = ServiceInstance(f"instance_{port}", port)
        try:
            instance.start()
        except KeyboardInterrupt:
            print(f"\nShutting down instance on port {port}")
            instance.shutdown()
    
    elif mode == "demo":
        # Run a demonstration
        print("Starting microservices demo...")
        
        # Check if we should start local services or connect to remote
        use_local = all(host == 'localhost' for host, port in SERVICE_INSTANCES)
        
        instances = []
        
        if use_local:
            # Start local service instances
            print("Starting local service instances...")
            for i, (host, port) in enumerate(SERVICE_INSTANCES):
                instance = ServiceInstance(f"instance_{i}", port)
                thread = threading.Thread(target=instance.start, daemon=True)
                thread.start()
                instances.append(instance)
                time.sleep(0.1)
            
            print(f"Started {len(SERVICE_INSTANCES)} local service instances")
            time.sleep(1)
        else:
            # Connect to remote services
            print(f"Connecting to {len(SERVICE_INSTANCES)} remote service instances:")
            for host, port in SERVICE_INSTANCES:
                print(f"  - {host}:{port}")
        
        # Create load balancer and add instances from SERVICE_INSTANCES
        lb = LoadBalancer(LoadBalancingStrategy.ROUND_ROBIN)
        for i, (host, port) in enumerate(SERVICE_INSTANCES):
            info = InstanceInfo(
                instance_id=f"instance_{i}",
                host=host,
                port=port
            )
            lb.add_instance(info)
        
        # Create smart client
        client = SmartClient(lb)
        
        # Run some tests
        tester = Tester()
        tester.test_basic_functionality(client)
        tester.test_load_balancing(client, 30)
        
        # Show statistics
        print("\n=== Final Statistics ===")
        stats = lb.get_stats()
        print(json.dumps(stats, indent=2))
        
        # Cleanup local instances if any
        for instance in instances:
            instance.shutdown()
    
    elif mode == "test":
        # Run full test suite
        print("Running comprehensive test suite...")
        
        # Check if we should start local services or connect to remote
        use_local = all(host == 'localhost' for host, port in SERVICE_INSTANCES)
        
        instances = []
        
        if use_local:
            # Start local service instances
            print("Starting local service instances for testing...")
            for i, (host, port) in enumerate(SERVICE_INSTANCES):
                instance = ServiceInstance(f"test_instance_{i}", port)
                thread = threading.Thread(target=instance.start, daemon=True)
                thread.start()
                instances.append(instance)
                time.sleep(0.1)
            
            print(f"Started {len(SERVICE_INSTANCES)} local service instances")
            time.sleep(1)
        else:
            # Connect to remote services
            print(f"Testing with {len(SERVICE_INSTANCES)} remote service instances:")
            for host, port in SERVICE_INSTANCES:
                print(f"  - {host}:{port}")
            print("Make sure these services are running!")
            time.sleep(2)
        
        # Test different strategies
        strategies = [
            LoadBalancingStrategy.ROUND_ROBIN,
            LoadBalancingStrategy.LEAST_CONNECTIONS,
            LoadBalancingStrategy.RANDOM
        ]
        
        tester = Tester()
        
        for strategy in strategies:
            print(f"\n{'='*50}")
            print(f"Testing with {strategy.value} strategy")
            print('='*50)
            
            # Create load balancer with strategy using SERVICE_INSTANCES
            lb = LoadBalancer(strategy)
            for i, (host, port) in enumerate(SERVICE_INSTANCES):
                info = InstanceInfo(
                    instance_id=f"instance_{i}",
                    host=host,
                    port=port
                )
                lb.add_instance(info)
            
            # Create client
            client = SmartClient(lb)
            
            # Run tests
            tester.test_basic_functionality(client)
            tester.test_load_balancing(client, 100)
            
            # Only run fault tolerance test with local instances
            if use_local and instances:
                tester.test_fault_tolerance(instances, client)
            else:
                print("\n=== Skipping Fault Tolerance Test (remote instances) ===")
        
        # Cleanup local instances if any
        for instance in instances:
            instance.shutdown()
        
        print("\n" + "="*50)
        print("All tests completed!")
    
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()