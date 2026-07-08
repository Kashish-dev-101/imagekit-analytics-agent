# Native Mobile Apps — Next-Gen Image Format Support

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
