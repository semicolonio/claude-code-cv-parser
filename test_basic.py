#!/usr/bin/env python3
"""Test basic Claude Code SDK functionality."""

import anyio
from claude_code_sdk import query, AssistantMessage, TextBlock


async def test_basic():
    """Test basic functionality."""
    print("Testing basic Claude Code SDK...")
    
    async for message in query(prompt="What is 2 + 2?"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Response: {block.text}")


if __name__ == "__main__":
    anyio.run(test_basic)