import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.data_models import AgentMessage


class MessageBus:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self._agents: Dict[str, Any] = {}  # agent_name -> agent_instance
        self._subscribers: Dict[str, List[str]] = defaultdict(list)  # message_type -> [agent_names]
        self._message_handlers: Dict[str, Callable] = {}
        self._message_queue = asyncio.Queue()
        self._running = False
        self._dispatcher_task = None
        
        # Message routing and filtering
        self._routing_rules: Dict[str, List[Callable]] = defaultdict(list)
        
        # Performance metrics
        self._message_stats = {
            "total_sent": 0,
            "total_delivered": 0,
            "total_failed": 0,
            "total_dropped": 0
        }
        
        self.logger.info("Message bus initialized")

    async def start(self):
        if self._running:
            self.logger.warning("Message bus is already running")
            return
            
        self._running = True
        self._dispatcher_task = asyncio.create_task(self._message_dispatcher())
        self.logger.info("Message bus started")

    async def stop(self):
        if not self._running:
            return
            
        self._running = False
        if self._dispatcher_task:
            self._dispatcher_task.cancel()
            try:
                await self._dispatcher_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Message bus stopped")

    def register_agent(self, agent_name: str, agent_instance):
        self._agents[agent_name] = agent_instance
        self.logger.info(f"Registered agent: {agent_name}")

    def unregister_agent(self, agent_name: str):
        if agent_name in self._agents:
            del self._agents[agent_name]
            # Remove from all subscriptions
            for message_type, subscribers in self._subscribers.items():
                if agent_name in subscribers:
                    subscribers.remove(agent_name)
            self.logger.info(f"Unregistered agent: {agent_name}")

    def subscribe(self, agent_name: str, message_type: str):
        if agent_name not in self._agents:
            self.logger.warning(f"Cannot subscribe unknown agent {agent_name}")
            return
            
        if agent_name not in self._subscribers[message_type]:
            self._subscribers[message_type].append(agent_name)
            self.logger.debug(f"Agent {agent_name} subscribed to {message_type}")

    def unsubscribe(self, agent_name: str, message_type: str):
        if agent_name in self._subscribers[message_type]:
            self._subscribers[message_type].remove(agent_name)
            self.logger.debug(f"Agent {agent_name} unsubscribed from {message_type}")

    def add_routing_rule(self, message_type: str, rule_func: Callable[[AgentMessage], bool]):
        self._routing_rules[message_type].append(rule_func)
        self.logger.debug(f"Added routing rule for {message_type}")

    async def send_message(self, message: AgentMessage):
        self._message_stats["total_sent"] += 1
        await self._message_queue.put(message)
        self.logger.debug(f"Queued message {message.message_id} from {message.sender}")

    async def broadcast_message(self, sender: str, message_type: str, payload: Dict[str, Any]):
        message = AgentMessage(
            sender=sender,
            recipient="*",  # Broadcast indicator
            message_type=message_type,
            payload=payload
        )
        await self.send_message(message)

    async def _message_dispatcher(self):
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self._message_queue.get(), timeout=1.0
                )
                await self._route_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error in message dispatcher: {e}")

    async def _route_message(self, message: AgentMessage):
        try:
            if message.recipient == "*":
                # Broadcast to all subscribers of this message type
                await self._broadcast_to_subscribers(message)
            elif message.recipient in self._agents:
                # Direct message to specific agent
                await self._deliver_message(message.recipient, message)
            else:
                self.logger.warning(f"Unknown recipient: {message.recipient}")
                self._message_stats["total_dropped"] += 1
        except Exception as e:
            self.logger.error(f"Error routing message {message.message_id}: {e}")
            self._message_stats["total_failed"] += 1

    async def _broadcast_to_subscribers(self, message: AgentMessage):
        subscribers = self._subscribers.get(message.message_type, [])
        if not subscribers:
            self.logger.debug(f"No subscribers for message type: {message.message_type}")
            self._message_stats["total_dropped"] += 1
            return

        # Apply routing rules
        filtered_subscribers = self._apply_routing_rules(message, subscribers)
        
        # Deliver to all filtered subscribers
        delivery_tasks = []
        for subscriber in filtered_subscribers:
            task = asyncio.create_task(self._deliver_message(subscriber, message))
            delivery_tasks.append(task)
        
        if delivery_tasks:
            await asyncio.gather(*delivery_tasks, return_exceptions=True)

    def _apply_routing_rules(self, message: AgentMessage, subscribers: List[str]) -> List[str]:
        if message.message_type not in self._routing_rules:
            return subscribers
        
        filtered_subscribers = []
        for subscriber in subscribers:
            should_deliver = True
            for rule in self._routing_rules[message.message_type]:
                try:
                    if not rule(message):
                        should_deliver = False
                        break
                except Exception as e:
                    self.logger.error(f"Error applying routing rule: {e}")
                    should_deliver = False
                    break
            
            if should_deliver:
                filtered_subscribers.append(subscriber)
        
        return filtered_subscribers

    async def _deliver_message(self, recipient: str, message: AgentMessage):
        try:
            if recipient not in self._agents:
                self.logger.warning(f"Cannot deliver to unknown agent: {recipient}")
                self._message_stats["total_dropped"] += 1
                return
                
            agent = self._agents[recipient]
            await agent.receive_message(message)
            self._message_stats["total_delivered"] += 1
            
            self.logger.debug(
                f"Delivered message {message.message_id} to {recipient}"
            )
            
        except Exception as e:
            self.logger.error(
                f"Failed to deliver message {message.message_id} to {recipient}: {e}"
            )
            self._message_stats["total_failed"] += 1

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "message_stats": self._message_stats.copy(),
            "registered_agents": list(self._agents.keys()),
            "subscriptions": dict(self._subscribers),
            "queue_size": self._message_queue.qsize(),
            "is_running": self._running
        }

    def get_agent_names(self) -> List[str]:
        return list(self._agents.keys())

    async def ping_agent(self, agent_name: str) -> bool:
        if agent_name not in self._agents:
            return False
            
        try:
            agent = self._agents[agent_name]
            health = await agent.health_check()
            return health.get("status") == "healthy"
        except Exception as e:
            self.logger.error(f"Error pinging agent {agent_name}: {e}")
            return False

    async def shutdown_all_agents(self):
        shutdown_tasks = []
        for agent_name, agent in self._agents.items():
            self.logger.info(f"Shutting down agent: {agent_name}")
            task = asyncio.create_task(agent.stop())
            shutdown_tasks.append(task)
        
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        self._agents.clear()
        self._subscribers.clear()
        self.logger.info("All agents shut down")


class MessageFilter:
    @staticmethod
    def priority_filter(min_priority: int):
        def filter_func(message: AgentMessage) -> bool:
            priority = message.payload.get("priority", 0)
            return priority >= min_priority
        return filter_func

    @staticmethod
    def symbol_filter(allowed_symbols: List[str]):
        def filter_func(message: AgentMessage) -> bool:
            symbols = message.payload.get("symbols", [])
            return any(symbol in allowed_symbols for symbol in symbols)
        return filter_func

    @staticmethod
    def time_window_filter(start_time: datetime, end_time: datetime):
        def filter_func(message: AgentMessage) -> bool:
            return start_time <= message.timestamp <= end_time
        return filter_func