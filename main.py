#!/usr/bin/env python3
"""TenderGram - construction/EPC tender feed for a Telegram channel.

Usage:
  python main.py fetch              # pull new tenders from active sources into DB
  python main.py post [--dry-run]   # post unposted tenders to the channel
  python main.py run  [--dry-run]   # fetch + post in one go
  python main.py add                # manually add a tender (interactive)
  python main.py stats              # DB counts
"""
import argparse
import sys
import time

import config
import db
import filters
import telegram_client as tg
import fetchers


def cmd_fetch() -> int:
    db.init()
    new = 0
    for mod in fetchers.ACTIVE:
        print(f"Fetching from {mod.SOURCE} ...")
        try:
            tenders = mod.fetch()
        except Exception as e:
            print(f"  ERROR fetching {mod.SOURCE}: {e}")
            continue
        kept = 0
        for t in tenders:
            if filters.accept(t) and db.upsert(t):
                kept += 1
        print(f"  {len(tenders)} notices scanned, {kept} new matching tenders stored")
        new += kept
    return new


def _send(t: dict, dry_run: bool) -> bool:
    caption = tg.format_tender(t)
    if config.VISUAL_CARDS:
        try:
            import card
            png = card.render(t)
            return tg.send_photo(png, caption, dry_run=dry_run)
        except ImportError:
            print("Pillow not installed; falling back to text post.")
        except Exception as e:
            print(f"Card rendering failed ({e}); falling back to text post.")
    return tg.send_message(caption, dry_run=dry_run)


def cmd_post(dry_run: bool = False) -> int:
    db.init()
    pending = db.unposted(config.MAX_POSTS_PER_RUN)
    if not pending:
        print("Nothing to post.")
        return 0
    posted = 0
    for t in pending:
        if _send(t, dry_run):
            if not dry_run:
                db.mark_posted(t["uid"])
            posted += 1
            time.sleep(0 if dry_run else config.POST_INTERVAL_SECONDS)
        else:
            print(f"Failed to post {t['uid']}; stopping this run.")
            break
    print(f"Posted {posted} tender(s){' (dry run)' if dry_run else ''}.")
    return posted


def cmd_add():
    db.init()
    print("Manual tender entry (blank title aborts):")
    title = input("Title: ").strip()
    if not title:
        return
    t = {
        "source": "manual",
        "source_id": str(int(time.time())),
        "title": title,
        "country": input("Country: ").strip() or None,
        "notice_type": input("Notice type [Invitation for Bids]: ").strip() or "Invitation for Bids",
        "procurement_group": "CW",
        "procurement_method": input("Method (optional): ").strip() or None,
        "project_name": input("Project (optional): ").strip() or None,
        "reference_no": input("Reference no (optional): ").strip() or None,
        "deadline": input("Deadline YYYY-MM-DD (optional): ").strip() or None,
        "url": input("URL (optional): ").strip() or None,
        "raw_excerpt": None,
    }
    if not filters.accept(t):
        t.setdefault("region", filters.region_for(t.get("country")) or "Other")
        print("Note: entry would not pass automatic filters; storing anyway.")
    db.upsert(t)
    print("Stored. It will go out on the next `post` run.")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["fetch", "post", "run", "add", "stats"])
    p.add_argument("--dry-run", action="store_true",
                   help="print messages instead of posting to Telegram")
    args = p.parse_args()

    if args.command == "fetch":
        cmd_fetch()
    elif args.command == "post":
        cmd_post(args.dry_run)
    elif args.command == "run":
        cmd_fetch()
        cmd_post(args.dry_run)
    elif args.command == "add":
        cmd_add()
    elif args.command == "stats":
        db.init()
        print(db.stats())


if __name__ == "__main__":
    sys.exit(main())
