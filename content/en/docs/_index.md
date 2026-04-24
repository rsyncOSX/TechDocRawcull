---
title: RawCull Documentation
linkTitle: Documentation
menu: { main: { weight: 20 } }
---


## System Requirements

- **macOS Tahoe** and later
- **Apple Silicon** (M-series) only

The release on [GitHub](https://github.com/rsyncOSX/RawCull/releases) may be more current than the release on the [Apple App Store](https://apps.apple.com/no/app/rawcull/id6759362764?mt=12). The builds on both platforms are identical, and the GitHub release is signed and notarized by Apple. 

> **Security & Privacy**: RawCull is digitally signed and notarized by Apple to protect against tampering. It runs as a sandboxed application, ensuring your data and system remain secure.

## Welcome to RawCull

**RawCull** is a robust, native macOS application developed using Swift and SwiftUI for *macOS Tahoe*. Tailored specifically for photographers, it simplifies the photo culling process, enabling users to quickly identify and keep only their best photographs. RawCull supports **Sony ARW** and **Nikon NEF** RAW files. Per-vendor knowledge (embedded thumbnail and preview extraction, MakerNote focus-point parsing, compression labels, size-class thresholds) is encapsulated behind a common `RawFormat` protocol, so additional brands can be added without touching the pipeline code.

## Supported RAW formats

| Brand | Extension | Source reference |
|---|---|---|
| Sony | `.arw` | `Enum/SonyRawFormat.swift` |
| Nikon | `.nef` | `Enum/NikonRawFormat.swift` |

Both paths use ImageIO for the common decode path and fall back to a dedicated binary TIFF walker (`SonyMakerNoteParser`, `NikonMakerNoteParser`) when ImageIO cannot surface the embedded JPEG — for example ARW 6.0 (RA16) from the A7 V or NEF files where the full-resolution preview lives inside a SubIFD chain rather than at a top-level image index.

## Sony ARW body compatibility

The following Sony bodies successfully extract EXIF, focus points, sharpness, and saliency, except for the ILCE-7RM5, which failed to extract saliency on one of its three files. The ILCE-1M2 is the only body tested across all three Sony RAW size variants (S/M/L). All files use compressed RAW, and every body achieves full-resolution L-size output, ranging from 12.4 MP (ILCE-1M2 S-crop) to 60.2 MP (ILCE-7RM5).

| Camera Body  | EXIF | FocusPt | Sharpness | Saliency | RAW Types | Dimensions |
|---|---|---|---|---|---|---|
| ILCE-1M2  |  ✅  |  ✅  |  ✅  |  ✅  | Compressed | 4320 × 2880 (12.4 MP, S), 5616 × 3744 (21.0 MP, M), 8640 × 5760 (49.8 MP, L) |
| ILCE-1   |  ✅  |  ✅  | ✅  | ✅  | Compressed | 8640 × 5760 (49.8 MP, L) |
| ILCE-7M5  |  ✅  |  ✅  |  ✅  |  ✅  | Compressed | 7008 × 4672 (32.7 MP, L) |
| ILCE-7RM5  |  ✅  |  ✅  |  ✅  |  ✅  | Compressed | 9504 × 6336 (60.2 MP, L) |
| ILCE-9M3 |  ✅  |  ✅  |  ✅  | ✅  | Compressed | 6000 × 4000 (24.0 MP, L) |

## Nikon NEF body compatibility

Nikon support targets current Z-series bodies. AF-point extraction uses the `AFInfo2` tag (0x00B7) with the `0300`+ layout common to Z9, Z8, Z7, and Z6 families; older DSLRs fall through and currently return `nil` for focus points while EXIF, thumbnail extraction, and sharpness scoring still work. Size-class thresholds for L/M/S are tuned per body (~45 MP for Z9/Z8/Z7/D850, ~24 MP for Z6).

### Key Features

RawCull has no editing capabilities — it is purpose-built for viewing, selecting, and copying photos.

- **High Performance:** Developed natively with Swift and SwiftUI, optimized for Apple Silicon-based Macs, utilizing only Apple's official Swift and SwiftUI frameworks, eliminating the need for third-party libraries
- **Small application:** The DMG file is about 3 MB in size
- **User-Friendly Interface:** Intuitive controls designed for efficient culling workflows
- **Privacy-First:** All data remains on your Mac, eliminating cloud synchronization and data collection
- **Security:** Digitally signed and notarized by Apple, it is also a sandboxed application, providing enhanced security
- **Free and Open Source:** Available under the MIT license
- **Non-Destructive:** It only reads ARW and NEF files, creating and storing thumbnails separately in the sandbox
- **Developed using official Apple Frameworks only:** latest Swift version, strict concurrency checking enabled, no third-party libraries which may break the app

The actual copy of RAW files from *source* to *destination* is non-destructive. It utilizes the default `/usr/bin/rsync` as part of macOS. Prior to the actual copy of files, a `--dry-run` parameter can be employed to simulate the files that will be copied to the destination.

<div class="alert alert-secondary" role="alert">

Both scanning and creating thumbnails, as well as extracting JPGs from ARW files, can be terminated using the shortcut `⌘K` or by the menu *Actions → Abort task*.

</div>

### Installation

RawCull is available for download on the [Apple App Store](https://apps.apple.com/no/app/rawcull/id6759362764?mt=12) or from the [GitHub Repository](https://github.com/rsyncOSX/RawCull/releases). 

> For security, please verify the SHA-256 hash after downloading if installed from GitHub. Current updates and release notes are available in the [changelog](/blog/releases/).
