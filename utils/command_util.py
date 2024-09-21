from functools import wraps
from botpy.message import BaseMessage


class Commands:
    """
    指令装饰器

    Args:
      args (tuple): 字符串元组。
    """

    def __init__(self, *args):
        self.commands = args

    def __call__(self, func):
        @wraps(func)
        async def decorated(*args, **kwargs):
            message: BaseMessage = kwargs["message"]
            params = message.content.split()
            for command in self.commands:
                if len(params) > 0 and f"/{command}" == params[0]:
                    params = params[1:] if len(params) > 1 else None
                    kwargs["params"] = params
                    return await func(*args, **kwargs)
            return False

        return decorated
