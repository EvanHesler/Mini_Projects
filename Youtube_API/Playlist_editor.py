"""
YouTube Playlist Reorder Tool
Moves a video to a specified position within a playlist the user owns.
"""

import os
import sys
from dataclasses import dataclass
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
CLIENT_SECRETS_FILE = "client_secret.json"
TOKEN_FILE = "token.json"


# ---------------------------------------------------------------------------
# 1. AUTH
# ---------------------------------------------------------------------------
def get_authenticated_service():
    creds: Optional[Credentials] = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


# ---------------------------------------------------------------------------
# 2. DATA MODEL
# ---------------------------------------------------------------------------
@dataclass
class PlaylistItemRecord:
    item_id: str          # playlist item ID (needed for update)
    video_id: str          # video ID (for display / matching)
    title: str
    position: int
    playlist_id: str


# ---------------------------------------------------------------------------
# 3. LIST PLAYLISTS (so the user can pick one safely, not paste a raw ID blind)
# ---------------------------------------------------------------------------
def list_my_playlists(youtube):
    playlists = []
    request = youtube.playlists().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=50,
    )
    while request is not None:
        response = request.execute()
        for item in response.get("items", []):
            playlists.append(
                {
                    "id": item["id"],
                    "title": item["snippet"]["title"],
                    "itemCount": item["contentDetails"]["itemCount"],
                }
            )
        request = youtube.playlists().list_next(request, response)
    return playlists


# ---------------------------------------------------------------------------
# 4. FETCH ALL ITEMS IN A PLAYLIST (paginated)
# ---------------------------------------------------------------------------
def fetch_playlist_items(youtube, playlist_id: str) -> list[PlaylistItemRecord]:
    records: list[PlaylistItemRecord] = []
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults=50,
    )
    while request is not None:
        try:
            response = request.execute()
        except HttpError as e:
            _handle_http_error(e)
            raise

        for item in response.get("items", []):
            snippet = item["snippet"]
            records.append(
                PlaylistItemRecord(
                    item_id=item["id"],
                    video_id=snippet["resourceId"]["videoId"],
                    title=snippet.get("title", "(untitled)"),
                    position=snippet["position"],
                    playlist_id=snippet["playlistId"],
                )
            )
        request = youtube.playlistItems().list_next(request, response)

    return records


# ---------------------------------------------------------------------------
# 5. FIND TARGET ITEM (with safeguards against ambiguity)
# ---------------------------------------------------------------------------
def find_target_item(
    records: list[PlaylistItemRecord], video_id: str
) -> PlaylistItemRecord:
    matches = [r for r in records if r.video_id == video_id]
    if not matches:
        raise ValueError(f"No video with ID '{video_id}' found in this playlist.")
    if len(matches) > 1:
        # Same video appears more than once in the playlist -> ambiguous.
        # Refuse to guess; force caller to disambiguate by playlist item ID.
        raise ValueError(
            f"Video '{video_id}' appears {len(matches)} times in this playlist "
            f"(item IDs: {[m.item_id for m in matches]}). "
            "Re-run specifying the exact playlist item ID instead of video ID."
        )
    return matches[0]


# ---------------------------------------------------------------------------
# 6. MOVE (UPDATE POSITION)
# ---------------------------------------------------------------------------
def move_playlist_item(youtube, record: PlaylistItemRecord, new_position: int):
    body = {
        "id": record.item_id,
        "snippet": {
            "playlistId": record.playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": record.video_id,
            },
            "position": new_position,
        },
    }
    try:
        response = (
            youtube.playlistItems()
            .update(part="snippet", body=body)
            .execute()
        )
    except HttpError as e:
        _handle_http_error(e)
        raise
    return response


# ---------------------------------------------------------------------------
# 7. VERIFY
# ---------------------------------------------------------------------------
def verify_position(youtube, item_id: str, expected_position: int) -> bool:
    response = youtube.playlistItems().list(part="snippet", id=item_id).execute()
    items = response.get("items", [])
    if not items:
        return False
    actual = items[0]["snippet"]["position"]
    return actual == expected_position


# ---------------------------------------------------------------------------
# ERROR HELPER
# ---------------------------------------------------------------------------
def _handle_http_error(e: HttpError):
    status = e.resp.status
    if status == 403:
        print(
            "Permission or quota error (403). Check OAuth scope is "
            "youtube.force-ssl/youtube, that you own the playlist, and that "
            "daily quota isn't exceeded."
        )
    elif status == 404:
        print("Not found (404). The playlist or item ID may be stale — re-fetch.")
    else:
        print(f"HTTP error {status}: {e}")


# ---------------------------------------------------------------------------
# MAIN — example: move a specific video to position 0 (top) of a playlist
# ---------------------------------------------------------------------------
def main():
    youtube = get_authenticated_service()

    # --- Safety: make the user explicitly pick from THEIR OWN playlists ---
    playlists = list_my_playlists(youtube)
    if not playlists:
        print("No playlists found for this account.")
        return

    print("Your playlists:")
    for i, p in enumerate(playlists):
        print(f"  [{i}] {p['title']}  ({p['itemCount']} items)  id={p['id']}")

    choice = int(input("Select playlist index: "))
    playlist_id = playlists[choice]["id"]

    # --- Fetch full current snapshot (paginated) ---
    records = fetch_playlist_items(youtube, playlist_id)
    print(f"\nFetched {len(records)} items.")
    for r in records:
        print(f"  pos={r.position:>3}  {r.title}  (videoId={r.video_id})")

    target_video_id = input("\nEnter the videoId to move: ").strip()
    new_position = int(input("Enter the desired 0-indexed position: ").strip())

    if not (0 <= new_position < len(records)):
        print(f"Position must be between 0 and {len(records) - 1}.")
        return

    target = find_target_item(records, target_video_id)

    # --- Confirm before mutating (avoid accidental changes) ---
    confirm = input(
        f"Move '{target.title}' from position {target.position} to "
        f"{new_position} in playlist '{playlists[choice]['title']}'? [y/N] "
    )
    if confirm.lower() != "y":
        print("Aborted.")
        return

    move_playlist_item(youtube, target, new_position)

    if verify_position(youtube, target.item_id, new_position):
        print("✅ Move confirmed: item is now at the requested position.")
    else:
        print("⚠️ Move request succeeded but verification did not match — re-check manually.")


if __name__ == "__main__":
    main()