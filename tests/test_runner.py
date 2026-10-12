import asyncio
import sys
import unittest

from utils.runner import CommandError, run_cmd


class RunCommandTests(unittest.IsolatedAsyncioTestCase):
    async def test_passes_arguments_and_stdin_without_a_shell(self):
        output = await run_cmd(
            [
                sys.executable,
                "-c",
                "import sys; print(sys.stdin.read()); print(sys.argv[1])",
                "value; not a shell command",
            ],
            input_text="input data",
        )

        self.assertEqual(
            output.replace("\r\n", "\n"),
            "input data\nvalue; not a shell command\n",
        )

    async def test_reports_missing_executable(self):
        with self.assertRaisesRegex(CommandError, "was not found"):
            await run_cmd(["kairox-command-that-does-not-exist"])

    async def test_reports_nonzero_exit_and_stderr(self):
        with self.assertRaisesRegex(CommandError, "test failure"):
            await run_cmd(
                [
                    sys.executable,
                    "-c",
                    "import sys; print('test failure', file=sys.stderr); sys.exit(2)",
                ]
            )

    async def test_stops_a_timed_out_process(self):
        with self.assertRaisesRegex(CommandError, "timeout"):
            await run_cmd(
                [sys.executable, "-c", "import time; time.sleep(5)"],
                timeout=0.01,
            )

    async def test_stops_a_process_when_cancelled(self):
        task = asyncio.create_task(
            run_cmd([sys.executable, "-c", "import time; time.sleep(5)"])
        )
        await asyncio.sleep(0.05)
        task.cancel()

        with self.assertRaises(asyncio.CancelledError):
            await task


if __name__ == "__main__":
    unittest.main()
