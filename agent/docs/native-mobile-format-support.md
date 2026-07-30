# Native Mobile Apps — Next-Gen Format Support (Image + Video)

Sources:
- [Android Supported Media Formats](https://developer.android.com/media/platform/supported-formats)
- [Apple — WebP Support](https://developer.apple.com/documentation/uniformtypeidentifiers/uttype-swift.struct/webp)

---

## Key Point

Unlike browsers, native mobile apps do not send `Accept` headers. ImageKit cannot auto-detect format support — formats must be specified explicitly in the URL (`tr=f-webp` or `tr=f-avif`). This is the critical difference from web browser traffic where content negotiation handles format delivery automatically.

---

## Flutter

[Flutter docs](https://docs.flutter.dev/development/ui/assets-and-images)

| Format | Support | Notes |
|--------|---------|-------|
| WebP | ✅ Native | Including animated WebP |
| AVIF | ❌ Not supported | Not listed in Flutter native format support |

- `f-webp` is safe for all Flutter apps
- Do NOT recommend `f-avif` for Flutter — not natively supported by the framework
- Most Flutter apps load network images via `cached_network_image` or `Image.network()` — both rely on Flutter's native format support

---

## Android (native, non-Flutter)

Source: [Android Supported Media Formats — Images](https://developer.android.com/media/platform/supported-formats)

| Format | Native Support | Notes |
|--------|---------------|-------|
| WebP | Android 4.0+ | Lossless + transparency from Android 4.2.1+ |
| AVIF | Android 14+ | Baseline profile — both encode and decode mandatory from Android 14 |

**Third-party libraries** (extend support and add caching/async loading):
- [Glide](https://github.com/bumptech/glide) — image loading and caching
- [Coil](https://github.com/coil-kt/coil) — modern image loading for Kotlin

---

## iOS (native, non-Flutter)

| Format | Native Support | Notes |
|--------|---------------|-------|
| WebP | iOS 14+ | [Apple docs](https://developer.apple.com/documentation/uniformtypeidentifiers/uttype-swift.struct/webp) |
| AVIF | iOS 16+ | iOS 16 onwards |

**Darwin version mapping (from UA strings in analytics):**
- Darwin 23.x → iOS 17
- Darwin 24.x → iOS 18

**Third-party libraries** (extend support and add caching/async loading):
- [SDWebImage](https://github.com/SDWebImage/SDWebImage)
- [Kingfisher](https://github.com/onevcat/Kingfisher)

---

## How ImageKit Can Help

Once native support is confirmed (or third-party libraries are in place), use ImageKit's URL-based format transformation to serve the right format explicitly:

| Client | Recommend | Do NOT recommend | Reason |
|--------|-----------|-----------------|--------|
| Flutter | `tr=f-webp` | `tr=f-avif` | AVIF not natively supported in Flutter |
| Android native (OkHttp) | `tr=f-webp` | `tr=f-avif` unless Android 14+ min OS | AVIF only guaranteed on Android 14+ |
| iOS native (CFNetwork / URLSession) | `tr=f-webp` | `tr=f-avif` unless iOS 16+ min OS | AVIF only guaranteed on iOS 16+ |

Reference: [ImageKit URL-based format control](https://docs.imagekit.io/features/image-optimization/automatic-image-format-conversion#url-based-format-control)

**Note:** Do not flag absent `f-webp` as critical if the account's overall WebP delivery is already high — the customer has likely solved format delivery for web traffic. The native app gap is a recommendation only when native app UAs are significant in the traffic mix.

---

## Importance of Third-Party Libraries

Libraries like Glide and Coil (Android) and SDWebImage and Kingfisher (iOS) ensure consistent format support across OS versions older than the native thresholds above. They provide caching, async loading, and format compatibility that simplifies integration. When a customer's minimum supported OS is below the WebP or AVIF threshold, recommend these libraries alongside the explicit `tr=f-webp` URL param.

---

## Video — Container vs Codec Support

Sources:
- [Android Supported Media Formats](https://developer.android.com/media/platform/supported-formats)
- [Apple AVFileType docs](https://developer.apple.com/documentation/avfoundation/avfiletype)
- [flutter/flutter#25503](https://github.com/flutter/flutter/issues/25503)

### Key Point

ImageKit only ever delivers VP9 and AV1 wrapped in a **WebM container** — never MP4. There are two separate gates for native video playback, not one: does the chip support the codec, and does the OS media framework support the *container* at all. A device can have codec-capable hardware and still fail to play the file if its player can't open the container it's wrapped in.

### Android (native, non-Flutter) & Flutter-Android

Android apps typically use ExoPlayer (Jetpack Media3), not the stock `MediaPlayer`. WebM is a fully supported container on Android — no container-level blocker.

| Codec | Support | Notes |
|-------|---------|-------|
| H.264 (MP4) | All Android versions | Hardware decode on every device |
| VP9 (WebM) | Android 4.4+ | Effectively universal |
| AV1 (WebM) | Android 10+ | Hardware on newer chips, `libgav1` software fallback on older ones |

**Safe to force `f-webm` for Android native / Flutter-Android traffic.**

### iOS (native, non-Flutter) & Flutter-iOS

**Apple's AVPlayer does not support the WebM container at all** — confirmed against Apple's own AVFileType docs (WebM is not in the supported MIME list). Since ImageKit only ships VP9/AV1 in WebM, this means **VP9 and AV1 do not work on iOS via ImageKit, regardless of chip generation** — not just AV1 being gated to newer chips. The container blocks it before the codec/chip question is even reached.

| Codec | Chip support | Container support | Net result via ImageKit |
|-------|--------------|-------------------|--------------------------|
| H.264 (MP4) | All iPhones | Supported | ✅ Works |
| VP9 (WebM) | iPhone 7+ (A10) | **Not supported** | ❌ Does not work, any device |
| AV1 (WebM) | iPhone 15 Pro+ (A17 Pro) only | **Not supported** | ❌ Does not work, any device |

**Only `f-mp4` (H.264) is safe for iOS native / Flutter-iOS traffic. Never recommend `f-webm` or `vc-av1` for iOS.**

### How ImageKit Can Help — Video

| Client | Recommend | Do NOT recommend | Reason |
|--------|-----------|-------------------|--------|
| Android native (OkHttp) / Flutter-Android | `tr=f-webm` (VP9); `tr=f-auto` with codec group incl. `av1` for Android 10+ | — | WebM container fully supported |
| iOS native (CFNetwork/URLSession) / Flutter-iOS | `tr=f-mp4` (H.264) | `tr=f-webm`, `tr=vc-av1` | AVPlayer cannot open WebM at all, regardless of chip |

**Note:** For cross-platform native/Flutter apps, branch by platform when constructing the video URL (`Platform.isIOS`/`Platform.isAndroid` in Flutter, or the equivalent native check) — there is no single format setting safe on both platforms beyond H.264.
