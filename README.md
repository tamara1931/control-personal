# Catering staff app — secure replacement draft

This is a proposed replacement, not a deployment. It intentionally has no connection to Firebase, no real worker data, and no hard-coded service credentials. The Firebase browser config in `index.html` is placeholders and must be configured for a separately approved deployment. Do not use it with production until the rollout steps and authorization review below are completed.

## Files
- `index.html` — Spanish responsive Firebase Auth email/password UI; staff own poll and event replies; admin poll response/day view, event management and assignment.
- `database.rules.json` — default-deny Realtime Database policy for the new data model.
- `tests.py` — offline structural/security-invariant checks only.

## New data layout and access model
- `profiles/{uid}`: `{displayName}`; server-provisioned, self/admin readable, client write denied.
- `roles/{uid}`: `admin` or `employee`; server-provisioned/read by that UID, all client writes denied. Admin is determined by this server-controlled role, never a client flag, email claim, localStorage, or UI state.
- `polls/{pushId}` and `events/{pushId}`: public to authenticated accounts, writes admin-only; exact field and size/type validation.
- `pollResponses/{pollId}/{uid}` and `eventResponses/{eventId}/{uid}`: each employee can read/write only their UID record; admins can read; names must agree with the server-provisioned profile. Admin-only parent read allows a compatible collection query; employees cannot read a parent collection. Read the exact child path in the staff UI.
- `eventAssignments/{eventId}/{uid}`: each employee reads only their own assignment; admins read/write.

Rules are the authorization boundary. UI role gating is not security. No global worker directory or DNI is included. All dynamic content uses DOM `textContent`/text nodes and selects, never HTML interpolation; input validation and database rules reject invalid/oversized values. Responses are written per UID path to avoid whole-poll/event replacement races; assignment writes are per UID, rather than read-modify-write of shared arrays. No localStorage auth/session data.

## Provisioning (server-only; prerequisite)
1. Create Firebase Auth email/password accounts through a trusted administrator process (Firebase console or Admin SDK). Require verified, unique employee email addresses and distribute initial credentials securely; arrange password change/reset. Do not use DNI as an identifier or credential.
2. Obtain each account's Firebase Auth UID from the trusted process. Using Firebase Admin SDK/service account in a controlled environment (never in this browser app), write exactly `profiles/{uid}: {displayName: ...}` and `roles/{uid}: 'employee'` for each employee. Assign `roles/{uid}: 'admin'` to the pre-approved manager UID(s) only. Restrict and audit access to Admin SDK credentials. Admin self-promotion from clients is impossible under these rules; changes to roles require trusted server/console authority and change control.
3. Before any client login, deploy and test these rules on a separate staging Firebase project, populate a small synthetic test dataset, and configure the web app with that project's web config. Enable Email/Password Auth, authorized domains, suitable password/reset policy, App Check where applicable, monitoring, and account recovery. Browser API key is public project configuration, not a secret. Never paste a service account or private key into the HTML.

## Backup and migration / rollout plan
1. Keep the deliberately locked production rules locked. Do not run this draft against the live project. Freeze old writers and independently export a timestamped full RTDB JSON backup using authorized Firebase tooling/Admin SDK; store an encrypted, access-controlled copy and verify it can be restored in a disposable project. Include rules and Auth account/UID inventory in the protected backup where applicable. Do not transmit or check in legacy worker records.
2. Inventory old `workers`, `polls`, `events` and their response data in a controlled migration environment, particularly the DNI fields and name-derived response keys. Resolve identities manually against authorized HR records; do not assume normalized names are unique and never use DNI as a login key. New UIDs should come from Auth, not the old key. Preserve the immutable backup; leave legacy branches untouched during initial rollout. Do not merge old data into this schema until reviewed and mapped.
3. If migration is approved, use a reviewed, one-off Admin SDK script with explicit UID mapping and dry-run report. Exclude DNI entirely. Convert polls/events into the exact new schema; map each individual answer to `pollResponses/{pollId}/{uid}` or `eventResponses/{eventId}/{uid}`, validate every field/date, and quarantine ambiguous/unmapped rows in encrypted restricted storage rather than guessing. Never import old `availability`, `assigned` arrays or a full worker list as trusted data. Keep legacy untouched until reconciliation and restore test pass.
4. Review the resulting export and counts without exposing personal data; run the staging test matrix and independent rules review. Obtain manager/worker acceptance, a tested rollback procedure and maintenance window. Deploy rules before hosting/app access; stage credentials and profile/role documents; only then authorize pilot logins. Monitor denied access and failures. Keep old application stopped. Roll back by disabling new app access and restoring the reviewed backup/rules through authorized operators; do not loosen root rules as a fallback.

## Known breakages and prerequisites
- Existing Firebase data is not compatible as-is: no legacy key/DNI login, worker creation, public staff list, old `responses` field, old `availability`/`assigned` event fields, or local remembered session. All staff need Auth accounts and UID profile/role provisioning first. The new model requires creating a fresh copy/migration of polls/events/responses; no automatic migration is performed.
- Firebase Auth SDK/config placeholders must be replaced by approved web config and matching Auth/RTDB project configuration. This HTML is not hosted and has not been tested against Firebase Emulator or a real project.
- RTDB rules cannot enforce global maximum record counts or a strict total payload budget; client checks for poll/event counts and 62-day range are usability controls, not hard security caps. For strict quotas / robust admin event deletion and response cleanup use a trusted backend/Cloud Function. Responses remain after event/poll deletion unless a controlled cleanup job is added.
- Date format rules enforce a date-shaped string, while client validates actual dates and interval length. For adversarial writes requiring true calendar validation, add backend validation.
- Admin display name/results are personal data; limit admin accounts and apply retention/access policy. Firebase Auth, hosting, backup, logging, privacy notices, legal basis, data retention and incident response need owner approval.

## Offline checks
Run `python3 tests.py`. They validate JSON syntax and a set of source/rules invariants without Firebase or worker data. They are not a substitute for Firebase Emulator Suite rules tests or a security audit.
