# Pixeldrop website

Production static site for [www.pixeldrop.space](https://www.pixeldrop.space/).

## Serve locally

```sh
python3 -m http.server 4173 --bind 127.0.0.1
```

Open `http://127.0.0.1:4173/`.

No build is required. Fonts, images, and JavaScript are local. There are no analytics or third-party runtime requests.

## Real app captures

The six files under `assets/story/` are accepted, untouched 1206×2622 iPhone 17 Pro Simulator captures from the current Pixeldrop app:

- `beat-1-knock.png`
- `beat-2-cover.png`
- `beat-3-grid.png`
- `beat-4-post.png`
- `beat-5-reply.png`
- `beat-6-done.png`

The Messages card uses the accepted real inbox capture at `assets/people/messages.png`, also at 1206×2622. All visible people, avatars, photos, and conversation copy are deterministic fictional seed data.

The opening and ending frames truthfully show the current dark Begin and Done mattes. The notification frame is a real native iOS lock-screen notification delivered with `simctl push`; its small icon is the current development app icon, retained without compositing or retouching.

`verify.py` requires all seven stable local paths, exact dimensions, hashes distinct from the retired temporary frames, and truthful image descriptions.

On desktop with JavaScript and motion enabled, the story uses a sticky phone frame and scrollama-driven crossfades. Mobile, reduced-motion, and no-JavaScript presentations render the full six-frame inline sequence with captions.

## Vendored dependency

`assets/vendor/scrollama.min.js` is Scrollama 3.2.0, vendored locally. Its license is retained at `assets/vendor/scrollama-LICENSE.txt`.
