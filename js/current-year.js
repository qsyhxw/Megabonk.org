(() => {
    const currentYear = String(new Date().getFullYear());
    const titleSelector = 'h1, h2, h3, .logo, .hero-title, .page-title, .database-title, .section-title';
    const emojiPattern = /\p{Extended_Pictographic}/u;
    const styleId = 'leading-emoji-fix-styles';

    const updateYears = (root = document) => {
        if (root.nodeType === Node.ELEMENT_NODE && root.matches?.('[data-current-year]')) {
            root.textContent = currentYear;
        }
        root.querySelectorAll?.('[data-current-year]').forEach((element) => {
            element.textContent = currentYear;
        });
    };

    const installEmojiStyle = () => {
        if (document.getElementById(styleId)) return;
        const style = document.createElement('style');
        style.id = styleId;
        style.textContent =             '.leading-emoji-icon{' +
            'display:inline-block;' +
            'background:none!important;' +
            '-webkit-background-clip:border-box!important;' +
            'background-clip:border-box!important;' +
            '-webkit-text-fill-color:initial!important;' +
            'color:initial!important;' +
            'font-family:"Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif!important;' +
            'font-style:normal;' +
            '}';
        document.head.appendChild(style);
    };

    const firstVisibleTextNode = (element) => {
        const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
        let node;
        while ((node = walker.nextNode())) {
            if (node.nodeValue.trim()) return node;
        }
        return null;
    };

    const wrapLeadingEmoji = (element) => {
        if (element.dataset.emojiHeadingFixed === 'true') return;
        const textNode = firstVisibleTextNode(element);
        if (!textNode) return;

        const raw = textNode.nodeValue;
        const whitespaceLength = raw.length - raw.trimStart().length;
        const content = raw.slice(whitespaceLength);
        const firstGrapheme = globalThis.Intl?.Segmenter
            ? [...new Intl.Segmenter(undefined, { granularity: 'grapheme' }).segment(content)][0]?.segment
            : Array.from(content)[0];

        if (!firstGrapheme || !emojiPattern.test(firstGrapheme)) return;

        const parent = textNode.parentNode;
        const before = document.createTextNode(raw.slice(0, whitespaceLength));
        const icon = document.createElement('span');
        icon.className = 'leading-emoji-icon';
        icon.setAttribute('aria-hidden', 'true');
        icon.textContent = firstGrapheme;
        const after = document.createTextNode(content.slice(firstGrapheme.length));

        parent.replaceChild(after, textNode);
        parent.insertBefore(icon, after);
        parent.insertBefore(before, icon);
        element.dataset.emojiHeadingFixed = 'true';
    };

    const fixEmojiHeadings = (root = document) => {
        const candidates = [];
        if (root.nodeType === Node.ELEMENT_NODE && root.matches?.(titleSelector)) candidates.push(root);
        root.querySelectorAll?.(titleSelector).forEach((element) => candidates.push(element));
        candidates.forEach(wrapLeadingEmoji);
    };

    installEmojiStyle();
    updateYears();
    fixEmojiHeadings();

    if (document.body) {
        new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType !== Node.ELEMENT_NODE) return;
                    updateYears(node);
                    fixEmojiHeadings(node);
                });
            });
        }).observe(document.body, { childList: true, subtree: true });
    }
})();
