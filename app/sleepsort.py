import argparse
import os
import sys
import threading
import time

import psycopg2


def parse_numbers(raw: str) -> list[int]:
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        raise ValueError("no numbers provided")
    nums = [int(p) for p in parts]
    if any(n < 0 for n in nums):
        raise ValueError("sleep sort requires non-negative integers")
    return nums


def sleep_sort(nums: list[int]) -> list[int]:
    result: list[int] = []
    lock = threading.Lock()

    def worker(n: int) -> None:
        time.sleep(n)
        with lock:
            result.append(n)

    threads = [threading.Thread(target=worker, args=(n,)) for n in nums]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return result


def insert_row(dsn: str, input_numbers: list[int], sorted_numbers: list[int]) -> int:
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sorts (input_numbers, sorted_numbers) "
                "VALUES (%s, %s) RETURNING id",
                (input_numbers, sorted_numbers),
            )
            row = cur.fetchone()
            assert row is not None, "INSERT ... RETURNING id must yield a row"
    return int(row[0])


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="sleepsort",
        description="Sleep-sort a comma-separated list of integers and persist to Postgres.",
    )
    parser.add_argument("numbers", help='Comma-separated integers, e.g. "5,2,3,6"')
    args = parser.parse_args()

    try:
        nums = parse_numbers(args.numbers)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("error: DATABASE_URL is not set", file=sys.stderr)
        return 2

    print(f"sleep-sorting {nums} (will take ~{max(nums)}s)...", flush=True)
    sorted_nums = sleep_sort(nums)
    print(f"sorted: {sorted_nums}", flush=True)

    row_id = insert_row(dsn, nums, sorted_nums)
    print(f"inserted row id={row_id}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
