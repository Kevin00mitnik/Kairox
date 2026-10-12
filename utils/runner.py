import asyncio
from collections.abc import Sequence
from shlex import join


class CommandError(RuntimeError):
    """An external command could not run or completed unsuccessfully."""


async def run_cmd(
    args: Sequence[str],
    input_text: str | None = None,
    timeout: int = 300,
) -> str:
    command = join(args)
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdin=(
                asyncio.subprocess.PIPE
                if input_text is not None
                else asyncio.subprocess.DEVNULL
            ),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise CommandError(
            f"Required command '{command}' was not found. Run ./install.sh as your normal user."
        ) from exc
    except OSError as exc:
        raise CommandError(f"Could not start '{command}': {exc}") from exc

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input_text.encode() if input_text is not None else None),
            timeout=timeout,
        )
    except asyncio.TimeoutError as exc:
        proc.kill()
        await proc.communicate()
        raise CommandError(
            f"'{command}' exceeded its {timeout}-second timeout. Check your connection and try again."
        ) from exc
    except asyncio.CancelledError:
        proc.kill()
        await proc.communicate()
        raise

    output = stdout.decode(errors="replace")
    if proc.returncode:
        detail = stderr.decode(errors="replace").strip()
        message = detail or f"process exited with status {proc.returncode}"
        raise CommandError(f"'{command}' failed: {message}")

    return output
