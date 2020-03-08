import asyncio
import unittest
from functools import partial
from unittest import mock

from bot.cogs.moderation.silence import FirstHash, Silence
from bot.constants import Emojis
from tests.helpers import MockBot, MockContext


class FirstHashTests(unittest.TestCase):
    def setUp(self) -> None:
        self.test_cases = (
            (FirstHash(0, 4), FirstHash(0, 5)),
            (FirstHash("string", None), FirstHash("string", True))
        )

    def test_hashes_equal(self):
        """Check hashes equal with same first item."""

        for tuple1, tuple2 in self.test_cases:
            with self.subTest(tuple1=tuple1, tuple2=tuple2):
                self.assertEqual(hash(tuple1), hash(tuple2))

    def test_eq(self):
        """Check objects are equal with same first item."""

        for tuple1, tuple2 in self.test_cases:
            with self.subTest(tuple1=tuple1, tuple2=tuple2):
                self.assertTrue(tuple1 == tuple2)


class SilenceTests(unittest.TestCase):
    def setUp(self) -> None:

        self.bot = MockBot()
        self.cog = Silence(self.bot)
        self.ctx = MockContext()

    def test_silence_sent_correct_discord_message(self):
        """Check if proper message was sent when called with duration in channel with previous state."""
        test_cases = (
            ((self.cog, self.ctx, 0.0001), f"{Emojis.check_mark} #channel silenced for 0.0001 minute(s).", True,),
            ((self.cog, self.ctx, None), f"{Emojis.check_mark} #channel silenced indefinitely.", True,),
            ((self.cog, self.ctx, 5), f"{Emojis.cross_mark} #channel is already silenced.", False,),
        )
        for silence_call_args, result_message, _silence_patch_return in test_cases:
            with self.subTest(
                    silence_duration=silence_call_args[-1],
                    result_message=result_message,
                    starting_unsilenced_state=_silence_patch_return
            ):
                with mock.patch(
                        "bot.cogs.moderation.silence.Silence._silence",
                        new_callable=partial(mock.AsyncMock, return_value=_silence_patch_return)
                ):
                    asyncio.run(self.cog.silence.callback(*silence_call_args))
                    self.ctx.send.call_args.assert_called_once_with(result_message)
