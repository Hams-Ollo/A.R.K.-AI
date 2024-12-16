"""
Enhanced CLI logger with emojis and styled output for ARK AI.
"""

import logging
from datetime import datetime
from typing import Any, Optional
import sys
from rich.console import Console
from rich.theme import Theme
from rich.logging import RichHandler
from rich.style import Style

# Create Rich console with custom theme
console = Console(theme=Theme({
    'info': 'cyan',
    'warning': 'yellow',
    'error': 'red',
    'success': 'green',
    'debug': 'blue'
}))

class CliLogger:
    """Enhanced CLI logger with emojis and styled output."""
    
    # Emoji mappings for different contexts
    EMOJI_MAP = {
        # System states
        'startup': '🚀',
        'shutdown': '🛑',
        'ready': '✨',
        'loading': '⌛',
        'done': '✅',
        'error': '❌',
        'warning': '⚠️',
        
        # AI and ML
        'ai_thinking': '🤔',
        'ai_response': '🤖',
        'model_loaded': '🧠',
        'processing': '⚡',
        
        # Data operations
        'database': '🗄️',
        'search': '🔍',
        'document': '📄',
        'upload': '📤',
        'download': '📥',
        'cache': '💾',
        
        # User interaction
        'user_input': '👤',
        'chat': '💬',
        'notification': '🔔',
        
        # Performance
        'performance': '📊',
        'memory': '💻',
        'time': '⏱️',
        'optimization': '🔧'
    }
    
    @classmethod
    def style_message(cls, message: str, context: str, details: Optional[dict] = None) -> str:
        """Style a message with emoji and optional details."""
        emoji = cls.EMOJI_MAP.get(context, '🔹')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        styled_msg = f"[{timestamp}] {emoji} {message}"
        
        if details:
            details_str = ' '.join([f"[bold]{k}:[/bold] {v}" for k, v in details.items()])
            styled_msg += f"\n       ├─ {details_str}"
            
        return styled_msg

    @classmethod
    def info(cls, message: str, context: str = 'info', **kwargs):
        """Log an info message with style."""
        styled_msg = cls.style_message(message, context, kwargs)
        console.print(styled_msg, style='info')

    @classmethod
    def success(cls, message: str, context: str = 'done', **kwargs):
        """Log a success message with style."""
        styled_msg = cls.style_message(message, context, kwargs)
        console.print(styled_msg, style='success')

    @classmethod
    def warning(cls, message: str, context: str = 'warning', **kwargs):
        """Log a warning message with style."""
        styled_msg = cls.style_message(message, context, kwargs)
        console.print(styled_msg, style='warning')

    @classmethod
    def error(cls, message: str, context: str = 'error', **kwargs):
        """Log an error message with style."""
        styled_msg = cls.style_message(message, context, kwargs)
        console.print(styled_msg, style='error')

    @classmethod
    def debug(cls, message: str, context: str = 'debug', **kwargs):
        """Log a debug message with style."""
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            styled_msg = cls.style_message(message, context, kwargs)
            console.print(styled_msg, style='debug')

    @classmethod
    def performance(cls, function_name: str, execution_time: float, **kwargs):
        """Log performance metrics with style."""
        details = {
            'time': f"{execution_time:.3f}s",
            **kwargs
        }
        styled_msg = cls.style_message(
            f"Performance metrics for {function_name}",
            'performance',
            details
        )
        console.print(styled_msg, style='info')

    @classmethod
    def ai_event(cls, event_type: str, message: str, **kwargs):
        """Log AI-related events with appropriate styling."""
        context_map = {
            'thinking': 'ai_thinking',
            'response': 'ai_response',
            'model': 'model_loaded',
            'processing': 'processing'
        }
        context = context_map.get(event_type, 'ai_response')
        styled_msg = cls.style_message(message, context, kwargs)
        console.print(styled_msg, style='info')

    @classmethod
    def data_event(cls, event_type: str, message: str, **kwargs):
        """Log data-related events with appropriate styling."""
        context_map = {
            'search': 'search',
            'document': 'document',
            'upload': 'upload',
            'download': 'download',
            'cache': 'cache',
            'database': 'database'
        }
        context = context_map.get(event_type, 'database')
        styled_msg = cls.style_message(message, context, kwargs)
        console.print(styled_msg, style='info')
