//This script prevents Discord from detecting when the user switches windows/tabs,
//allowing video quests to continue playing in the background without being paused.
(function() {
    console.log('[QuestBot] Applying video quest bypass (fixed)...');
    Object.defineProperty(document, 'hidden', {
        get: () => false,
        configurable: true
    });
    
    Object.defineProperty(document, 'visibilityState', {
        get: () => 'visible',
        configurable: true
    });
    document.hasFocus = () => true;
    const blockedEvents = ['visibilitychange', 'blur', 'pagehide']; 
    blockedEvents.forEach(event => {
        window.addEventListener(event, (e) => {
            e.stopImmediatePropagation();
        }, true);
        
        document.addEventListener(event, (e) => {
            e.stopImmediatePropagation();
        }, true);
    });
    const OriginalIntersectionObserver = window.IntersectionObserver;
    window.IntersectionObserver = class extends OriginalIntersectionObserver {
        constructor(callback, options) {
            super((entries, observer) => {
                entries = entries.map(entry => ({
                    ...entry,
                    isIntersecting: true,
                    intersectionRatio: 1.0,
                    intersectionRect: entry.boundingClientRect,
                }));
                callback(entries, observer);
            }, options);
            console.log('[QuestBot] IntersectionObserver intercepted');
        }
    };
    const originalRAF = window.requestAnimationFrame;
    window.requestAnimationFrame = function(callback) {
        return originalRAF(function(time) {
            try {
                return callback(time);
            } catch(e) {
                console.error('[QuestBot] RAF error:', e);
            }
        });
    };
      const originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;
    Element.prototype.getBoundingClientRect = function() {
        const rect = originalGetBoundingClientRect.call(this);
        if (this.tagName === 'VIDEO' || this.tagName === 'IFRAME') {
            return {
                ...rect,
                top: 100,
                left: 100,
                bottom: rect.height + 100,
                right: rect.width + 100,
                x: 100,
                y: 100,
                width: rect.width || 1920,
                height: rect.height || 1080
            };
        }
        return rect;
    };
    const originalPause = HTMLMediaElement.prototype.pause;
    HTMLMediaElement.prototype.pause = function() {
        console.log('[QuestBot] Blocked video pause attempt');
        return;
    };
    setInterval(() => {
        document.querySelectorAll('video').forEach(video => {
            if (video.paused && !video.ended) {
                console.log('[QuestBot] Auto-resuming paused video');
                video.play().catch(() => {});
            }
        });
    }, 100);
    
    console.log('[QuestBot] ✓ Video bypass active');
})();
