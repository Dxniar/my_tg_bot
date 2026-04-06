from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware


class ContextMiddleware(BaseMiddleware):
    def __init__(self, **context):
        self.context = context

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        data.update(self.context)
        return await handler(event, data)
