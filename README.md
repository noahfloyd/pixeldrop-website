# Pixeldrop website

Production static site for [www.pixeldrop.space](https://www.pixeldrop.space/).

## Serve locally

```sh
python3 -m http.server 4173 --bind 127.0.0.1
```

Open `http://127.0.0.1:4173/`.

No build is required. Fonts, images, and JavaScript are local. There are no analytics or third-party runtime requests.

## Real app captures

The six stable files under `assets/story/` are untouched 1206×2622 iPhone 17 Pro Simulator captures from the Pixeldrop app:

- `beat-1-knock.png`
- `beat-2-cover.png`
- `beat-3-grid.png`
- `beat-4-post.png`
- `beat-5-reply.png`
- `beat-6-done.png`

All six story frames are accepted. The Phase B host-proof pass also accepted `assets/people/messages.png`. The four refreshed captures are:

- `beat-1-knock.png`: one real native iOS Notification Center notification from the rebuilt app, showing the installed app's genuine updated pixel-orb icon.
- `beat-4-post.png`: fictional Ava Sol's deterministic second post, whose portrait blue-vase image matches its caption.
- `beat-5-reply.png`: the same Ava post expanded to show all three deterministic shared comments, `Private reply` selected, `Shared comment` unselected, and the composer without a keyboard.
- `assets/people/messages.png`: the real top-of-inbox Messages state used for the large CSS-only top-half crop.

`verify.py` pins the accepted SHA-256 digest for every capture and rejects all four retired stale digests. `index.html` marks each refreshed use as `data-capture-status="accepted"`.

All visible people, avatars, photos, comments, and conversation copy are deterministic fictional seed data. The accepted Ava and Comments frames visibly retain the source-owned fixture handles `@ava_seed`, `@mira_seed`, `@jules_seed`, and `@sana_seed`. The capture manifest simultaneously required those exact identities and said no seed words; Phase B records that contradiction explicitly. It is accepted as a bounded presentation caveat because the handles identify repository-owned fictional fixtures, expose no personal or viewer data, and do not represent proof, smoke, or developer state. The relationship cards reuse untouched real screenshots through CSS-only crops: the private-reply card focuses the lower response controls from `beat-5-reply.png`, while the Messages card shows a readable top-half slice of `assets/people/messages.png`.

The ending frame truthfully shows the current dark Done matte. The accepted notification is a real native iOS notification delivered with `simctl push`; its icon comes from the rebuilt installed app, without compositing or retouching.

`verify.py` requires all seven stable local paths, exact dimensions, exact accepted hashes, explicit accepted-state markup for the refreshed capture uses, retired-hash rejection, descriptive alt contracts, and the reviewed CSS crop hooks.

The hero uses the stable Pixeldrop orb plus three lightweight WebP derivatives of repository-owned fictional seed imagery under `assets/hero/`. It contains no generated phone UI and makes no network request.

On desktop with JavaScript and motion enabled, the story uses a sticky phone frame and scrollama-driven crossfades. Mobile, reduced-motion, and no-JavaScript presentations render the full six-frame inline sequence with captions.

## Vendored dependency

`assets/vendor/scrollama.min.js` is Scrollama 3.2.0, vendored locally. Its license is retained at `assets/vendor/scrollama-LICENSE.txt`.
