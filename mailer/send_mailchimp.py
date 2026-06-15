"""
Mailchimp API integration.

Operations:
  1. Create (or update) a campaign with the draft HTML
  2. Send a test email to the owner for approval
  3. (After approval) send the campaign to the list

Usage:
  python email/send_mailchimp.py --html drafts/file.html --subject "MacroPulse | Week Ahead | 6 May 2026" --test
  python email/send_mailchimp.py --campaign-id abc123 --send

Requires .env with:
  MAILCHIMP_API_KEY=your-key-us1
  MAILCHIMP_LIST_ID=your-audience-id
  MAILCHIMP_FROM_NAME=MacroPulse
  MAILCHIMP_FROM_EMAIL=shaunmcewan@gmail.com
  MAILCHIMP_TEST_EMAIL=shaunmcewan@gmail.com
"""

import argparse
import json
import os
import sys

import requests


def _load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    env = {}
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"')
    # Override with actual environment variables
    for key in ["MAILCHIMP_API_KEY", "MAILCHIMP_LIST_ID", "MAILCHIMP_FROM_NAME",
                "MAILCHIMP_FROM_EMAIL", "MAILCHIMP_TEST_EMAIL"]:
        if key in os.environ:
            env[key] = os.environ[key]
    return env


def get_client():
    env    = _load_env()
    api_key = env.get("MAILCHIMP_API_KEY", "")
    if not api_key:
        raise ValueError("MAILCHIMP_API_KEY not set. Add it to .env file.")

    server = api_key.split("-")[-1] if "-" in api_key else "us1"
    base   = f"https://{server}.api.mailchimp.com/3.0"
    auth   = ("anystring", api_key)
    return base, auth, env


def create_campaign(subject: str, preview_text: str = "") -> str:
    """Create a new regular campaign. Returns campaign_id."""
    base, auth, env = get_client()

    list_id    = env.get("MAILCHIMP_LIST_ID", "")
    from_name  = env.get("MAILCHIMP_FROM_NAME", "MacroPulse")
    from_email = env.get("MAILCHIMP_FROM_EMAIL", "")

    if not list_id:
        raise ValueError("MAILCHIMP_LIST_ID not set.")

    payload = {
        "type": "regular",
        "settings": {
            "subject_line":   subject,
            "preview_text":   preview_text,
            "title":          subject,
            "from_name":      from_name,
            "reply_to":       from_email,
        },
        "recipients": {"list_id": list_id},
    }
    resp = requests.post(f"{base}/campaigns", json=payload, auth=auth, timeout=20)
    resp.raise_for_status()
    campaign_id = resp.json()["id"]
    print(f"[mailchimp] Created campaign: {campaign_id}")
    return campaign_id


def set_campaign_content(campaign_id: str, html: str) -> None:
    """Upload HTML content to an existing campaign."""
    base, auth, _ = get_client()
    resp = requests.put(
        f"{base}/campaigns/{campaign_id}/content",
        json={"html": html},
        auth=auth,
        timeout=30,
    )
    resp.raise_for_status()
    print(f"[mailchimp] Content uploaded to campaign {campaign_id}")


def send_test_email(campaign_id: str, test_email: str = None) -> None:
    """Send a test email to the specified address."""
    base, auth, env = get_client()
    email = test_email or env.get("MAILCHIMP_TEST_EMAIL", "shaunmcewan@gmail.com")

    resp = requests.post(
        f"{base}/campaigns/{campaign_id}/actions/test",
        json={"test_emails": [email], "send_type": "html"},
        auth=auth,
        timeout=20,
    )
    resp.raise_for_status()
    print(f"[mailchimp] Test email sent to {email}")


def send_campaign(campaign_id: str) -> None:
    """Send the campaign to the full list. IRREVERSIBLE.

    Belt-and-braces: re-PATCHes the campaign's subject_line from the saved
    pending_campaign.json right before firing, so Mailchimp can never leak a
    '[TEST]' or other test-flow modification into the live send.
    """
    base, auth, _ = get_client()

    # Defensive subject restore from pending_campaign.json.
    # Mailchimp stores "[TEST] ..." on the campaign when a test is sent;
    # we PATCH it back and then verify with a GET before the live send.
    # A failed PATCH or a mismatch on verify raises here — better to abort
    # than to send "[TEST] MacroPulse ..." to the full subscriber list.
    try:
        pending_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "drafts", "pending_campaign.json"
        )
        with open(pending_path, encoding="utf-8") as f:
            meta = json.load(f)
        clean_subject = meta.get("subject")
        if clean_subject and meta.get("campaign_id") == campaign_id:
            # 1. PATCH the subject back to the clean value.
            patch_resp = requests.patch(
                f"{base}/campaigns/{campaign_id}",
                auth=auth,
                json={"settings": {"subject_line": clean_subject}},
                timeout=20,
            )
            if not patch_resp.ok:
                raise RuntimeError(
                    f"Subject PATCH failed ({patch_resp.status_code}): "
                    f"{patch_resp.text[:300]}"
                )
            print(f"[mailchimp] Subject PATCH accepted: \"{clean_subject}\"")

            # 2. Verify the live campaign subject matches before sending.
            get_resp = requests.get(
                f"{base}/campaigns/{campaign_id}",
                auth=auth,
                timeout=20,
            )
            get_resp.raise_for_status()
            live_subject = get_resp.json().get("settings", {}).get("subject_line", "")
            if live_subject != clean_subject:
                raise RuntimeError(
                    f"Subject mismatch after PATCH — live='{live_subject}', "
                    f"expected='{clean_subject}'. Aborting send."
                )
            print(f"[mailchimp] Subject verified clean: \"{live_subject}\"")
        else:
            print("[mailchimp] !! pending_campaign.json missing or campaign_id mismatch "
                  "— cannot verify subject. Aborting send.")
            raise RuntimeError("Cannot verify subject — aborting to protect subscriber list.")
    except RuntimeError:
        raise  # propagate to caller — do not proceed to send
    except Exception as e:
        print(f"[mailchimp] !! subject restore failed unexpectedly: {e}")
        raise RuntimeError(f"Subject restore error — aborting send: {e}") from e

    resp = requests.post(
        f"{base}/campaigns/{campaign_id}/actions/send",
        auth=auth,
        timeout=20,
    )
    resp.raise_for_status()
    print(f"[mailchimp] Campaign {campaign_id} sent to list.")
    # Auto-archive: commit + push archive/ so the website picks up the new issue.
    try:
        archive_after_send(campaign_id)
    except Exception as e:
        print(f"[archive] !! auto-archive failed: {e}")
        print("[archive] Run manually: git add archive/ && git commit && git push")


def archive_after_send(campaign_id: str) -> None:
    """
    After a successful Mailchimp send, copy the rendered HTML draft into
    archive/, update archive/index.json, and commit+push to origin/main.

    Reads drafts/pending_campaign.json to find the draft file and subject.
    Safe to call multiple times — git will say 'nothing to commit' if there
    are no changes.
    """
    import os, json, subprocess, shutil, datetime as _dt
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent
    pending   = repo_root / "drafts" / "pending_campaign.json"
    archive   = repo_root / "archive"
    archive.mkdir(exist_ok=True)
    manifest_path = archive / "index.json"

    if not pending.exists():
        print("[archive] no drafts/pending_campaign.json — skipping")
        return

    with open(pending, encoding="utf-8") as f:
        meta = json.load(f)
    if meta.get("campaign_id") != campaign_id:
        print(f"[archive] pending_campaign.json doesn't match {campaign_id} — skipping")
        return

    src_html = Path(meta["html_path"])
    if not src_html.exists():
        print(f"[archive] !! html missing: {src_html}")
        return

    archived = archive / src_html.name
    shutil.copy2(src_html, archived)
    print(f"[archive] copied -> {archived.relative_to(repo_root)}")

    # Update index.json — load existing, prepend/replace this issue entry
    if manifest_path.exists():
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        manifest = {"_schema_version": 1, "issues": []}

    # Derive a slug + issue metadata from the filename: YYYY-MM-DD-{monday|friday}.html
    stem = src_html.stem  # "2026-06-03-monday"
    parts = stem.rsplit("-", 1)
    date_str, kind = parts[0], parts[1].lower() if len(parts) == 2 else (stem, "monday")
    kind = "monday" if "monday" in kind else "friday"
    title = "Week Ahead" if kind == "monday" else "Week in Review"
    slug  = f"{date_str}-{title.lower().replace(' ', '-')}"

    existing = manifest.get("issues", [])

    # issue_number: reuse this issue's number if we're re-archiving the same
    # campaign/slug; otherwise increment from the highest number on file.
    prior = next(
        (i for i in existing
         if i.get("mailchimp_campaign_id") == campaign_id or i.get("slug") == slug),
        None,
    )
    if prior and isinstance(prior.get("issue_number"), int):
        issue_number = prior["issue_number"]
    else:
        nums = [i["issue_number"] for i in existing
                if isinstance(i.get("issue_number"), int)]
        issue_number = (max(nums) + 1) if nums else 1

    # headline: first non-blank line of the matching article draft.
    headline = ""
    article_file = repo_root / "drafts" / f"article-{kind}.txt"
    try:
        with open(article_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    headline = line.strip()
                    break
    except Exception:
        pass

    # dial_state + scorecard from the bot's indicators.json (the source of
    # truth), falling back to config/dial.json for the state only.
    dial_state, scorecard = "", ""
    try:
        with open(repo_root / "data" / "indicators.json", encoding="utf-8") as f:
            ind = json.load(f)
        dial_state = (ind.get("dial") or {}).get("state", "")
        inds = ind.get("indicators", []) or []
        sup = sum(1 for i in inds if (i.get("status") or "").lower() == "supportive")
        neu = sum(1 for i in inds if (i.get("status") or "").lower() == "neutral")
        hw  = sum(1 for i in inds if (i.get("status") or "").lower() == "headwind")
        scorecard = f"{sup} supportive · {neu} neutral · {hw} headwind"
    except Exception:
        pass
    if not dial_state:
        try:
            with open(repo_root / "config" / "dial.json", encoding="utf-8") as f:
                dial_state = json.load(f).get("phase", "")
        except Exception:
            pass

    if not headline:
        print(f"[archive] !! headline empty — check {article_file.name}")
    if not scorecard:
        print("[archive] !! scorecard empty — check data/indicators.json")

    entry = {
        "issue_number":          issue_number,
        "date":                  date_str,
        "type":                  kind,
        "title":                 title,
        "subject":               meta.get("subject", ""),
        "headline":              headline,
        "dial_state":            dial_state,
        "scorecard":             scorecard,
        "html_path":             f"archive/{src_html.name}",
        "mailchimp_campaign_id": campaign_id,
        "sent_at":               _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "slug":                  slug,
    }
    # Replace any existing entry with the same campaign_id or slug; then append.
    manifest["issues"] = [
        i for i in existing
        if i.get("mailchimp_campaign_id") != campaign_id and i.get("slug") != slug
    ]
    manifest["issues"].append(entry)
    # Sort ascending by date, newest last (matches existing convention).
    manifest["issues"].sort(key=lambda i: i.get("date", ""))

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"[archive] updated -> {manifest_path.relative_to(repo_root)}")

    # Commit + push
    def _git(*args):
        return subprocess.run(
            ["git", *args], cwd=repo_root, check=False,
            capture_output=True, text=True,
        )
    _git("add", "archive/")
    status = _git("status", "--porcelain", "archive/").stdout.strip()
    if not status:
        print("[archive] nothing new to commit")
        return
    commit = _git(
        "commit",
        "-m", f"Archive {kind} issue {date_str} (campaign {campaign_id})",
    )
    if commit.returncode != 0:
        print(f"[archive] !! commit failed: {commit.stderr.strip()}")
        return
    push = _git("push", "origin", "HEAD:main")
    if push.returncode != 0:
        print(f"[archive] !! push failed: {push.stderr.strip()}")
        print("[archive] Run manually: git push origin main")
        return
    print("[archive] pushed to origin/main — website will pick up within 5 min")


def upload_image(png_bytes: bytes, filename: str) -> str:
    """
    Upload a PNG to Mailchimp's file manager and return the hosted CDN URL.
    Mailchimp strips data:image base64 URIs from campaign HTML, so charts
    must be hosted here instead.
    """
    import base64
    base, auth, _ = get_client()
    b64 = base64.b64encode(png_bytes).decode("ascii")
    resp = requests.post(
        f"{base}/file-manager/files",
        json={"name": filename, "file_data": b64},
        auth=auth,
        timeout=30,
    )
    resp.raise_for_status()
    url = resp.json().get("full_size_url", "")
    print(f"[mailchimp] Uploaded {filename} -> {url}")
    return url


def draft_and_test(html_path: str, subject: str, preview_text: str = "",
                   test_email: str = None, send_test: bool = True) -> str:
    """
    Build a campaign draft on Mailchimp and send a test email by default.
    Returns the campaign_id.

    Workflow:
      1. Orchestrator runs (Monday/Friday) → creates draft + sends test to owner.
         The test arrives with Mailchimp's "[TEST]" subject prefix — that is
         Mailchimp's behaviour, not stored on the campaign.
      2. Owner reviews, edits article/charts, may run another test:
            python mailer/send_mailchimp.py --campaign-id <id> --test
      3. Owner approves and publishes:
            python mailer/send_mailchimp.py --campaign-id <id> --send
         send_campaign() re-PATCHes the campaign's subject_line right before
         firing, so the live send is guaranteed [TEST]-free.

    Pass send_test=False to skip the auto-test (rarely needed).
    """
    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    campaign_id = create_campaign(subject, preview_text)
    set_campaign_content(campaign_id, html)
    if send_test:
        send_test_email(campaign_id, test_email)

    # Save campaign ID to a pending file so approve.py can use it
    pending_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "drafts", "pending_campaign.json"
    )
    os.makedirs(os.path.dirname(pending_path), exist_ok=True)
    with open(pending_path, "w") as f:
        json.dump({"campaign_id": campaign_id, "subject": subject,
                   "html_path": html_path}, f, indent=2)
    print(f"[mailchimp] Pending campaign saved to {pending_path}")

    return campaign_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html",        help="Path to HTML draft file")
    parser.add_argument("--subject",     default="MacroPulse Newsletter")
    parser.add_argument("--preview",     default="")
    parser.add_argument("--test",        action="store_true", help="Create draft and send test email")
    parser.add_argument("--campaign-id", help="Existing campaign ID")
    parser.add_argument("--send",        action="store_true", help="Send campaign to full list")
    args = parser.parse_args()

    if args.send and args.campaign_id:
        confirm = input(f"Send campaign {args.campaign_id} to the full list? (yes/no): ")
        if confirm.strip().lower() == "yes":
            send_campaign(args.campaign_id)
        else:
            print("Cancelled.")
    elif args.test and args.campaign_id:
        # Send a test email for an existing campaign (the orchestrator's draft).
        send_test_email(args.campaign_id)
    elif args.test and args.html:
        # Build a fresh draft AND send a test in one shot.
        draft_and_test(args.html, args.subject, args.preview, send_test=True)
    else:
        parser.print_help()
