# Security Policy

## Threat Model
The extension intermediates access to Bitwarden data via the `rbw` CLI. It does not store secrets persistently; all sensitive values originate from `rbw` output and are optionally copied to the system clipboard.

## Clipboard Handling
Secrets copied to the clipboard are automatically cleared after a configurable timeout (`clipboard_timeout`, default 15s). Users should avoid prolonging clipboard retention or pasting secrets into untrusted applications.

## Masking
Passwords, CVV, and document identifiers are masked in the UI. Clicking an item copies the full underlying value. Enable `confirm_password_copy` to require an explicit confirmation step for passwords.

## Logging
User queries and prompts are logged only at DEBUG level and redacted to lengths. Run the extension with appropriate log level to avoid retaining sensitive text.

## External Commands
All `rbw` invocations use argument lists (no shell) to mitigate command injection risks. The absolute path to `rbw` is resolved at startup using `shutil.which()`.

## Error Reporting
User-facing notifications provide generic messages. Detailed stack traces remain in logs for debugging.

## Reporting Vulnerabilities
Open an issue labeled `security` or email the developer. Avoid sharing secrets or full stack traces publicly.

## Limitations
- Clipboard clearing depends on the desktop environment's clipboard APIs.
- If a user copies additional data before timeout, previous secrets may persist in clipboard history managers.
- The extension trusts `rbw` output and does not perform additional validation.
