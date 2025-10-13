# PdaNet Linux – Security and Privileges

## PolicyKit Integration

- The GUI performs privileged actions (connecting/disconnecting, firewall rules) using `pkexec`.
- A PolicyKit policy is installed by `install.sh` to present a graphical authentication prompt:
  - `/usr/share/polkit-1/actions/org.pdanetlinux.pkexec.policy`
- Fallback: if `pkexec` is unavailable, the app falls back to `sudo`.

## WiFi Credential Storage

- WiFi passwords are stored in the system keyring (Secret Service/libsecret) via the Python `keyring` package when available.
- If the keyring is not available, the app falls back to a JSON file at `~/.config/pdanet-linux/wifi_networks.json` with file mode `0600`.
- Migration: on first read, the app will use keyring if available and keep only metadata in JSON.

## Visual Testing Baselines

- Visual regression baselines update only when `PDANET_UPDATE_BASELINES=1` is set.
- Default behavior prevents accidental baseline drift in CI.

## Connectivity Checks

- Connectivity and proxy validation use HTTPS (HEAD) requests for better security and reliability.

