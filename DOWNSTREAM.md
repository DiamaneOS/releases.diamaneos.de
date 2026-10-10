# Download service boundaries

Upstream provenance is recorded in [UPSTREAM.json](UPSTREAM.json). The upstream MIT license is retained in [LICENSE](LICENSE).

Nginx serves OS and application files from read-only publication roots. HTTPS requires TLS 1.3. DNS resolution uses systemd-resolved. Session tickets rotate through the shared infrastructure scripts. This repository defines no SUPL listener.

The Debian deployment uses [DiamaneOS/infrastructure](https://github.com/DiamaneOS/infrastructure/tree/main/debian). Targets are explicit, and request logs are disabled. Gzip negotiation and explicit compressed-package paths retain their upstream behavior without a separately rebuilt Brotli module.

Publication copies immutable payloads to configured download targets before replacing selectors. Files referenced by current and previous metadata remain available. Publication does not prune historical payloads. The overview rejects empty selectors and supports absent channels.

`deploy-releases` calls the protected executable selected by `DIAMANEOS_PUBLICATION_TRANSPORT` for payload and selector phases. Authentication, target selection and remote installation belong to that transport.

Signature creation is separate from serving. A transport response does not establish an APK, OTA or verified-boot signature's validity. Serving hosts contain no release-signing private keys.
