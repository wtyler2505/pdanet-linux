#!/usr/bin/env python3
"""
ConnectionOptimizer - Reinforcement Learning-based Network Connection Optimization

Implements PPO (Proximal Policy Optimization) agent for adaptive network routing,
bandwidth allocation, and connection management with continuous learning.
"""

import asyncio
import logging
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
from collections import deque, namedtuple
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

from ..utils.config import Config
from ..utils.network_utils import NetworkUtils
from ..data.storage import RewardStorage

logger = logging.getLogger(__name__)

# Experience tuple for RL
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])

@dataclass
class NetworkEnvironmentState:
    """Represents the current network environment state"""
    bandwidth_utilization: float
    connection_count: int
    latency: float
    packet_loss: float
    jitter: float
    cpu_usage: float
    memory_usage: float
    active_routes: int
    congestion_level: float
    time_of_day: float
    
    def to_tensor(self) -> torch.Tensor:
        """Convert state to tensor for RL processing"""
        state_vector = [
            self.bandwidth_utilization,
            self.connection_count / 1000.0,  # Normalize
            self.latency / 1000.0,  # Normalize to 0-1 range
            self.packet_loss,
            self.jitter / 100.0,
            self.cpu_usage,
            self.memory_usage,
            self.active_routes / 10.0,
            self.congestion_level,
            self.time_of_day,
        ]
        return torch.FloatTensor(state_vector)

@dataclass
class OptimizationAction:
    """Represents an optimization action taken by the RL agent"""
    bandwidth_reallocation: float  # -1 to 1
    route_change: int             # 0-3 (no change, primary, secondary, load balance)
    qos_adjustment: float         # -1 to 1
    connection_limit: float       # 0-1
    compression_level: float      # 0-1
    
    @classmethod
    def from_action_vector(cls, action_vector: torch.Tensor):
        """Create action from RL agent output"""
        actions = action_vector.numpy() if hasattr(action_vector, 'numpy') else action_vector
        
        return cls(
            bandwidth_reallocation=float(actions[0]),
            route_change=int(actions[1]),
            qos_adjustment=float(actions[2]),
            connection_limit=float(actions[3]),
            compression_level=float(actions[4])
        )

class PPOActorCritic(nn.Module):
    """PPO Actor-Critic network for connection optimization"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        
        # Shared feature extractor
        self.feature_extractor = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        
        # Actor network (policy)
        self.actor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, action_dim),
        )
        
        # Critic network (value function)
        self.critic = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
        )
        
    def forward(self, state):
        features = self.feature_extractor(state)
        return self.actor(features), self.critic(features)
    
    def get_action(self, state, deterministic=False):
        """Get action from current policy"""
        with torch.no_grad():
            action_logits, value = self.forward(state)
            
            if deterministic:
                # Take the most likely action
                action = torch.argmax(action_logits, dim=-1)
                log_prob = torch.log_softmax(action_logits, dim=-1)[action]
            else:
                # Sample from the policy distribution
                dist = Categorical(logits=action_logits)
                action = dist.sample()
                log_prob = dist.log_prob(action)
            
            return action, log_prob, value
    
    def evaluate_actions(self, states, actions):
        """Evaluate actions for PPO training"""
        action_logits, values = self.forward(states)
        dist = Categorical(logits=action_logits)
        
        action_log_probs = dist.log_prob(actions)
        entropy = dist.entropy()
        
        return action_log_probs, values.squeeze(), entropy

class PPOAgent:
    """PPO agent for network optimization"""
    
    def __init__(self, state_dim: int, action_dim: int, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Network parameters
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # PPO hyperparameters
        self.lr = config.get('ppo_lr', 3e-4)
        self.gamma = config.get('ppo_gamma', 0.99)
        self.eps_clip = config.get('ppo_eps_clip', 0.2)
        self.k_epochs = config.get('ppo_k_epochs', 4)
        self.entropy_coef = config.get('ppo_entropy_coef', 0.01)
        self.value_coef = config.get('ppo_value_coef', 0.5)
        
        # Networks
        self.policy = PPOActorCritic(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=self.lr)
        
        # Experience storage
        self.memory = deque(maxlen=config.get('ppo_memory_size', 10000))
        self.batch_size = config.get('ppo_batch_size', 64)
        
        # Performance tracking
        self.episode_rewards = deque(maxlen=1000)
        self.training_step = 0
        
    async def select_action(self, state_vector: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Select action using current policy"""
        state = state_vector.unsqueeze(0).to(self.device)
        action, log_prob, value = self.policy.get_action(state)
        
        return action.squeeze(), log_prob.squeeze(), value.squeeze()
    
    def store_experience(self, state: torch.Tensor, action: torch.Tensor, 
                        reward: float, next_state: torch.Tensor, done: bool):
        """Store experience for later training"""
        experience = Experience(state, action, reward, next_state, done)
        self.memory.append(experience)
    
    async def update(self, state_vector: torch.Tensor, action: torch.Tensor, reward: float):
        """Update policy based on reward feedback"""
        # Store immediate experience
        self.store_experience(
            state_vector, action, reward, 
            state_vector, False  # Simplified - in practice, would use next state
        )
        
        # Train if we have enough experiences
        if len(self.memory) >= self.batch_size:
            await self._train_policy()
    
    async def _train_policy(self):
        """Train the PPO policy"""
        if len(self.memory) < self.batch_size:
            return
        
        # Sample batch from memory
        batch_indices = np.random.choice(len(self.memory), self.batch_size, replace=False)
        batch = [self.memory[i] for i in batch_indices]
        
        # Extract batch components
        states = torch.stack([exp.state for exp in batch]).to(self.device)
        actions = torch.stack([exp.action for exp in batch]).to(self.device)
        rewards = torch.tensor([exp.reward for exp in batch], dtype=torch.float32).to(self.device)
        next_states = torch.stack([exp.next_state for exp in batch]).to(self.device)
        dones = torch.tensor([exp.done for exp in batch], dtype=torch.float32).to(self.device)
        
        # Calculate advantages and returns
        with torch.no_grad():
            _, values, _ = self.policy.get_action(states)
            _, next_values, _ = self.policy.get_action(next_states)
            
            returns = rewards + self.gamma * next_values * (1 - dones)
            advantages = returns - values
            
            # Normalize advantages
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Get old policy probabilities
        with torch.no_grad():
            _, old_log_probs, _ = self.policy.get_action(states)
        
        # PPO training loop
        for _ in range(self.k_epochs):
            # Forward pass
            log_probs, state_values, entropy = self.policy.evaluate_actions(states, actions)
            
            # Calculate ratios
            ratios = torch.exp(log_probs - old_log_probs)
            
            # Calculate surrogate losses
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1 - self.eps_clip, 1 + self.eps_clip) * advantages
            
            # PPO loss
            actor_loss = -torch.min(surr1, surr2).mean()
            critic_loss = nn.MSELoss()(state_values, returns)
            entropy_loss = -entropy.mean()
            
            total_loss = (
                actor_loss + 
                self.value_coef * critic_loss + 
                self.entropy_coef * entropy_loss
            )
            
            # Backward pass
            self.optimizer.zero_grad()
            total_loss.backward()
            nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
            self.optimizer.step()
        
        self.training_step += 1
        
        if self.training_step % 100 == 0:
            self.logger.info(
                f"PPO training step {self.training_step}, "
                f"loss: {total_loss.item():.4f}, "
                f"avg_reward: {np.mean(list(self.episode_rewards)) if self.episode_rewards else 0:.2f}"
            )
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get agent performance metrics"""
        if not self.episode_rewards:
            return {'avg_reward': 0.0, 'episodes': 0}
        
        return {
            'avg_reward': np.mean(list(self.episode_rewards)),
            'episodes': len(self.episode_rewards),
            'training_steps': self.training_step,
            'memory_size': len(self.memory),
        }

class RewardCalculator:
    """Calculates rewards for RL agent based on network performance"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Reward weights
        self.bandwidth_weight = config.get('reward_bandwidth_weight', 0.3)
        self.latency_weight = config.get('reward_latency_weight', 0.3)
        self.stability_weight = config.get('reward_stability_weight', 0.2)
        self.efficiency_weight = config.get('reward_efficiency_weight', 0.2)
        
    async def compute(self, previous_state: NetworkEnvironmentState, 
                     action: OptimizationAction, 
                     new_state: NetworkEnvironmentState) -> float:
        """Compute reward based on state transition"""
        
        reward = 0.0
        
        # Bandwidth utilization reward
        bandwidth_improvement = self._calculate_bandwidth_reward(
            previous_state.bandwidth_utilization, 
            new_state.bandwidth_utilization
        )
        reward += self.bandwidth_weight * bandwidth_improvement
        
        # Latency improvement reward
        latency_improvement = self._calculate_latency_reward(
            previous_state.latency, 
            new_state.latency
        )
        reward += self.latency_weight * latency_improvement
        
        # Network stability reward
        stability_reward = self._calculate_stability_reward(
            previous_state, new_state
        )
        reward += self.stability_weight * stability_reward
        
        # Resource efficiency reward
        efficiency_reward = self._calculate_efficiency_reward(
            previous_state, new_state
        )
        reward += self.efficiency_weight * efficiency_reward
        
        # Penalty for extreme actions
        action_penalty = self._calculate_action_penalty(action)
        reward -= action_penalty
        
        # Normalize reward to [-1, 1] range
        reward = np.tanh(reward)
        
        self.logger.debug(
            f"Reward calculation: bandwidth={bandwidth_improvement:.3f}, "
            f"latency={latency_improvement:.3f}, stability={stability_reward:.3f}, "
            f"efficiency={efficiency_reward:.3f}, penalty={action_penalty:.3f}, "
            f"total={reward:.3f}"
        )
        
        return float(reward)
    
    def _calculate_bandwidth_reward(self, old_bw: float, new_bw: float) -> float:
        """Calculate reward based on bandwidth utilization improvement"""
        # Optimal utilization is around 70-80%
        optimal_utilization = 0.75
        
        old_distance = abs(old_bw - optimal_utilization)
        new_distance = abs(new_bw - optimal_utilization)
        
        # Positive reward for getting closer to optimal
        improvement = old_distance - new_distance
        return improvement * 2  # Scale the reward
    
    def _calculate_latency_reward(self, old_latency: float, new_latency: float) -> float:
        """Calculate reward based on latency improvement"""
        # Lower latency is better
        if old_latency == 0:
            return 0.0
        
        improvement = (old_latency - new_latency) / old_latency
        return improvement
    
    def _calculate_stability_reward(self, old_state: NetworkEnvironmentState, 
                                  new_state: NetworkEnvironmentState) -> float:
        """Calculate reward based on network stability"""
        # Stability is measured by consistency in packet loss and jitter
        packet_loss_stability = 1.0 - abs(old_state.packet_loss - new_state.packet_loss)
        jitter_stability = 1.0 - abs(old_state.jitter - new_state.jitter) / 100.0
        
        return (packet_loss_stability + jitter_stability) / 2 - 0.5  # Center around 0
    
    def _calculate_efficiency_reward(self, old_state: NetworkEnvironmentState, 
                                   new_state: NetworkEnvironmentState) -> float:
        """Calculate reward based on resource efficiency"""
        # Reward for lower resource usage with same or better performance
        cpu_improvement = old_state.cpu_usage - new_state.cpu_usage
        memory_improvement = old_state.memory_usage - new_state.memory_usage
        
        return (cpu_improvement + memory_improvement) / 2
    
    def _calculate_action_penalty(self, action: OptimizationAction) -> float:
        """Calculate penalty for extreme actions"""
        # Penalize extreme actions to encourage stability
        penalty = 0.0
        
        # Bandwidth reallocation penalty
        if abs(action.bandwidth_reallocation) > 0.8:
            penalty += 0.1 * abs(action.bandwidth_reallocation)
        
        # QoS adjustment penalty
        if abs(action.qos_adjustment) > 0.8:
            penalty += 0.05 * abs(action.qos_adjustment)
        
        return penalty

class NetworkEnvironment:
    """Network environment for RL agent interaction"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.network_utils = NetworkUtils()
        
        # Environment state
        self.current_state: Optional[NetworkEnvironmentState] = None
        self.state_history = deque(maxlen=100)
        
    async def get_current_state(self) -> NetworkEnvironmentState:
        """Get current network environment state"""
        try:
            # Collect network metrics
            metrics = await self.network_utils.collect_comprehensive_metrics()
            
            state = NetworkEnvironmentState(
                bandwidth_utilization=metrics.get('bandwidth_utilization', 0.0),
                connection_count=metrics.get('connection_count', 0),
                latency=metrics.get('avg_latency', 0.0),
                packet_loss=metrics.get('packet_loss_rate', 0.0),
                jitter=metrics.get('jitter', 0.0),
                cpu_usage=metrics.get('cpu_usage', 0.0),
                memory_usage=metrics.get('memory_usage', 0.0),
                active_routes=metrics.get('active_routes', 0),
                congestion_level=metrics.get('congestion_level', 0.0),
                time_of_day=datetime.now().hour / 24.0
            )
            
            self.current_state = state
            self.state_history.append(state)
            
            return state
            
        except Exception as e:
            self.logger.error(f"Failed to get environment state: {e}")
            # Return default state
            return NetworkEnvironmentState(
                bandwidth_utilization=0.5,
                connection_count=0,
                latency=100.0,
                packet_loss=0.0,
                jitter=0.0,
                cpu_usage=0.5,
                memory_usage=0.5,
                active_routes=1,
                congestion_level=0.0,
                time_of_day=datetime.now().hour / 24.0
            )
    
    async def apply_action(self, action: OptimizationAction) -> Dict[str, Any]:
        """Apply optimization action to the network environment"""
        try:
            results = {}
            
            # Apply bandwidth reallocation
            if abs(action.bandwidth_reallocation) > 0.1:
                bandwidth_result = await self.network_utils.adjust_bandwidth_allocation(
                    adjustment_factor=action.bandwidth_reallocation
                )
                results['bandwidth_adjustment'] = bandwidth_result
            
            # Apply route changes
            if action.route_change > 0:
                route_result = await self.network_utils.optimize_routing(
                    strategy=action.route_change
                )
                results['routing_change'] = route_result
            
            # Apply QoS adjustments
            if abs(action.qos_adjustment) > 0.1:
                qos_result = await self.network_utils.adjust_qos_parameters(
                    adjustment=action.qos_adjustment
                )
                results['qos_adjustment'] = qos_result
            
            # Apply connection limits
            if action.connection_limit != 0.5:  # 0.5 is neutral
                connection_result = await self.network_utils.set_connection_limits(
                    limit_factor=action.connection_limit
                )
                results['connection_limits'] = connection_result
            
            # Apply compression settings
            if abs(action.compression_level - 0.5) > 0.1:  # 0.5 is neutral
                compression_result = await self.network_utils.set_compression_level(
                    level=action.compression_level
                )
                results['compression'] = compression_result
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to apply action: {e}")
            return {'error': str(e)}
    
    def get_state_statistics(self) -> Dict[str, Any]:
        """Get statistics about the environment state history"""
        if not self.state_history:
            return {}
        
        states = list(self.state_history)
        
        return {
            'avg_bandwidth_utilization': np.mean([s.bandwidth_utilization for s in states]),
            'avg_latency': np.mean([s.latency for s in states]),
            'avg_packet_loss': np.mean([s.packet_loss for s in states]),
            'stability_score': 1.0 - np.std([s.bandwidth_utilization for s in states]),
            'samples': len(states),
        }

class ConnectionOptimizer:
    """Main connection optimizer with RL-based adaptive optimization"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # RL components
        self.rl_agent = PPOAgent(state_dim=10, action_dim=5, config=config)
        self.environment = NetworkEnvironment(config)
        self.reward_calculator = RewardCalculator(config)
        
        # Storage for learning
        self.reward_storage = RewardStorage(config)
        
        # Optimization state
        self.is_learning_enabled = config.get('enable_rl_learning', True)
        self.optimization_history = deque(maxlen=1000)
        
    async def initialize(self):
        """Initialize the connection optimizer"""
        self.logger.info("Initializing ConnectionOptimizer...")
        
        try:
            await self.reward_storage.initialize()
            self.logger.info("ConnectionOptimizer initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize ConnectionOptimizer: {e}")
            raise
    
    async def optimize_connection(self, network_state: Any) -> Dict[str, Any]:
        """Main optimization function using RL agent"""
        try:
            # Get current environment state
            env_state = await self.environment.get_current_state()
            state_tensor = env_state.to_tensor()
            
            # Get action from RL agent
            action_tensor, log_prob, value = await self.rl_agent.select_action(state_tensor)
            
            # Convert to optimization action
            # For simplicity, we'll use a discrete action space mapping
            action = self._tensor_to_action(action_tensor)
            
            # Apply optimization action
            previous_state = env_state
            application_result = await self.environment.apply_action(action)
            
            # Wait for changes to take effect
            await asyncio.sleep(2)
            
            # Get new state after action
            new_state = await self.environment.get_current_state()
            
            # Calculate reward for learning
            if self.is_learning_enabled:
                reward = await self.reward_calculator.compute(
                    previous_state=previous_state,
                    action=action,
                    new_state=new_state
                )
                
                # Update RL agent
                await self.rl_agent.update(state_tensor, action_tensor, reward)
                
                # Store reward for analysis
                await self.reward_storage.store_reward({
                    'timestamp': datetime.utcnow(),
                    'state': previous_state.__dict__,
                    'action': action.__dict__,
                    'reward': reward,
                    'new_state': new_state.__dict__,
                })
            
            # Record optimization
            optimization_record = {
                'timestamp': datetime.utcnow(),
                'previous_state': previous_state.__dict__,
                'action_taken': action.__dict__,
                'application_result': application_result,
                'new_state': new_state.__dict__,
                'reward': reward if self.is_learning_enabled else None,
                'confidence': float(torch.max(torch.softmax(action_tensor, dim=0)))
            }
            
            self.optimization_history.append(optimization_record)
            
            return {
                'success': True,
                'optimization_applied': True,
                'action': action.__dict__,
                'performance_change': self._calculate_performance_change(previous_state, new_state),
                'confidence': optimization_record['confidence'],
                'learning_enabled': self.is_learning_enabled,
            }
            
        except Exception as e:
            self.logger.error(f"Connection optimization failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'optimization_applied': False,
            }
    
    def _tensor_to_action(self, action_tensor: torch.Tensor) -> OptimizationAction:
        """Convert RL agent action tensor to optimization action"""
        # Simple mapping from discrete actions to continuous optimization parameters
        action_idx = int(action_tensor.item()) if action_tensor.dim() == 0 else int(torch.argmax(action_tensor).item())
        
        # Map discrete actions to optimization parameters
        action_mappings = {
            0: OptimizationAction(0.0, 0, 0.0, 0.5, 0.5),      # No change
            1: OptimizationAction(0.2, 1, 0.1, 0.6, 0.6),      # Increase bandwidth, improve QoS
            2: OptimizationAction(-0.2, 2, -0.1, 0.4, 0.4),    # Decrease bandwidth, reduce QoS
            3: OptimizationAction(0.1, 3, 0.2, 0.7, 0.8),      # Balance load, increase compression
            4: OptimizationAction(0.0, 1, 0.3, 0.5, 0.3),      # Focus on QoS improvement
        }
        
        return action_mappings.get(action_idx, action_mappings[0])
    
    def _calculate_performance_change(self, old_state: NetworkEnvironmentState, 
                                    new_state: NetworkEnvironmentState) -> Dict[str, float]:
        """Calculate performance changes between states"""
        changes = {}
        
        # Bandwidth utilization change
        if old_state.bandwidth_utilization > 0:
            changes['bandwidth_change'] = (
                (new_state.bandwidth_utilization - old_state.bandwidth_utilization) / 
                old_state.bandwidth_utilization * 100
            )
        
        # Latency change
        if old_state.latency > 0:
            changes['latency_change'] = (
                (old_state.latency - new_state.latency) / old_state.latency * 100
            )
        
        # Packet loss change
        changes['packet_loss_change'] = (
            (old_state.packet_loss - new_state.packet_loss) * 100
        )
        
        # Connection efficiency
        changes['connection_efficiency'] = (
            new_state.bandwidth_utilization / max(new_state.connection_count, 1) -
            old_state.bandwidth_utilization / max(old_state.connection_count, 1)
        ) * 100
        
        return changes
    
    async def optimize_routing(self, routing_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize routing based on RL recommendations"""
        try:
            # Get current state for context
            current_state = await self.environment.get_current_state()
            
            # Apply routing optimizations
            if routing_config.get('path_optimization', False):
                path_result = await self.environment.network_utils.optimize_path_selection()
            
            load_balancing = routing_config.get('load_balancing', 0.0)
            if load_balancing > 0.1:
                balance_result = await self.environment.network_utils.configure_load_balancing(
                    intensity=load_balancing
                )
            
            failover_threshold = routing_config.get('failover_threshold', 0.5)
            failover_result = await self.environment.network_utils.set_failover_threshold(
                threshold=failover_threshold
            )
            
            return {
                'routing_optimized': True,
                'path_optimization': routing_config.get('path_optimization', False),
                'load_balancing_level': load_balancing,
                'failover_threshold': failover_threshold,
            }
            
        except Exception as e:
            self.logger.error(f"Routing optimization failed: {e}")
            return {
                'routing_optimized': False,
                'error': str(e)
            }
    
    async def get_optimization_insights(self) -> Dict[str, Any]:
        """Get insights about optimization performance"""
        insights = {
            'rl_agent_performance': self.rl_agent.get_performance_metrics(),
            'environment_stats': self.environment.get_state_statistics(),
            'optimization_count': len(self.optimization_history),
            'learning_enabled': self.is_learning_enabled,
        }
        
        # Analyze recent optimizations
        if len(self.optimization_history) >= 10:
            recent_optimizations = list(self.optimization_history)[-10:]
            
            rewards = [opt['reward'] for opt in recent_optimizations if opt['reward'] is not None]
            if rewards:
                insights['recent_performance'] = {
                    'avg_reward': np.mean(rewards),
                    'reward_trend': 'improving' if len(rewards) > 1 and rewards[-1] > rewards[0] else 'stable',
                    'optimization_success_rate': sum(1 for opt in recent_optimizations if opt.get('success', False)) / len(recent_optimizations),
                }
        
        return insights
    
    def set_learning_enabled(self, enabled: bool):
        """Enable or disable RL learning"""
        self.is_learning_enabled = enabled
        self.logger.info(f"RL learning {'enabled' if enabled else 'disabled'}")