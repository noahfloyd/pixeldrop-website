(() => {
  const story = document.querySelector(".story");
  const captions = [...document.querySelectorAll(".story-caption")];
  const frames = [...document.querySelectorAll(".story-frame")];
  const storyImages = frames.map((frame) => frame.querySelector("img")?.getAttribute("src")).filter(Boolean);
  const motionQuery = window.matchMedia("(min-width: 901px) and (prefers-reduced-motion: no-preference)");
  let scroller = null;
  let preloadStarted = false;

  const preloadFrames = () => {
    if (preloadStarted) return;
    preloadStarted = true;
    storyImages.forEach((source) => {
      const image = new Image();
      image.src = source;
    });
  };

  const setActive = (activeIndex) => {
    frames.forEach((frame, index) => {
      const isActive = index === activeIndex;
      frame.classList.toggle("is-active", isActive);
      frame.classList.toggle("is-past", index < activeIndex);
      frame.classList.toggle("is-future", index > activeIndex);
      frame.setAttribute("aria-hidden", String(!isActive));
    });
    captions.forEach((caption, index) => {
      const isActive = index === activeIndex;
      caption.classList.toggle("is-current", isActive);
      if (isActive) caption.setAttribute("aria-current", "step");
      else caption.removeAttribute("aria-current");
    });
    document.body.dataset.storyBeat = String(activeIndex + 1);
  };

  const disableStory = () => {
    if (scroller) {
      scroller.destroy();
      scroller = null;
    }
    document.body.classList.remove("story-enhanced");
    document.body.dataset.storyMode = "static";
    captions.forEach((caption) => {
      caption.classList.remove("is-current");
      caption.removeAttribute("aria-current");
    });
    frames.forEach((frame) => {
      frame.classList.remove("is-past", "is-future");
      frame.classList.add("is-active");
      frame.removeAttribute("aria-hidden");
    });
  };

  const enableStory = () => {
    if (!story || !captions.length || !frames.length || typeof window.scrollama !== "function") {
      disableStory();
      return;
    }
    document.body.classList.add("story-enhanced");
    document.body.dataset.storyMode = "sticky";
    setActive(0);
    scroller = window.scrollama();
    scroller
      .setup({ step: ".story-caption", offset: 0.55 })
      .onStepEnter(({ index }) => setActive(index));
  };

  const syncMode = () => {
    if (motionQuery.matches) enableStory();
    else disableStory();
  };

  if (story && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        preloadFrames();
        observer.disconnect();
      }
    }, { rootMargin: "700px 0px" });
    observer.observe(story);
  } else {
    preloadFrames();
  }

  syncMode();
  motionQuery.addEventListener("change", syncMode);
  window.addEventListener("resize", () => scroller?.resize());
})();
