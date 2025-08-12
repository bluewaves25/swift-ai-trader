#!/usr/bin/env python3
"""
Load Balancer - Intelligent request routing and worker distribution
Implements load balancing for risk validation requests
Provides optimal resource utilization and scalability
"""

import asyncio
import time
import random
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class RequestPriority(Enum):
    """Request priority levels."""
    ULTRA_HIGH = 1    # HFT strategies (10-50ms)
    HIGH = 2          # Standard strategies (100-500ms)
    MEDIUM = 3        # Strategic strategies (1-5s)
    LOW = 4           # Background tasks (5s+)

@dataclass
class RiskRequest:
    """Risk validation request structure."""
    request_id: str
    strategy_type: str
    symbol: str
    priority: RequestPriority
    timestamp: float
    data: Dict[str, Any]
    timeout: float = 1.0  # Default 1 second timeout

class Worker:
    """Individual worker for processing risk requests."""
    
    def __init__(self, worker_id: int, max_queue_size: int = 1000):
        self.worker_id = worker_id
        self.max_queue_size = max_queue_size
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.is_running = False
        self.current_load = 0
        self.total_processed = 0
        self.total_failed = 0
        self.avg_processing_time = 0.0
        self.last_activity = time.time()
        
        # Performance metrics
        self.processing_times = []
        self.max_history = 1000
    
    async def start(self, processor_func: Callable):
        """Start the worker loop."""
        self.is_running = True
        while self.is_running:
            try:
                # Get request from queue with timeout
                try:
                    request = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process the request
                start_time = time.time()
                try:
                    result = await processor_func(request)
                    self.total_processed += 1
                    
                    # Update performance metrics
                    processing_time = time.time() - start_time
                    self._update_performance_metrics(processing_time)
                    
                except Exception as e:
                    self.total_failed += 1
                    print(f"Worker {self.worker_id} failed to process request: {e}")
                
                finally:
                    self.queue.task_done()
                    self.current_load = self.queue.qsize()
                    self.last_activity = time.time()
                    
            except Exception as e:
                print(f"Worker {self.worker_id} error: {e}")
                await asyncio.sleep(0.1)
    
    def _update_performance_metrics(self, processing_time: float):
        """Update worker performance metrics."""
        self.processing_times.append(processing_time)
        
        # Keep only recent history
        if len(self.processing_times) > self.max_history:
            self.processing_times = self.processing_times[-self.max_history:]
        
        # Calculate average processing time
        self.avg_processing_time = sum(self.processing_times) / len(self.processing_times)
    
    async def add_request(self, request: RiskRequest) -> bool:
        """Add request to worker queue."""
        if self.queue.qsize() >= self.max_queue_size:
            return False
        
        await self.queue.put(request)
        self.current_load = self.queue.qsize()
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""
        return {
            'worker_id': self.worker_id,
            'is_running': self.is_running,
            'current_load': self.current_load,
            'queue_size': self.queue.qsize(),
            'total_processed': self.total_processed,
            'total_failed': self.total_failed,
            'avg_processing_time': self.avg_processing_time,
            'last_activity': self.last_activity,
            'success_rate': self.total_processed / max(self.total_processed + self.total_failed, 1)
        }
    
    def stop(self):
        """Stop the worker."""
        self.is_running = False

class LoadBalancer:
    """Intelligent load balancer for risk validation requests."""
    
    def __init__(self, num_workers: int = 4, max_queue_size: int = 1000):
        self.num_workers = num_workers
        self.max_queue_size = max_queue_size
        self.workers: List[Worker] = []
        self.is_running = False
        
        # Routing strategies
        self.routing_strategies = {
            'round_robin': self._round_robin_routing,
            'least_loaded': self._least_loaded_routing,
            'fastest_worker': self._fastest_worker_routing,
            'priority_based': self._priority_based_routing
        }
        
        self.current_routing_strategy = 'priority_based'
        self.round_robin_index = 0
        
        # Performance tracking
        self.total_requests = 0
        self.successful_routes = 0
        self.failed_routes = 0
        self.routing_times = []
    
    async def start(self, processor_func: Callable):
        """Start the load balancer and all workers."""
        self.is_running = True
        
        # Create and start workers
        for i in range(self.num_workers):
            worker = Worker(i, self.max_queue_size)
            self.workers.append(worker)
            
            # Start worker in background
            asyncio.create_task(worker.start(processor_func))
        
        print(f"Load balancer started with {self.num_workers} workers")
    
    async def route_request(self, request: RiskRequest) -> bool:
        """Route a request to an appropriate worker."""
        if not self.is_running:
            return False
        
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # Select routing strategy based on request priority
            if request.priority == RequestPriority.ULTRA_HIGH:
                # For ultra-high priority, use fastest worker
                worker = self._fastest_worker_routing(request)
            else:
                # For other priorities, use configured strategy
                worker = self.routing_strategies[self.current_routing_strategy](request)
            
            if worker:
                # Try to add request to worker
                success = await worker.add_request(request)
                if success:
                    self.successful_routes += 1
                    
                    # Update routing performance metrics
                    routing_time = time.time() - start_time
                    self._update_routing_metrics(routing_time)
                    
                    return True
                else:
                    # Worker queue is full, try alternative routing
                    return await self._fallback_routing(request)
            else:
                self.failed_routes += 1
                return False
                
        except Exception as e:
            print(f"Load balancer routing error: {e}")
            self.failed_routes += 1
            return False
    
    def _round_robin_routing(self, request: RiskRequest) -> Optional[Worker]:
        """Round-robin routing strategy."""
        if not self.workers:
            return None
        
        worker = self.workers[self.round_robin_index]
        self.round_robin_index = (self.round_robin_index + 1) % len(self.workers)
        return worker
    
    def _least_loaded_routing(self, request: RiskRequest) -> Optional[Worker]:
        """Route to worker with least load."""
        if not self.workers:
            return None
        
        return min(self.workers, key=lambda w: w.current_load)
    
    def _fastest_worker_routing(self, request: RiskRequest) -> Optional[Worker]:
        """Route to fastest worker (lowest average processing time)."""
        if not self.workers:
            return None
        
        # Filter out workers with no processing history
        workers_with_history = [w for w in self.workers if w.avg_processing_time > 0]
        
        if not workers_with_history:
            return self._least_loaded_routing(request)
        
        return min(workers_with_history, key=lambda w: w.avg_processing_time)
    
    def _priority_based_routing(self, request: RiskRequest) -> Optional[Worker]:
        """Priority-based routing strategy."""
        if request.priority == RequestPriority.ULTRA_HIGH:
            # Ultra-high priority: fastest worker with low load
            return self._fastest_worker_routing(request)
        elif request.priority == RequestPriority.HIGH:
            # High priority: least loaded worker
            return self._least_loaded_routing(request)
        else:
            # Medium/Low priority: round-robin
            return self._round_robin_routing(request)
    
    async def _fallback_routing(self, request: RiskRequest) -> bool:
        """Fallback routing when primary routing fails."""
        # Try all workers with different strategies
        strategies = ['least_loaded', 'fastest_worker', 'round_robin']
        
        for strategy in strategies:
            worker = self.routing_strategies[strategy](request)
            if worker and await worker.add_request(request):
                return True
        
        return False
    
    def _update_routing_metrics(self, routing_time: float):
        """Update routing performance metrics."""
        self.routing_times.append(routing_time)
        
        # Keep only recent history
        if len(self.routing_times) > 1000:
            self.routing_times = self.routing_times[-1000:]
    
    def set_routing_strategy(self, strategy: str):
        """Set the routing strategy."""
        if strategy in self.routing_strategies:
            self.current_routing_strategy = strategy
        else:
            raise ValueError(f"Unknown routing strategy: {strategy}")
    
    def get_worker_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all workers."""
        return [worker.get_stats() for worker in self.workers]
    
    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics."""
        total_workers = len(self.workers)
        active_workers = sum(1 for w in self.workers if w.is_running)
        total_load = sum(w.current_load for w in self.workers)
        
        avg_routing_time = sum(self.routing_times) / max(len(self.routing_times), 1)
        
        return {
            'total_workers': total_workers,
            'active_workers': active_workers,
            'total_load': total_load,
            'avg_load_per_worker': total_load / max(total_workers, 1),
            'current_routing_strategy': self.current_routing_strategy,
            'total_requests': self.total_requests,
            'successful_routes': self.successful_routes,
            'failed_routes': self.failed_routes,
            'success_rate': self.successful_routes / max(self.total_requests, 1),
            'avg_routing_time': avg_routing_time,
            'timestamp': time.time()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of load balancer and workers."""
        worker_stats = self.get_worker_stats()
        lb_stats = self.get_load_balancer_stats()
        
        # Calculate overall health score
        worker_health_scores = [ws['success_rate'] for ws in worker_stats]
        avg_worker_health = sum(worker_health_scores) / max(len(worker_health_scores), 1)
        
        overall_health = (avg_worker_health + lb_stats['success_rate']) / 2
        
        return {
            'overall_health': overall_health,
            'load_balancer_health': lb_stats['success_rate'],
            'worker_health': avg_worker_health,
            'active_workers': lb_stats['active_workers'],
            'total_workers': lb_stats['total_workers'],
            'timestamp': time.time()
        }
    
    def stop(self):
        """Stop the load balancer and all workers."""
        self.is_running = False
        for worker in self.workers:
            worker.stop()
        print("Load balancer stopped")
