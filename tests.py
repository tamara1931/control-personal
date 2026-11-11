#!/usr/bin/env python3
"""Offline static checks; deliberately no Firebase/network or real user data."""
import json
from pathlib import Path

base = Path(__file__).parent
html = (base / 'index.html').read_text()
rules = json.loads((base / 'database.rules.json').read_text())['rules']
assert rules['.read'] is False and rules['.write'] is False
assert rules['roles']['$uid']['.write'] is False
assert rules['profiles']['$uid']['.write'] is False
assert "auth.uid === $uid" in rules['pollResponses']['$pollId']['$uid']['.read']
assert "root.child('roles').child(auth.uid).val() === 'admin'" in rules['pollResponses']['$pollId']['.read']
assert "auth.uid === $uid" in rules['eventResponses']['$eventId']['$uid']['.write']
assert "root.child('roles').child(auth.uid).val() === 'admin'" in rules['events']['$eventId']['.write']
assert "root.child('roles').child(auth.uid).val() === 'admin'" in rules['eventAssignments']['$eventId']['$uid']['.write']
assert 'REPLACE_WITH_FIREBASE_WEB_API_KEY' in html
assert 'localStorage' not in html
assert 'innerHTML' not in html
assert 'worker-dni' not in html.lower() and 'dni' not in html.lower()
assert 'pollResponses/${id}/${me.uid}' in html
assert 'eventResponses/${id}/${me.uid}' in html
assert 'ServerValue.TIMESTAMP' in html
assert 'push().set' in html
assert "newData.val() === 'none'" in rules['pollResponses']['$pollId']['$uid']['days']['$day']['.validate']
print('PASS: rules JSON parse; default-deny and client-write-denied roles/profiles; owner/admin response access; admin event/assignment writes; placeholder config; no localStorage/innerHTML/DNI; UID-scoped writes and timestamp; availability enum validation.')
print('LIMIT: static checks only; no Firebase Emulator, rules compiler, browser execution, project access, or live data test.')
