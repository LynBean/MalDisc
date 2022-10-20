
from io import StringIO
import ast
import os
import sys
import textwrap

from discord.ext import commands
from discord.ext.commands import Cog, Context, hybrid_command
import discord

from .constants import *
from .requests import *

class Eval(Cog):

    def __init__(self, bot):
        self.bot = bot

    async def _Eval(self, context: Context, *, code: str) -> str:
        func_name = '_eval_expr'
        code = f'async def {func_name}():\n{code}'

        def insert_returns(body):
            if isinstance(body[-1], ast.Expr):
                body[-1] = ast.Return(body[-1].value)
                ast.fix_missing_locations(body[-1])

            if isinstance(body[-1], ast.If):
                insert_returns(body[-1].body)
                insert_returns(body[-1].orelse)

            if isinstance(body[-1], ast.With):
                insert_returns(body[-1].body)

        parsed = ast.parse(code)
        insert_returns(parsed.body[0].body)

        variables = {
            'bot': self.bot,
            'discord': discord,
            'commands': commands,
            'context': context,
            '__import__': __import__
        }

        exec(compile(
            parsed,
            filename = '<ast>',
            mode = 'exec'),
             variables)

        temp = sys.stdout
        string = StringIO()
        sys.stdout = string
        result = await eval(
            f'{func_name}()',
            variables)

        sys.stdout = temp

        if isinstance(result, list) == True:
            result = '\n'.join(result)
        if result == None:
            result = ''

        result = string.getvalue() + str(result)
        return result


    @hybrid_command(
        name = 'eval')
    async def Eval(self, context: Context, *, code: str):
        if code.lower().startswith(prefix := '```python') == True: pass
        elif code.lower().startswith(prefix := '```py') == True: pass
        elif code.lower().startswith(prefix := '```') == True: pass
        elif code.lower().startswith(prefix := '`') == True: pass
        else:
            raise commands.BadArgument('Please provide the entered text as a valid code block, type '\
                f'`{self.bot.config.read(list, "BOT", "prefixes")[0]} help eval` for more info')

        code = code[len(prefix):].rstrip('```')
        code = '\n'.join(f'    {i}'
                         for i in code.splitlines())

        result = await self._Eval(context, code = code)

        def build_message() -> str:
            nonlocal code, result
            code = str(code).strip()
            result = str(result).strip()
            uname = os.uname()
            content = textwrap.dedent('```Python\n' \
                f'Python {sys.version} on {uname[0]} {uname[1]} {uname[2]}\n\n' \
                f'<<< {code}\n\n' \
                f'>>> {result}')

            return content[:1997] + '```'

        await context.reply(
            mention_author = False,
            content = build_message())

        return


async def setup(bot):
    await bot.add_cog(
        Eval(bot))
