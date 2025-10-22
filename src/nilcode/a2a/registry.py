"""
A2A External Agent Registry

This module discovers and manages external agents available via the A2A protocol.
It fetches agent cards to understand capabilities and maintains a registry of
available external agents.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import httpx
from a2a.client import A2ACardResolver
from a2a.types import AgentCard
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH, EXTENDED_AGENT_CARD_PATH


logger = logging.getLogger(__name__)


@dataclass
class ExternalAgent:
    """Represents a discovered external agent."""
    name: str
    base_url: str
    description: str
    capabilities: List[str]
    agent_card: AgentCard
    supports_extended_card: bool
    auth_required: bool = False
    auth_token: Optional[str] = None


class A2AAgentRegistry:
    """
    Registry for discovering and managing external A2A agents.

    This class handles:
    - Discovering agents from configured endpoints
    - Fetching and parsing agent cards (both public and extended)
    - Maintaining a registry of available external agents
    - Providing agent metadata for task planning
    """

    def __init__(self, httpx_client: Optional[httpx.AsyncClient] = None):
        """
        Initialize the A2A agent registry.

        Args:
            httpx_client: Optional HTTP client for making requests
        """
        self.httpx_client = httpx_client
        self.external_client_owned = httpx_client is None
        self.registry: Dict[str, ExternalAgent] = {}

    async def __aenter__(self):
        """Async context manager entry."""
        if self.external_client_owned:
            self.httpx_client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.external_client_owned and self.httpx_client:
            await self.httpx_client.aclose()

    async def discover_agent(
        self,
        agent_name: str,
        base_url: str,
        auth_token: Optional[str] = None
    ) -> Optional[ExternalAgent]:
        """
        Discover an agent from a base URL by fetching its agent card.

        Args:
            agent_name: Friendly name for the agent
            base_url: Base URL of the agent server
            auth_token: Optional authentication token for extended card

        Returns:
            ExternalAgent if discovered successfully, None otherwise
        """
        logger.info(f"Discovering agent '{agent_name}' at {base_url}")

        try:
            resolver = A2ACardResolver(
                httpx_client=self.httpx_client,
                base_url=base_url,
            )

            # Fetch public agent card
            logger.debug(f"Fetching public agent card from {base_url}{AGENT_CARD_WELL_KNOWN_PATH}")
            public_card = await resolver.get_agent_card()

            final_card = public_card
            supports_extended = public_card.supports_authenticated_extended_card or False

            # Try to fetch extended card if supported and auth token provided
            if supports_extended and auth_token:
                try:
                    logger.debug(f"Fetching extended agent card from {base_url}{EXTENDED_AGENT_CARD_PATH}")
                    auth_headers = {"Authorization": f"Bearer {auth_token}"}
                    extended_card = await resolver.get_agent_card(
                        relative_card_path=EXTENDED_AGENT_CARD_PATH,
                        http_kwargs={"headers": auth_headers}
                    )
                    final_card = extended_card
                    logger.info(f"Using extended agent card for '{agent_name}'")
                except Exception as e:
                    logger.warning(f"Failed to fetch extended card for '{agent_name}': {e}")
                    logger.info(f"Falling back to public card for '{agent_name}'")

            # Extract capabilities from agent card
            capabilities = self._extract_capabilities(final_card)

            # Create external agent object
            external_agent = ExternalAgent(
                name=agent_name,
                base_url=base_url,
                description=final_card.description or "No description provided",
                capabilities=capabilities,
                agent_card=final_card,
                supports_extended_card=supports_extended,
                auth_required=bool(auth_token),
                auth_token=auth_token
            )

            # Add to registry
            self.registry[agent_name] = external_agent
            logger.info(f"Successfully registered agent '{agent_name}' with {len(capabilities)} capabilities")

            return external_agent

        except Exception as e:
            logger.error(f"Failed to discover agent '{agent_name}' at {base_url}: {e}", exc_info=True)
            return None

    def _extract_capabilities(self, agent_card: AgentCard) -> List[str]:
        """
        Extract capabilities from an agent card.

        Args:
            agent_card: The agent card to analyze

        Returns:
            List of capability strings
        """
        capabilities = []

        # Extract from description
        if agent_card.description:
            capabilities.append(agent_card.description)

        # Extract from skills if available
        if hasattr(agent_card, 'skills') and agent_card.skills:
            capabilities.extend(agent_card.skills)

        # Extract from metadata
        if hasattr(agent_card, 'metadata') and isinstance(agent_card.metadata, dict):
            if 'capabilities' in agent_card.metadata:
                caps = agent_card.metadata['capabilities']
                if isinstance(caps, list):
                    capabilities.extend(caps)

        return capabilities

    async def discover_multiple_agents(
        self,
        agent_configs: List[Dict[str, Any]]
    ) -> List[ExternalAgent]:
        """
        Discover multiple agents from a list of configurations.

        Args:
            agent_configs: List of agent configurations, each containing:
                - name: Agent name
                - base_url: Base URL
                - auth_token: Optional auth token

        Returns:
            List of successfully discovered ExternalAgent objects
        """
        discovered = []

        for config in agent_configs:
            agent = await self.discover_agent(
                agent_name=config.get('name'),
                base_url=config.get('base_url'),
                auth_token=config.get('auth_token')
            )
            if agent:
                discovered.append(agent)

        logger.info(f"Discovered {len(discovered)}/{len(agent_configs)} agents")
        return discovered

    def get_agent(self, name: str) -> Optional[ExternalAgent]:
        """
        Get an agent from the registry by name.

        Args:
            name: Agent name

        Returns:
            ExternalAgent if found, None otherwise
        """
        return self.registry.get(name)

    def list_agents(self) -> List[ExternalAgent]:
        """
        List all registered agents.

        Returns:
            List of all ExternalAgent objects in registry
        """
        return list(self.registry.values())

    def get_agent_summary(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of an agent's capabilities for task planning.

        Args:
            name: Agent name

        Returns:
            Dictionary with agent summary or None
        """
        agent = self.get_agent(name)
        if not agent:
            return None

        return {
            "name": agent.name,
            "description": agent.description,
            "capabilities": agent.capabilities,
            "base_url": agent.base_url,
            "supports_extended_card": agent.supports_extended_card,
            "auth_required": agent.auth_required
        }

    def get_all_agent_summaries(self) -> List[Dict[str, Any]]:
        """
        Get summaries of all registered agents.

        Returns:
            List of agent summaries
        """
        return [self.get_agent_summary(name) for name in self.registry.keys()]


# Global registry instance (will be initialized with agents)
_global_registry: Optional[A2AAgentRegistry] = None


async def get_global_registry() -> A2AAgentRegistry:
    """
    Get or create the global agent registry.

    Returns:
        Global A2AAgentRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = A2AAgentRegistry()
    return _global_registry


async def initialize_registry_from_config(config_path: Optional[str] = None) -> A2AAgentRegistry:
    """
    Initialize the global registry from a configuration file.

    Args:
        config_path: Path to configuration file (JSON or YAML)

    Returns:
        Initialized A2AAgentRegistry
    """
    import json
    import os

    global _global_registry

    # Create new registry
    async with A2AAgentRegistry() as registry:
        # Priority 1: Use provided config_path
        if config_path and os.path.exists(config_path):
            logger.info(f"Loading A2A agents from config file: {config_path}")
            with open(config_path, 'r') as f:
                config = json.load(f)

            agents_config = config.get('external_agents', [])
            await registry.discover_multiple_agents(agents_config)
        else:
            # Priority 2: Check A2A_CONFIG_PATH environment variable
            env_config_path = os.getenv('A2A_CONFIG_PATH')
            if env_config_path and os.path.exists(env_config_path):
                logger.info(f"Loading A2A agents from A2A_CONFIG_PATH: {env_config_path}")
                with open(env_config_path, 'r') as f:
                    config = json.load(f)

                agents_config = config.get('external_agents', [])
                await registry.discover_multiple_agents(agents_config)
            else:
                # Priority 3: Load from A2A_AGENTS environment variable
                # Example: A2A_AGENTS='[{"name":"agent1","base_url":"http://localhost:9999"}]'
                agents_env = os.getenv('A2A_AGENTS')
                if agents_env:
                    try:
                        logger.info("Loading A2A agents from A2A_AGENTS environment variable")
                        agents_config = json.loads(agents_env)
                        await registry.discover_multiple_agents(agents_config)
                    except Exception as e:
                        logger.error(f"Failed to parse A2A_AGENTS environment variable: {e}")
                else:
                    logger.info("No A2A agent configuration found")

        _global_registry = registry
        return registry
