#!/usr/bin/env python3

""" async basics """

import asyncio
import random


async def wait_random(max_delay: int = 10) -> float:
    """ wait for a random delay and eventually return it """
    delay = random.uniform(0, max_delay)
    await asyncio.sleep(delay)
    return delay

""" event loop """
asyncio.run(wait_random())
