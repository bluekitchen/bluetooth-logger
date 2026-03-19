#!/usr/bin/env python3

import argparse
import datetime
import os
import re
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import packetlogger


HCI_PACKET_TYPES = {
    "HCI CMD": 1,
    "HCI ACL": 2,
    "HCI EVT": 4,
}
NOTE_PACKET_TYPE = 0xFC
DEFAULT_NOTE_CATEGORIES = {"GENERIC", "WARN"}

RAW_START_RE = re.compile(r"HCI_RAW (Command|Event|ACL|SCO|ISO) Data\s*:")
HEX_LINE_RE = re.compile(r"^(?P<offset>[0-9A-Fa-f]{4}):\s*(?P<rest>.*)$")
CODE_LEN_RE = re.compile(r"\(Code:\s*0x([0-9A-Fa-f]+)\s+Len:\s*(\d+)\)")
ACL_SUMMARY_RE = re.compile(
    r"Handle:\s*0x([0-9A-Fa-f]+)\s+Boundary:\s*(\d+)\s+Brdcst:\s*(\d+)\s+Len:\s*(\d+)"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert an Infineon AIROC BTSpy text capture into an Apple PacketLogger "
            "(.pklg) file."
        )
    )
    parser.add_argument("input", type=Path, help="BTSpy text capture")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Output PacketLogger file (default: input path with .pklg suffix)",
    )
    parser.add_argument(
        "--date",
        type=parse_date,
        help=(
            "Base capture date in YYYY-MM-DD. If omitted, the input file's mtime date is used. "
            "The converter increments the date on midnight rollover."
        ),
    )
    parser.add_argument(
        "--no-notes",
        action="store_true",
        help="Do not emit PacketLogger note records for BTSpy debug messages.",
    )
    return parser.parse_args()


def parse_date(value: str) -> datetime.date:
    try:
        return datetime.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid date '{value}', expected YYYY-MM-DD") from exc


def default_output_path(input_path: Path) -> Path:
    if input_path.suffix:
        return input_path.with_suffix(".pklg")
    return input_path.with_name(f"{input_path.name}.pklg")


def split_fields(line: str) -> tuple[str, str, str, str] | None:
    parts = re.split(r"\s{2,}", line.rstrip("\r\n"), maxsplit=4)
    if len(parts) != 5:
        return None
    _index, timestamp, direction, category, message = parts
    return timestamp.strip(), direction.strip(), category.strip(), message.strip()


def parse_time(value: str) -> datetime.time:
    try:
        return datetime.time.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid timestamp '{value}'") from exc


def direction_is_outgoing(direction: str, summary: str) -> bool:
    if "🠊" in direction:
        return True
    if "🠈" in direction:
        return False
    if summary.startswith("SENT "):
        return True
    if summary.startswith("RCVD "):
        return False
    raise ValueError(f"cannot determine packet direction from '{direction}' / '{summary}'")


def packetlogger_type(category: str, outgoing: bool) -> int:
    if category not in HCI_PACKET_TYPES:
        raise ValueError(f"unsupported PacketLogger category '{category}'")

    try:
        return packetlogger.packet_log_type_for_hci_type_and_incoming(
            HCI_PACKET_TYPES[category],
            not outgoing,
        )
    except KeyError as exc:
        raise ValueError(f"unsupported PacketLogger category '{category}'") from exc


def hex_bytes_from_message(message: str) -> bytes | None:
    match = HEX_LINE_RE.match(message)
    if not match:
        return None

    hex_region = re.split(r"\s{2,}", match.group("rest"), maxsplit=1)[0].strip()
    if not hex_region:
        return b""

    tokens = hex_region.split()
    for token in tokens:
        if not re.fullmatch(r"[0-9A-Fa-f]{2}", token):
            raise ValueError(f"invalid hex dump token '{token}' in '{message}'")
    return bytes.fromhex(" ".join(tokens))


def format_note(direction: str, category: str, message: str) -> str:
    prefix = category
    if direction != "-":
        prefix = f"{direction} {category}"
    return f"{prefix}: {message}"


@dataclass
class PendingPacket:
    line_no: int
    timestamp: datetime.datetime
    direction: str
    category: str
    raw_kind: str
    payload: bytearray = field(default_factory=bytearray)

    def add_hex_line(self, line_no: int, message: str) -> bool:
        chunk = hex_bytes_from_message(message)
        if chunk is None:
            return False

        match = HEX_LINE_RE.match(message)
        assert match is not None
        offset = int(match.group("offset"), 16)
        if offset != len(self.payload):
            raise ValueError(
                f"line {line_no}: unexpected hex dump offset 0x{offset:04x}, "
                f"expected 0x{len(self.payload):04x}"
            )
        self.payload.extend(chunk)
        return True

    def build_packet(self, line_no: int, message: str) -> tuple[int, bytes] | None:
        outgoing = direction_is_outgoing(self.direction, message)
        packet_type = packetlogger_type(self.category, outgoing)

        if self.category == "HCI CMD":
            packet = self._build_command_packet(line_no, message)
            return None if packet is None else (packet_type, packet)
        if self.category == "HCI EVT":
            packet = self._build_event_packet(line_no, message)
            return None if packet is None else (packet_type, packet)
        if self.category == "HCI ACL":
            packet = self._build_acl_packet(line_no, message)
            return None if packet is None else (packet_type, packet)

        if self.category in {"HCI SCO", "HCI ISO"}:
            raise ValueError(
                f"line {line_no}: {self.category} reconstruction is not implemented yet"
            )
        return None

    def _build_command_packet(self, line_no: int, message: str) -> bytes | None:
        if "Command to HCI." not in message:
            return None

        opcode, param_len = parse_code_and_length(line_no, message)
        self._validate_payload_length(line_no, param_len)
        return struct.pack("<HB", opcode, param_len) + bytes(self.payload)

    def _build_event_packet(self, line_no: int, message: str) -> bytes | None:
        if "Event from HCI." not in message:
            return None

        event_code, param_len = parse_code_and_length(line_no, message)
        if not 0 <= event_code <= 0xFF:
            raise ValueError(f"line {line_no}: event code 0x{event_code:x} does not fit in one byte")
        self._validate_payload_length(line_no, param_len)
        return bytes((event_code, param_len)) + bytes(self.payload)

    def _build_acl_packet(self, line_no: int, message: str) -> bytes | None:
        if "ACL Data to HCI." not in message and "ACL Data from HCI." not in message:
            return None

        match = ACL_SUMMARY_RE.search(message)
        if not match:
            raise ValueError(f"line {line_no}: could not parse ACL summary")

        handle = int(match.group(1), 16)
        boundary = int(match.group(2))
        broadcast = int(match.group(3))
        data_len = int(match.group(4))

        if handle > 0x0FFF:
            raise ValueError(f"line {line_no}: ACL handle 0x{handle:x} exceeds 12 bits")
        if not 0 <= boundary <= 0x3:
            raise ValueError(f"line {line_no}: ACL boundary value {boundary} exceeds 2 bits")
        if not 0 <= broadcast <= 0x3:
            raise ValueError(f"line {line_no}: ACL broadcast value {broadcast} exceeds 2 bits")

        self._validate_payload_length(line_no, data_len)
        header = handle | (boundary << 12) | (broadcast << 14)
        return struct.pack("<HH", header, data_len) + bytes(self.payload)

    def _validate_payload_length(self, line_no: int, expected_len: int) -> None:
        actual_len = len(self.payload)
        if actual_len != expected_len:
            raise ValueError(
                f"line {line_no}: payload length mismatch, decoded length is {expected_len} "
                f"but raw block contains {actual_len} bytes"
            )


def parse_code_and_length(line_no: int, message: str) -> tuple[int, int]:
    match = CODE_LEN_RE.search(message)
    if not match:
        raise ValueError(f"line {line_no}: could not parse code/length summary")
    return int(match.group(1), 16), int(match.group(2))


def base_date_for_capture(input_path: Path, override: datetime.date | None) -> datetime.date:
    if override is not None:
        return override
    mtime = os.path.getmtime(input_path)
    return datetime.datetime.fromtimestamp(mtime).date()


def iter_records(input_path: Path, base_date: datetime.date, emit_notes: bool):
    current_date = base_date
    previous_time: datetime.time | None = None
    pending: PendingPacket | None = None

    with input_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            fields = split_fields(line)
            if fields is None:
                continue

            timestamp_text, direction, category, message = fields
            line_time = parse_time(timestamp_text)

            if previous_time is not None and line_time < previous_time:
                current_date += datetime.timedelta(days=1)
            previous_time = line_time

            line_timestamp = datetime.datetime.combine(current_date, line_time)

            if (
                emit_notes
                and pending is None
                and category in DEFAULT_NOTE_CATEGORIES
            ):
                yield (
                    line_timestamp,
                    NOTE_PACKET_TYPE,
                    format_note(direction, category, message).encode(
                        "ascii",
                        errors="backslashreplace",
                    ),
                )
                continue

            if pending is not None:
                if pending.add_hex_line(line_no, message):
                    continue

                packet_info = pending.build_packet(line_no, message)
                if packet_info is not None:
                    packet_type, packet = packet_info
                    yield pending.timestamp, packet_type, packet
                    pending = None
                    continue

                raw_start_match = RAW_START_RE.search(message)
                if raw_start_match:
                    raise ValueError(
                        f"line {line_no}: encountered a new raw packet before the previous "
                        f"{pending.category} packet was completed"
                    )

            raw_start_match = RAW_START_RE.search(message)
            if raw_start_match:
                pending = PendingPacket(
                    line_no=line_no,
                    timestamp=line_timestamp,
                    direction=direction,
                    category=category,
                    raw_kind=raw_start_match.group(1),
                )

    if pending is not None:
        raise ValueError(
            f"line {pending.line_no}: unterminated raw packet block for {pending.category}"
        )


def main() -> int:
    args = parse_args()
    input_path = args.input
    output_path = args.output or default_output_path(input_path)
    base_date = base_date_for_capture(input_path, args.date)
    emit_notes = not args.no_notes

    records_written = 0
    try:
        with output_path.open("wb") as output:
            for timestamp, packet_type, packet in iter_records(input_path, base_date, emit_notes):
                packetlogger.dump_packet(output, timestamp.timestamp(), packet_type, packet)
                records_written += 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Wrote {records_written} PacketLogger records to {output_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
