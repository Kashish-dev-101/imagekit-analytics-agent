# Native Mobile Apps — Next-Gen Image Format Support

Sources:
- https://imagekit.notion.site/Native-Mobile-apps-Next-Gen-Image-Format-support-22f6464239f34faab74da32cb841e2b7
- https://docs.flutter.dev/development/ui/assets-and-images

---

## Key Point

Unlike browsers, native mobile apps do not send `Accept` headers. ImageKit cannot auto-detect format support — formats must be specified explicitly in the URL (`tr=f-webp` or `tr=f-avif`).

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

| Format | Native Support | Notes |
|--------|---------------|-------|
| WebP | Android 4.0+ | Very broad coverage |
| AVIF | Android 14+ | Newer devices only |

**Third-party libraries:**
- [Glide](https://github.com/bumptech/glide) — image loading and caching
- [Coil](https://github.com/coil-kt/coil) — modern image loading

---

## iOS (native, non-Flutter)

| Format | Native Support | Notes |
|--------|---------------|-------|
| WebP | iOS 14+ | [Apple docs](https://developer.apple.com/documentation/uniformtypeidentifiers/uttype-swift.struct/webp) |
| AVIF | iOS 16+ | iOS 16 onwards |

**Darwin version mapping (from UA strings in analytics):**
- Darwin 23.x → iOS 17
- Darwin 24.x → iOS 18

**Third-party libraries:**
- [SDWebImage](https://github.com/SDWebImage/SDWebImage)
- [Kingfisher](https://github.com/onevcat/Kingfisher)

---

## ImageKit Fix

| Client | Safe format | Notes |
|--------|-------------|-------|
| Flutter | `tr=f-webp` | AVIF not supported in Flutter |
| Android native | `tr=f-webp` | Safe for Android 4.0+. `tr=f-avif` only if Android 14+ minimum |
| iOS native | `tr=f-webp` | Safe for iOS 14+. `tr=f-avif` only if iOS 16+ minimum |

Reference: https://docs.imagekit.io/features/image-optimization/automatic-image-format-conversion#url-based-format-control
