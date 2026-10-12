import ipaddress
import re


def normalize_domain(value: str) -> str:
    target = value.strip().rstrip(".")
    if not target:
        raise ValueError("A domain is required.")

    try:
        return str(ipaddress.ip_address(target))
    except ValueError:
        pass

    try:
        target = target.encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise ValueError("Enter a valid domain name.") from exc

    if len(target) > 253 or any(
        not label
        or len(label) > 63
        or not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label)
        for label in target.split(".")
    ):
        raise ValueError("Enter a valid domain name, for example example.com.")

    return target
